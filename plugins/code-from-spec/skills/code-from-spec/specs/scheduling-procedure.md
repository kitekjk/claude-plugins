# 스케줄링 절차

## 목적

Spec 파일들의 의존성을 분석하고, Jira 티켓 생성 + Git worktree 구성 + 실행 순서 결정을 수행합니다.

## 사전 조건

- Spec 디렉토리가 존재하고 1개 이상의 Spec 파일이 있어야 합니다.
- Git 저장소가 초기화되어 있어야 합니다.
- Jira MCP 서버가 연결되어 있어야 합니다.

## Phase 1: Spec 수집

1. `{spec_dir}` 하위의 모든 `.md` 파일을 수집합니다.
2. 파일 유형별로 분류합니다:
   - 구현 Spec (기본 정보의 type: usecase, model, service, refactoring, performance)
   - Policy Spec (`POLICY-*`)
   - 기초 문서 (`service-definition`, `architecture-rules`, `naming-guide`, `infra-config`)
3. 기초 문서와 Policy Spec은 스케줄링 대상에서 제외합니다 (항상 최우선 적용).

## Phase 2: 의존성 분석

1. 각 Spec 파일에서 `dependsOn` 메타데이터를 파싱합니다.

```yaml
# Spec 파일 내 메타데이터 형식 (기본 정보 테이블 또는 dependsOn 섹션)
dependsOn:
  - spec_id: PLM-STYLE-001
    shared_files: ["StyleEntity.java", "StyleRepository.java"]
    reason: "스타일 엔티티를 참조하여 PO 취소 처리"
```

2. 의존성 그래프를 구성합니다.
3. 순환 의존성을 감지합니다.

**순환 의존성 발견 시:**
- 관련 Spec 목록과 순환 경로를 사용자에게 보고합니다.
- 사용자가 의존성을 수정할 때까지 진행하지 않습니다.

## Phase 3: 위상 정렬

1. 의존성 그래프를 위상 정렬합니다.
2. 실행 Level을 결정합니다:

```text
Level 0: [PLM-POCANCEL-001, PLM-STYLE-001]    # 의존성 없음 → 병렬
Level 1: [PLM-BOM-001]                        # Level 0에만 의존 → 병렬
Level 2: [PLM-ORDER-001]                      # Level 0, 1에 의존 → 순차
```

3. 같은 Level 내 Spec 수가 `maxParallel`을 초과하면 배치로 나눕니다.

## Phase 4: Jira 티켓 생성

각 Spec에 대해:

1. 기존 구현 추적 섹션의 `jiraTicket` 필드를 확인합니다.
2. 이미 티켓이 있으면 건너뜁니다.
3. 새 티켓을 생성합니다:

```
POST /rest/api/2/issue
{
  "fields": {
    "project": { "key": "{jira_project}" },
    "summary": "[Spec] {spec_id}: {spec_title}",
    "issuetype": { "name": "Task" },
    "description": "Spec 기반 구현 작업\n\nSpec 파일: {spec_file}\n실행 Level: {level}\n의존성: {dependencies}",
    "labels": ["spec-impl", "auto-generated", "level-{n}"]
  }
}
```

4. 의존 관계가 있는 티켓 간 이슈 링크를 생성합니다 (`blocks` 관계).

## Phase 5: Git worktree 구성

각 Spec에 대해:

1. 기존 worktree를 확인합니다 (`git worktree list`).
2. 이미 존재하면 재사용합니다.
3. 새 worktree를 생성합니다:

```bash
git branch {jira_key}-{spec_id_kebab} main
git worktree add {worktree_base}/{jira_key}-{spec_id_kebab} {jira_key}-{spec_id_kebab}
```

## Phase 6: 구현 추적 섹션 초기화

각 Spec 파일 하단에 구현 추적 섹션을 추가합니다:

```markdown
## 구현 추적

```yaml
status: not-started
jiraTicket: PROJ-123
branch: PROJ-123-plm-pocancel-001
pr: ""
commit: ""
completedAt: ""
`` `
```

- 이미 구현 추적 섹션이 존재하면 누락 필드만 추가합니다.
- 기존 값은 덮어쓰지 않습니다.

## Phase 7: 작업 계획서 출력

`reports/work-plan-{date}.md` 파일에 전체 계획을 기록합니다.

포함 내용:
- Spec 목록 + 실행 Level
- 의존성 그래프 (Mermaid)
- Jira 티켓 매핑 테이블
- worktree 경로 매핑 테이블
- 예상 실행 순서

## 후속 동작

스케줄링 완료 후:
- `implement` 워크플로우가 실행 Level 순서대로 각 worktree에서 구현을 시작합니다.
- 각 Spec 구현 완료 시 구현 추적 섹션의 `status`를 `completed`로 업데이트합니다.
- `verify` 워크플로우 완료 시 `verified`로 업데이트합니다.
- PR 생성 시 `pr` 필드를 업데이트합니다.
