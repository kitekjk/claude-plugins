# spec-from-design 플러그인

이 플러그인의 모든 규칙은 `contract.json`이 기준입니다.

## 우선순위

1. `contract.json`
2. `specs/*.md`, `templates/*.md`, `checklists/*.md`
3. `mappings/*.md`
4. `presets/*.md`

프리셋은 아키텍처/네이밍 기본값만 제공합니다. HLD/LLD 내용과 충돌하면 HLD/LLD가 우선입니다.

## 두 가지 모드

| 모드 | 조건 | 아키텍처/네이밍 소스 |
|------|------|-------------------|
| `existing-project` | 코드가 있음 | 코드에서 추출 |
| `new-project` | 코드 없음 | 프리셋 사용 (기본: `ddd-clean-kotlin`) |

## 핵심 규칙

- 입력 품질 검증 후 Spec 생성 시작
- 출력 품질 80점 이상 통과
- HLD/LLD 추적성 10점 미만이면 FAIL
- 프리셋은 HLD/LLD 내용을 덮어쓰지 않음
- 기존 코드가 있으면 하위호환 유지

## Subagent 아키텍처

```text
spec-orchestrator
├── design-analyzer
├── usecase-api-writer
├── policy-extractor
├── test-scenario-writer
└── spec-reviewer
```

## Spec 타입

| 타입 | 소스 | 담당 |
|------|------|------|
| Use Case | LLD FR + 클래스 설계 | usecase-api-writer |
| API Spec | LLD API 설계 | usecase-api-writer |
| 정책 | HLD KDD + LLD 설계 판단 | policy-extractor |
| 서비스 정의 | HLD Glossary + Overview | design-analyzer |
| 아키텍처 규칙 | HLD Architecture + 코드/프리셋 | design-analyzer |
| 네이밍 가이드 | 코드 추출 또는 프리셋 | design-analyzer |
| 테스트 시나리오 | LLD FR 검증 기준 + 리스크 | test-scenario-writer |
