# spec-harness 플러그인

이 플러그인의 구조와 정책은 `contract.json`이 기준입니다.

## 우선순위

1. `contract.json`
2. `specs/*.md`, `checklists/*.md`, `templates/*.md`

## 핵심 계약

- regen 독립성: 별도 세션, 코드 미참조, 동일 Spec만 입력
- 빌드 검증: 빌드 성공 + 테스트 통과 + TC-ID 대응
- 비교 체계: 5 Level, 100점 만점
- Spec 보강: 사용자 승인 필수
- 리포트 저장: `reports/determinism-{date}.md`

## 서브에이전트 아키텍처

```text
harness-orchestrator
├── code-generator
├── determinism-evaluator
└── spec-improver
```

## 워크플로우

1. `harness-orchestrator`가 커맨드를 판별합니다.
2. `code-generator`가 Spec에서 코드를 생성합니다 (Agent Teams).
3. `determinism-evaluator`가 5 Level로 비교합니다.
4. `spec-improver`가 차이점에서 Spec 보강 항목을 추출합니다.

## 참조 파일

- 재생성 절차: `specs/regen-procedure.md`
- 비교 레벨: `specs/comparison-levels.md`
- 재생성 프롬프트: `templates/regen-prompt.md`
- 리포트 형식: `templates/determinism-report.md`
- 재생성 체크리스트: `checklists/regen-checklist.md`
- 비교 체크리스트: `checklists/comparison-checklist.md`
