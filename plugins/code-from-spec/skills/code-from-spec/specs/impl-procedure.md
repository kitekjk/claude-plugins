# 구현 절차 스펙

## 목적

Spec 문서만으로 프로젝트를 처음부터 생성하는 절차를 정의한다.

## 사전 조건

- Spec 디렉토리에 Spec 문서가 존재
- Docker Desktop 실행 중
- 빌드 도구(Gradle 등) 사용 가능

## 절차

### Phase 1: 프로젝트 초기화

1. 빈 디렉토리 생성
2. Spec 문서 복사 (`docs/specs/`)
3. CLAUDE.md 복사 (프로젝트 규칙)

### Phase 2: Agent Teams 구현

4명의 Teammate가 순차적으로 구현한다.

| 순서 | Teammate | 기반 Spec | 담당 범위 | 의존 |
|------|----------|-----------|-----------|------|
| 1 | 인프라 | architecture-rules, infra-config, naming-guide | 빌드, 설정, Docker | 없음 |
| 2 | 도메인 | service-definition, model Spec | domain/** | T1 |
| 3 | 애플리케이션 | usecase/service/simplification Spec, policies | application/**, interfaces/**, infrastructure/** | T2 |
| 4 | 테스트 | 테스트 시나리오 (TC-ID) | src/test/** | T1,T2,T3 |

**refactoring/performance/simplification 유형 처리:**
- Teammate 2 (도메인): 엔티티 변경/병합/제거, 리포지토리 수정
- Teammate 3 (애플리케이션): Before → After 코드 변환, Migration 로직 구현, 기존 코드 제거/병합
- Teammate 4 (테스트): Before/After 동작 비교 테스트, Migration 테스트, 하위호환성 검증 테스트
- Spec의 "Before/After" 섹션을 기준으로 변경 범위를 판단한다.

### Phase 3: 빌드 + 테스트 검증

- 빌드 성공 확인
- 전체 테스트 통과 확인
- 실패 시 최대 3회 재시도
- 3회 후에도 실패 시 실패 리포트를 impl-orchestrator에 반환하고 **code-generator 실행을 중단한다**. impl-orchestrator가 사용자에게 보고하고 다음 행동을 결정한다.

### Phase 4: TC-ID 커버리지 게이트 (필수 — 스킵 금지)

빌드/테스트 통과 직후, 코드 리뷰 전에 TC-ID 전수 커버리지를 확인한다.

1. Spec의 `## 테스트 시나리오` 섹션에서 모든 TC-ID 추출
2. 테스트 코드에서 `@Tag("{TC-ID}")` 검색
3. 매핑 대조 → 누락 TC-ID 식별
4. **누락 시**: **Teammate 4만 재실행**하여 누락 테스트 추가 (Teammate 1~3은 재실행하지 않는다) (최대 2회). impl-orchestrator.md의 '① 재실행'은 Teammate 4 재실행을 의미한다.
5. **2회 후에도 누락 시**: 누락 목록을 impl-orchestrator에 보고 (진행 불가)
6. **전수 커버리지 달성 시**: Phase 5로 진행

> 이 게이트를 통과하지 못하면 코드 리뷰로 넘어가지 않는다.
> 프로덕션 코드만 있고 테스트가 없는 상태는 "미완료"이다.

### Phase 5: 코드 리뷰 루프

TC-ID 게이트 통과 후, PR 생성 전에 코드 리뷰를 반복 수행한다.

1. 프로젝트 유형 감지 (build.gradle → Spring, package.json + react → React)
2. 유형별 리뷰 체크리스트 로드 + 프로젝트 CLAUDE.md/AGENTS.md 커스텀 규칙 병합
3. 체크리스트 항목별 코드 검사 → 위반 항목 수정
4. 수정 후 재리뷰 (최대 3회 반복)
5. 위반 0건이면 통과, 3회 초과 시 잔여 이슈 보고
6. 수정으로 인해 테스트가 깨지면 테스트도 수정

## Teammate 컨텍스트 제한

각 Teammate는 자신의 기반 Spec만 로드한다.
불필요한 파일을 로드하지 않아 컨텍스트 윈도우를 효율적으로 사용한다.

| Teammate | 읽기 | 읽지 않기 |
|----------|------|-----------|
| T1 (인프라) | architecture-rules, infra-config, naming-guide | usecase/model/service Spec |
| T2 (도메인) | service-definition, model Spec, naming-guide, policies (검증 규칙) | infra-config |
| T3 (앱) | usecase/service/simplification Spec, policies, naming-guide | infra-config |
| T4 (테스트) | 테스트 시나리오 섹션들, naming-guide | infra-config |
