# spec-from-design 플러그인 재설계 세션 노트

## 세션 날짜: 2026-03-13

## 진행 사항

### 1. 생성 프롬프트 작성 완료
- `spec-from-design-rebuild-prompt.md` — 기존 플러그인을 참조하지 않고 처음부터 만드는 순수 생성 프롬프트로 작성
- "재설계/개선" 뉘앙스 모두 제거, "유지할 것/바꿀 것" → "필수 요구사항/설계 핵심 사항"으로 변경
- 에이전트 아키텍처 옵션 A/B/C → 확정 구조로 단일화

### 2. 에이전트 아키텍처 설계
- **10개 에이전트** 파이프라인 확정:
  ```
  orchestrator → analyzer → identifier → identification-verifier
  → policy-extractor → writer → scope-evaluator → usecase-splitter(조건부)
  → test-scenario-writer → reviewer
  ```
- 주요 설계 결정:
  - `usecase-identifier`: Use Case 식별 전담 (식별 목록만 산출)
  - `identification-verifier`: 식별 후 완전성·1:1 매핑 검증 게이트 추가
  - `usecase-writer`: 규모 무관하게 무조건 1 UC = 1 파일로 작성만 담당
  - `scope-evaluator`: writer 산출물의 분해 필요 여부 판정
  - `usecase-splitter`: 조건부 실행, 대규모 UC를 model/service Spec으로 분해

### 3. usecase-identifier 테스트
- `scm-pms-be` 프로젝트의 실제 HLD/LLD로 테스트 수행
- 테스트 스킬 생성: `/Users/kay.kim/works/scm-pms-be/.claude/skills/usecase-identifier-test/SKILL.md`
- **결과**:
  - po-state-management LLD → **UC 7개** (Activity 6개 변경 + Scheduler 1개 신규)
  - po-cancel-flow LLD → **UC 3개** (REST API 1 + Workflow 1 + Activity 1, 모두 신규)
  - **총 10개 UC** 식별
- 기존 플러그인 산출물(SPEC-PO-001~007, 총 7개)과 비교:
  - po-state-management: 기존 model/service/usecase 3개 → Activity별 7개로 세분화
  - po-cancel-flow: 거의 동일

### 4. 외부 스킬 조사
- Anthropic 공식 (anthropics/skills, claude-plugins-official): usecase 관련 스킬 없음
- 커뮤니티: DDD/Clean Architecture 패턴 스킬은 있으나, HLD/LLD에서 usecase 추출하는 스킬은 없음
- → 직접 설계해야 하는 영역

## 미결 사항 / 다음 할 일

1. **po-state-management UC 세분화 적절성 판단**: Activity별 분리가 과한지 확인 필요
2. **usecase-identifier 스킬 고도화**: 현재는 테스트용 기본 스킬. 진입점 판별 로직 정밀화 필요
3. **프롬프트 기반 실제 플러그인 생성**: `spec-from-design-rebuild-prompt.md`로 v2.0.0 플러그인 생성 실행
4. **identification-verifier 로직 설계**: 완전성·1:1 매핑 검증의 구체적 구현
5. **scope-evaluator 기준 정의**: 분해가 필요한 "대규모"의 정량적 기준 (파일 10개 초과? FR 5개 초과?)

## 관련 파일
- `spec-from-design-rebuild-prompt.md` — 플러그인 생성 명세서
- `plugins/spec-from-design/` — 기존 플러그인 (v1.7.0, 참고용)
