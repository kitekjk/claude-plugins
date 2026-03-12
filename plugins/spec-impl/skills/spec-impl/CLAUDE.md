# spec-impl 플러그인

이 플러그인의 구조와 정책은 `contract.json`이 기준입니다.

## 우선순위

1. `contract.json`
2. `specs/*.md`, `checklists/*.md`, `templates/*.md`

## 핵심 계약

- 빌드 검증: 빌드 성공 + 테스트 통과 + TC-ID 대응
- 준수도 검증: 4영역, 100점 만점
- 리포트 저장: `reports/compliance-{date}.md`

## 서브에이전트 아키텍처

```text
impl-orchestrator
├── code-generator
└── spec-verifier
```

## 워크플로우

1. `impl-orchestrator`가 커맨드를 판별합니다.
2. `code-generator`가 Spec에서 코드를 생성합니다 (Agent Teams).
3. `spec-verifier`가 4영역으로 Spec 준수도를 검증합니다.

## 참조 파일

- 구현 절차: `specs/impl-procedure.md`
- 검증 절차: `specs/verify-procedure.md`
- 구현 프롬프트: `templates/impl-prompt.md`
- 리포트 형식: `templates/compliance-report.md`
- 구현 체크리스트: `checklists/impl-checklist.md`
- 검증 체크리스트: `checklists/verify-checklist.md`
