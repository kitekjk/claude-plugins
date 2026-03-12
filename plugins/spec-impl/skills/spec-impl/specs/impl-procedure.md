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
| 2 | 도메인 | service-definition | domain/** | T1 |
| 3 | 애플리케이션 | Use Case, API, policies | application/**, interfaces/**, infrastructure/** | T2 |
| 4 | 테스트 | 테스트 시나리오 (TC-ID) | src/test/** | T1,T2,T3 |

### Phase 3: 빌드 검증

- 빌드 성공 확인
- 전체 테스트 통과 확인
- 실패 시 최대 3회 재시도
- 3회 후에도 실패 시 실패 리포트 반환

### Phase 4: TC-ID 커버리지 확인

- Spec의 모든 TC-ID가 테스트 코드에 @Tag로 존재하는지 확인
- 누락된 TC-ID 목록 보고

## Teammate 컨텍스트 제한

각 Teammate는 자신의 기반 Spec만 로드한다.
불필요한 파일을 로드하지 않아 컨텍스트 윈도우를 효율적으로 사용한다.

| Teammate | 읽기 | 읽지 않기 |
|----------|------|-----------|
| T1 (인프라) | architecture-rules, infra-config, naming-guide | Use Case, API Spec |
| T2 (도메인) | service-definition, naming-guide, policies (검증 규칙) | infra-config, API Spec |
| T3 (앱) | Use Case, API, policies, naming-guide | infra-config |
| T4 (테스트) | 테스트 시나리오 섹션들, naming-guide | infra-config |
