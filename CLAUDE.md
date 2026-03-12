# Claude Code Plugin Repository

이 repo는 Claude Code 플러그인 마켓플레이스입니다. 플러그인을 추가하거나 수정할 때 이 가이드를 따릅니다.

## 버전 정책 (Semantic Versioning)

모든 플러그인은 `MAJOR.MINOR.PATCH` 버전을 사용합니다.

| 변경 유형 | 버전 | 예시 |
|-----------|------|------|
| 기존 구조 호환 깨짐 | **MAJOR** 올림 | 필수 섹션 삭제, 체크리스트 구조 변경 |
| 새 기능/섹션 추가 (하위 호환) | **MINOR** 올림 | 조건부 섹션 추가, 새 에이전트 추가 |
| 버그 수정, 배점 조정, 문구 개선 | **PATCH** 올림 | 오타 수정, 배점 미세 조정 |

### 버전 반영 위치

플러그인 수정 시 **반드시** 아래 파일들의 버전을 동기화합니다:

1. `.claude-plugin/plugin.json` → `"version"` 필드
2. `skills/{name}/contract.json` → `"version"` 필드
3. 루트 `.claude-plugin/marketplace.json` → 해당 플러그인의 `"version"` 필드
4. 루트 `README.md` → 플러그인 목록 테이블의 버전

### 변경 이력

체크리스트 파일에 변경 이력 섹션이 있으면 새 버전을 추가합니다.

## 플러그인 구조 규칙

```
plugins/{name}/
├── .claude-plugin/
│   └── plugin.json           # 매니페스트 (name, version, agents, skills)
├── agents/
│   └── {agent-name}.md       # 에이전트 정의 (frontmatter + 본문)
└── skills/{name}/
    ├── SKILL.md               # 스킬 진입점 (frontmatter 필수)
    ├── CLAUDE.md              # 플러그인 내부 규칙
    ├── contract.json          # 단일 기준 (구조/정책/품질 규칙)
    ├── specs/                 # 문서/Spec 정의
    ├── templates/             # 출력 템플릿
    └── checklists/            # 평가 체크리스트
```

### 핵심 원칙

- **contract.json이 단일 기준**: 다른 파일과 충돌 시 contract.json을 따름
- **에이전트는 역할 분리**: orchestrator는 조율만, writer는 작성만, reviewer는 평가만
- **직접 작성 금지**: orchestrator/reviewer가 본문을 직접 쓰거나 고치지 않음

## 에이전트 정의 규칙

```markdown
---
name: {agent-name}
description: {한 줄 설명}
tools: {사용 도구 목록}
model: opus                    # 선택: 고품질 필요 시
color: {색상}                  # 선택: UI 구분용
---

{에이전트 본문}
```

- `tools`는 최소 권한 원칙 — 필요한 도구만 선언
- reviewer는 `Read, Grep`만 허용 (수정 방지)

## SKILL.md 규칙

```markdown
---
name: {skill-name}
description: {한 줄 설명 — 트리거 키워드 포함}
allowed-tools: {도구 목록}
---

{스킬 본문}
```

- `description`에 트리거 키워드를 포함해야 자연어 요청 시 자동 매칭됨

## 수정 시 체크리스트

플러그인을 수정할 때 반드시 확인:

- [ ] contract.json 변경 시 관련 specs/templates/checklists/agents 동기화
- [ ] 버전 올림 (4곳: plugin.json, contract.json, marketplace.json, README.md)
- [ ] 배점 변경 시 총점 100점 유지 확인
- [ ] 새 체크리스트 항목 추가 시 ID 충돌 없는지 확인
- [ ] 조건부 섹션 추가 시 orchestrator에 확인 워크플로우 추가
- [ ] 커밋 메시지에 `feat/fix/docs` prefix + 플러그인 scope 사용

## 커밋 메시지 규칙

```
{type}({plugin-name}): {설명}

{상세 변경 내용}

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

| type | 용도 |
|------|------|
| `feat` | 새 기능, 새 섹션, 새 에이전트 |
| `fix` | 버그 수정, 배점 오류 수정 |
| `docs` | README, CLAUDE.md 등 문서 수정 |
| `refactor` | 구조 변경 (동작 변화 없음) |

## 플러그인 간 관계

```
doc-writing-team  →  HLD / LLD 작성
       ↓
spec-from-design  →  HLD/LLD → Spec 도출
       ↓
spec-harness      →  Spec → 코드 생성 + 결정성 검증

md-to-confluence  →  Confluence 발행 (독립 사용 가능)
```

- `md-to-confluence`는 파이프라인과 무관하게 **임의의 MD 파일**을 Confluence에 발행할 수 있는 독립 플러그인입니다.
- 파이프라인 내에서는 doc-writing-team / spec-from-design 산출물 발행에 활용되지만, 어떤 Markdown 파일이든 단독으로 사용 가능합니다.

수정 시 상류/하류 플러그인에 영향이 있는지 확인합니다:
- HLD/LLD 구조 변경 → spec-from-design의 mappings 확인
- Spec 구조 변경 → spec-harness의 regen-procedure 확인
