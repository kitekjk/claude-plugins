# 스케줄링 절차

## 목적

Spec 파일들의 의존성을 분석하고, Jira 티켓 생성 + Git worktree 구성 + 실행 순서 결정을 수행합니다.

## 사전 조건

- Spec 디렉토리가 존재하고 1개 이상의 Spec 파일이 있어야 합니다.
- Git 저장소가 초기화되어 있어야 합니다.
- Jira MCP 서버가 연결되어 있어야 합니다 (불가 시 Jira 없이 진행 가능).

## Phase 1: Spec 수집 및 상태 필터링

1. `{spec_dir}` 하위의 모든 `.md` 파일을 수집합니다.
2. 파일 유형별로 분류합니다:
   - 구현 Spec (기본 정보의 type: usecase, model, service, refactoring, performance, simplification)
   - Policy Spec (`POLICY-*`)
   - 기초 문서 (`service-definition`, `architecture-rules`, `naming-guide`, `infra-config`)
3. 기초 문서와 Policy Spec은 스케줄링 대상에서 제외합니다 (항상 최우선 적용).
4. 각 구현 Spec의 `## 구현 추적` 섹션에서 `status` 필드를 확인합니다.
5. 다음 상태의 Spec은 스케줄링 대상에서 **제외**합니다:
   - `completed`: 구현 완료
   - `review-approved`: 리뷰 승인 완료
   - `verified`: 검증 완료
6. 다음 상태의 Spec은 스케줄링 대상에 **포함**합니다:
   - `not-started`: 미시작
   - `in-progress`: 진행 중 (재시도/중단 복구 대상)
   - `review-pending`: 리뷰 대기 (재스케줄링 가능)
   - (status 없음): 구현 추적 섹션이 없는 신규 Spec
7. 제외된 Spec 수와 목록을 작업 계획서에 기록합니다.

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

**순서 오류 발견 시:** 중단하고, 오류 원인(존재하지 않는 브랜치명, 순환 의존성 등)을 구체적으로 보고한다.

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

**Jira MCP 불가 시 대체 동작:**

1. Jira MCP 연결을 시도합니다.
2. 연결 실패 시 `[WARN] Jira MCP 연결 불가 — Jira 없이 진행` 로그를 출력합니다.
3. 구현 추적 섹션의 `jiraTicket` 필드는 빈 값으로 유지합니다.
4. 브랜치명은 `{spec_id_kebab}` 형식으로 대체합니다 (Jira 키 없이).
5. 나머지 Phase (worktree, 작업 계획서)는 정상 진행합니다.

## Phase 5: Git worktree 구성

각 Spec에 대해:

1. 기존 worktree를 확인합니다 (`git worktree list`).
2. 이미 존재하면 재사용합니다.
3. 새 worktree를 생성합니다. **base 브랜치는 의존성 여부에 따라 결정합니다.**

**base 브랜치 결정 규칙:**

| 조건 | base 브랜치 |
|------|------------|
| `dependsOn: []` (Level 0) | `main` |
| 의존 Spec이 1개 | 해당 선행 Spec의 브랜치 |
| 의존 Spec이 여럿 | `shared_files` 겹침이 가장 많은 선행 Spec의 브랜치. 동률인 경우 Spec ID의 알파벳 순서가 빠른 Spec의 브랜치를 base로 선택한다. 사용자 확인은 3개 이상 동률인 경우에만 요청한다. |

```bash
# Level 0 (의존성 없음)
git branch {jira_key}-{spec_id_kebab} main
git worktree add {worktree_base}/{jira_key}-{spec_id_kebab} {jira_key}-{spec_id_kebab}

# Level 1+ (의존성 있음) — 선행 Spec 브랜치에서 분기
BASE_BRANCH={선행-spec의-branch명}   # 구현 추적 섹션의 branch 필드에서 읽음
git branch {jira_key}-{spec_id_kebab} ${BASE_BRANCH}
git worktree add {worktree_base}/{jira_key}-{spec_id_kebab} {jira_key}-{spec_id_kebab}
```

**선행 Spec 브랜치명 조회:** 선행 Spec 파일의 `## 구현 추적` 섹션 → `branch` 필드에서 읽습니다.

## Phase 6: 실행 모드 결정

`contract.json`의 `execution.default` 또는 사용자 요청에서 실행 모드를 결정합니다.

| 판별 | 모드 |
|------|------|
| 사용자 요청에 '리뷰 포함', 'review-gate', '리뷰 게이트' 포함 | `review-gate` |
| 사용자 요청에 '자동', 'auto', '전자동' 포함 | `auto` |
| 명시 없음 | `contract.json`의 `execution.default` |

**review-gate 모드 추가 분석:**

Level별로 `shared_files` 겹침 맵을 생성합니다.

```text
Level N의 Spec A의 shared_files ∩ Level N+1의 Spec B의 shared_files → 겹침 여부
```

- 겹침이 없는 Level N+1 Spec → `lookahead` 대상으로 표시
- 겹침이 있는 Level N+1 Spec → 리뷰 완료 후 구현

## Phase 7: 구현 추적 섹션 초기화

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
reviewedAt: ""
`` `
```

- 이미 구현 추적 섹션이 존재하면 누락 필드만 추가합니다.
- 기존 값은 덮어쓰지 않습니다.

## Phase 8: 작업 계획서 출력

`reports/work-plan-{date}.md` 파일에 전체 계획을 기록합니다.

포함 내용:
- 실행 모드 (auto / review-gate)
- Spec 목록 + 실행 Level
- 의존성 그래프 (Mermaid)
- Jira 티켓 매핑 테이블
- worktree 경로 매핑 테이블
- 예상 실행 순서
- (review-gate 모드) 리뷰 체크포인트 목록 + lookahead 대상 Spec 표시

**review-gate 모드 작업 계획서 추가 섹션:**

```markdown
## 리뷰 체크포인트

| 체크포인트 | Level | 리뷰 대상 Spec | Lookahead 가능 Spec |
|-----------|-------|--------------|-------------------|
| CP-0 | Level 0 완료 후 | {spec_list} | {lookahead_list} |
| CP-1 | Level 1 완료 후 | {spec_list} | {lookahead_list} |
...
```

## 후속 동작

스케줄링 완료 후:

**auto 모드:**
- `implement` 워크플로우가 실행 Level 순서대로 각 worktree에서 구현을 시작합니다.

**review-gate 모드:**
- Level 0 구현 시작
- Level 0 완료 → `review-pending` 상태 + Jira `In Review` + 리뷰 요청 메시지 출력 + 대기
- 사용자 승인 → `review-approved` 상태 + Level 1 진행
- 반복

**공통:**
- Spec 구현 완료 시 구현 추적 섹션의 `status`를 `completed`로 업데이트합니다.
- `verify` 워크플로우 완료 시 `verified`로 업데이트합니다.
- PR 생성 시 `pr` 필드를 업데이트합니다.

## Worktree 정리

PR이 머지된 후 worktree를 정리합니다:

1. `git worktree list`로 활성 worktree를 확인합니다.
2. 해당 Spec의 구현 추적 `status`가 `verified`이고 PR이 머지된 경우:
   ```bash
   git worktree remove {worktree_path}
   git branch -d {branch_name}
   ```
3. 정리는 다음 `schedule` 또는 `full` 워크플로우 실행 시 자동으로 수행합니다.
4. 사용자가 명시적으로 "worktree 정리" 요청 시에도 수행합니다.
