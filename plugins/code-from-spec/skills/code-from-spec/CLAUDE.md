# code-from-spec 플러그인

이 플러그인의 구조와 정책은 `contract.json`이 기준입니다.

## 우선순위

1. `contract.json`
2. `specs/*.md`, `checklists/*.md`, `templates/*.md`

## 핵심 계약

- 스케줄링: Spec 의존성 분석 + Jira 티켓 + Git 브랜치 + 실행 순서
- 빌드 검증: 빌드 성공 + 테스트 통과 + TC-ID 대응
- 모호점 로그: 구현 중 임의 판단 항목을 ambiguity-log.md에 기록
- 준수도 검증: 4영역, 100점 만점 + Spec 갭 플래그
- Spec 피드백: 모호점 + 갭 + PR 리뷰에서 수정 제안, 사용자 승인 필수
- 코드 리뷰 루프: 프로젝트 유형별 체크리스트 + 프로젝트 커스텀 규칙으로 리뷰 → 수정 반복 (최대 3회)
- review-apply: PR 리뷰 → 코드 수정 → 재검증 → Spec 동기화 한 사이클
- 통합: 모든 Spec 브랜치를 로컬 integration branch에 머지 → 전체 테스트 → push 확인
- 구현 추적: Spec 파일에 Jira/PR/commit 기록 (Spec = SSOT)
- 리포트 저장: `reports/` 디렉토리

## 서브에이전트 아키텍처

```text
impl-orchestrator
├── work-scheduler
├── code-generator
├── spec-verifier
└── spec-feedback
```

## 워크플로우

1. `impl-orchestrator`가 커맨드를 판별합니다.
2. `code-generator`가 Spec에서 코드를 생성합니다 (Agent Teams + 모호점 로그).
3. `spec-verifier`가 4영역으로 Spec 준수도를 검증합니다 (Spec 갭 플래그).
4. `spec-feedback`이 모호점 + 갭에서 Spec 수정 제안을 생성합니다.

## 참조 파일

- 스케줄링 절차: `specs/scheduling-procedure.md`
- 구현 절차: `specs/impl-procedure.md`
- 검증 절차: `specs/verify-procedure.md`
- 피드백 절차: `specs/feedback-procedure.md`
- 작업 계획서: `templates/work-plan.md`
- 구현 프롬프트: `templates/impl-prompt.md`
- 준수도 리포트: `templates/compliance-report.md`
- 피드백 리포트: `templates/feedback-report.md`
- 스케줄링 체크리스트: `checklists/scheduling-checklist.md`
- 구현 체크리스트: `checklists/impl-checklist.md`
- 검증 체크리스트: `checklists/verify-checklist.md`
- 피드백 체크리스트: `checklists/feedback-checklist.md`
