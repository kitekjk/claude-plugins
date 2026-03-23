# 검증 절차 스펙

## 목적

구현된 코드가 Spec을 얼마나 충실히 따르는지 검증하는 절차를 정의한다.

## 사전 조건

- 구현 디렉토리에 빌드 가능한 프로젝트가 존재
- Spec 디렉토리에 Spec 문서가 존재

## 절차

### Phase 1: Spec 항목 수집

Spec 디렉토리에서 검증 대상을 추출한다.

| 추출 대상 | 소스 |
|-----------|------|
| Spec 목록 (ID + type) | 기본 정보 섹션의 Spec ID와 type 필드 |
| 수정 대상 파일 목록 | 각 Spec의 "수정 대상 파일" 섹션 |
| 비즈니스 규칙 목록 | policies/ |
| TC-ID 목록 | 테스트 시나리오 |
| 아키텍처 규칙 목록 | architecture-rules.md |

### Phase 2: 코드 매핑

구현 코드에서 각 Spec 항목에 대응하는 코드를 찾는다.

| Spec 항목 | 코드 매핑 대상 |
|-----------|---------------|
| usecase Spec | Application Service / Controller |
| model Spec | Entity / Repository |
| service Spec | Domain Service |
| refactoring Spec | 기존 코드 리팩터링 (외부 동작 불변) |
| performance Spec | 성능 최적화 코드 |
| simplification Spec | 대상 코드 제거/병합 + Migration 코드 |
| 비즈니스 규칙 | Domain/Policy 클래스 |
| TC-ID | @Tag 테스트 |
| 아키텍처 규칙 | 패키지 구조, import 분석 |

### Phase 3: 항목별 검증

4개 영역으로 검증을 수행한다.

#### V1: 기능 구현 완결성 (40점)
- usecase Spec의 기본 흐름이 구현되었는지
- model Spec의 엔티티/리포지토리가 존재하는지
- service Spec의 도메인 서비스가 구현되었는지
- 수정 대상 파일이 모두 생성/수정되었는지
- 에러 응답이 정의된 대로 처리되는지
- refactoring/simplification Spec의 Before 코드가 제거/변환되었는지
- simplification Spec의 After 상태가 구현되고 Migration 로직이 존재하는지
- performance Spec의 목표 지표가 달성 가능한 구조인지

#### V2: 비즈니스 규칙 준수 (30점)
- policies/의 각 규칙이 코드에 반영되었는지
- 경계값 처리 (반올림, 절사, 범위 체크)
- 상태 전이 규칙
- 권한/접근 제어 규칙

#### V3: 아키텍처 준수 (15점)
- 레이어 분리 (도메인에 프레임워크 의존성 없음)
- 의존성 방향 규칙
- 모듈/패키지 구조
- 아키텍처 패턴 적용 여부

#### V4: 테스트 커버리지 (15점)
- TC-ID가 @Tag로 존재하는지
- 테스트가 실제로 통과하는지
- Given-When-Then 시나리오 반영 여부

### Phase 4: 빌드 + 테스트 실행

- 빌드 성공 확인
- 전체 테스트 통과 확인

### Phase 5: 리포트 생성

- 영역별 점수 산출
- 총점 + 등급 계산
- 미준수 항목 상세 기록
- `reports/compliance-{date}.md`에 저장
