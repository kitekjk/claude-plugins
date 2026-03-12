# doc-writing-team 플러그인

이 플러그인의 구조와 정책은 `contract.json`이 기준입니다. 다른 문서와 예시가 충돌하면 항상 `contract.json`을 따릅니다.

## 우선순위

1. `contract.json`
2. `memory/style_guide.md`, `specs/*.md`, `checklists/*.md`, `templates/*.md`
3. `memory/approved_corpus/`

`approved_corpus`는 톤과 예시 참고용이며 구조, 저장 경로, 정책을 바꾸지 않습니다.

## 핵심 계약

- 저장 경로: `documents/{type}/{slug}/DOCUMENT.md`
- 선택 경로: `documents/{type}/{slug}/REVIEW.md`, `documents/{type}/{slug}/assets/`
- 루트 직접 `.md` 생성 금지
- 통과 점수: `88`
- 품질 루프: 최대 `5회`
- 사용자 수정 루프: 승인될 때까지 반복

## 문서 타입별 규칙

### ADR

- Writer: `adr-writer`
- 필수 섹션: `Context`, `Agenda`, `Decision`, `Next Step`
- Appendix 불가
- `Decision`은 사용자 확인값 또는 `[TBD]`만 허용

### HLD

- Writer: `hld-writer`
- 필수 섹션: `Glossary`, `Overview`, `System Context`, `High-Level Architecture`, `Key Design Decisions`, `Non-Functional Requirements`
- 조건부 필수: `State Transition Model` (상태 기반 도메인)
- 선택 섹션: `Deployment Overview`, `Appendix`
- Appendix 허용
- Spec 도출 가능성 평가: H-20~H-22

### LLD

- Writer: `lld-writer`
- 필수 섹션: `Glossary`, `Problem Statement`, `Functional Requirements`, `Non-Functional Requirements`, `Goal / Non-Goal`, `Proposed Design`
- Proposed Design 필수 하위 섹션: `API 설계`, `클래스/컴포넌트 설계`, `DB 스키마`, `설계 판단 근거`
- 선택 섹션: `Appendix`
- Appendix 허용
- Spec 도출 가능성 평가: L-20~L-23

## 참조 파일

- Persona: `memory/personas/staff-engineer.md`
- 스타일: `memory/style_guide.md`
- 스펙: `specs/adr.md`, `specs/hld.md`, `specs/lld.md`
- 체크리스트: `checklists/common-checklist.md`, `checklists/{type}-checklist.md`
- 템플릿: `templates/adr.md`, `templates/hld.md`, `templates/lld.md`
- 피드백 스키마 기준: `contract.json`

## Subagent 아키텍처

```text
doc-orchestrator
├── adr-writer
├── hld-writer
├── lld-writer
├── content-reviewer
├── style-learner
└── style-analyzer
```

## 워크플로우

1. 사용자 요청을 문서 타입으로 판별합니다.
2. 해당 writer가 계약과 참조 파일을 사용해 초안을 작성합니다.
3. `content-reviewer`가 88점 기준으로 검토합니다 (Spec 도출 가능성 포함).
4. 사용자가 승인할 때까지 수정 루프를 반복합니다.
