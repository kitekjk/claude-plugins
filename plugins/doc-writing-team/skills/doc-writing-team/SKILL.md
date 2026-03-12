---
name: doc-writing-team
description: ADR, HLD, LLD 문서를 멀티 에이전트 품질 루프로 작성합니다. 범용 설계 문서 작성 요청에서 사용하세요.
allowed-tools: Read, Write, Edit, Grep, Glob, Task, Bash
---

# doc-writing-team

## 목적

`doc-writing-team`은 `ADR`, `HLD`, `LLD`를 일관된 구조와 스타일로 생성하고, `88점` 품질 게이트와 피드백 학습 루프를 적용하는 문서 작성 스킬입니다.

**v3.0 핵심 변경**: HLD/LLD에서 하류 Spec(Use Case, API, 정책, 테스트)을 도출할 수 있는 수준의 상세도를 보장합니다.

## 단일 기준

모든 구조/저장/품질/스키마 규칙의 기준은 `contract.json`입니다.

- `contract.json`
- `memory/style_guide.md`
- `specs/{type}.md`
- `templates/{type}.md`
- `checklists/common-checklist.md`
- `checklists/{type}-checklist.md`

충돌이 생기면 `contract.json`을 먼저 맞추고 관련 파일을 동기화합니다.

## 서브에이전트 구조

```text
doc-orchestrator
├── adr-writer
├── hld-writer
├── lld-writer
├── content-reviewer
├── style-learner
└── style-analyzer
```

## 문서 타입 판별

| 키워드 | 타입 | 담당 |
|--------|------|------|
| `ADR`, `의사결정`, `선택`, `비교` | `ADR` | `adr-writer` |
| `HLD`, `고수준 설계`, `시스템 설계`, `아키텍처` | `HLD` | `hld-writer` |
| `LLD`, `상세 설계`, `구현 설계` | `LLD` | `lld-writer` |

## 워크플로우

1. `doc-orchestrator`가 문서 타입을 판별합니다.
2. writer가 `persona -> style -> spec -> template` 순서로 초안을 만듭니다.
3. `content-reviewer`가 체크리스트 기준으로 평가합니다.
   - **기존 항목**: 스타일, 구조, 명확성, 옵션 비교, 제약조건, 금지표현
   - **추가 항목**: Spec 도출 가능성 (HLD: H-20~H-22, LLD: L-20~L-23)
4. 총점 `88점` 미만이면 수정 후 재평가합니다.
5. 통과한 초안은 사용자에게 제시됩니다.
6. 사용자 피드백은 revision 또는 style-learning 경로로 분기됩니다.

## 고정 정책

- 저장 구조는 `documents/{type}/{slug}/DOCUMENT.md`
- `ADR`의 Decision은 작성자가 임의 확정하지 않음
- `HLD`, `LLD`는 `Appendix` 선택 허용
- 공통 체크리스트는 `ADR`, `HLD`, `LLD` 모두에 적용
- 승인 코퍼스는 스타일 참고용이며 구조 계약을 덮어쓰지 않음

## v3.0 강화 사항

### HLD 강화
- **State Transition Model** 조건부 필수 (상태 기반 도메인)
- **KDD에 대안 비교 필수** (정책 Spec 도출을 위해)
- **컴포넌트 테이블에 기술 스택 필수** (아키텍처 규칙 도출을 위해)

### LLD 강화
- **Proposed Design 하위 구조화**:
  - API 설계 (엔드포인트+요청/응답+에러 코드)
  - 클래스/컴포넌트 설계 (클래스+메서드 시그니처)
  - DB 스키마 (테이블+컬럼+인덱스+DDL)
  - 설계 판단 근거 (채택/탈락 비교+감수하는 단점)
- **미해결 리스크 필수** (리스크+영향도+완화 방안)
- **FR 검증 기준 필수** (테스트 시나리오 도출을 위해)

### Spec 도출 매핑

| HLD 섹션 | 도출 가능한 Spec |
|----------|----------------|
| KDD | 정책 Spec (비즈니스 규칙) |
| NFR | NFR 정책 (성능/가용성 목표) |
| State Transition | 상태 전이 정책 |
| 컴포넌트 역할 | 아키텍처 규칙 |

| LLD 섹션 | 도출 가능한 Spec |
|----------|----------------|
| FR + 클래스 설계 | Use Case Spec |
| API 설계 | API Spec |
| 설계 판단 근거 | 정책 Spec |
| FR 검증 기준 + 미해결 리스크 | 테스트 시나리오 |

## 피드백 학습

- 피드백은 `memory/feedback_log.jsonl`에 기록합니다.
- `style-learner`는 피드백을 `common|adr|hld|lld|both`로 분류합니다.
- `style-analyzer`는 승인 범위에 따라 스타일 가이드, 스펙, 템플릿, 체크리스트를 업데이트합니다.
