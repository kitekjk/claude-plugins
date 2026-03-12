# 프리셋: DDD + Clean Architecture + Kotlin

> new-project 모드에서 코드가 없을 때 사용하는 아키텍처/네이밍 기본값입니다.
> HLD/LLD 내용과 충돌하면 **HLD/LLD가 우선**합니다.

## 기술 스택

| 항목 | 기본값 |
|------|--------|
| 언어 | Kotlin 2.x |
| 프레임워크 | Spring Boot 3.x |
| JDK | 21 |
| 빌드 도구 | Gradle (Kotlin DSL) |
| DB | MySQL 8.x + Spring Data JPA |
| 인증 | Spring Security 6.x + JWT |
| 테스트 | JUnit 5 + MockK + Testcontainers |
| 린트 | Spotless + ktlint |

## 레이어 구조 (Clean Architecture)

```
{module}/
├── domain/              # 도메인 레이어 (가장 안쪽)
│   ├── model/           # Entity, Value Object, Aggregate Root
│   ├── event/           # Domain Event
│   ├── exception/       # 도메인 예외
│   └── service/         # Domain Service (순수 비즈니스 로직)
├── application/         # 애플리케이션 레이어
│   ├── port/
│   │   ├── in/          # Input Port (Use Case 인터페이스)
│   │   └── out/         # Output Port (Repository, External 인터페이스)
│   ├── service/         # Use Case 구현
│   └── dto/             # Command, Query DTO
├── infrastructure/      # 인프라 레이어 (가장 바깥)
│   ├── persistence/     # JPA Repository 구현
│   ├── external/        # 외부 시스템 Adapter
│   ├── config/          # Spring Config
│   └── security/        # Security Config
└── interfaces/          # 인터페이스 레이어
    ├── web/             # REST Controller
    │   ├── dto/         # Request/Response DTO
    │   └── handler/     # Exception Handler
    └── event/           # Event Listener
```

## 의존성 규칙

```
interfaces → application → domain
infrastructure → application → domain

domain은 다른 레이어에 의존하지 않는다.
application은 domain에만 의존한다.
infrastructure는 application의 port/out을 구현한다.
interfaces는 application의 port/in을 호출한다.
```

## 네이밍 컨벤션

### 패키지

| 레이어 | 패턴 | 예시 |
|--------|------|------|
| 최상위 | `com.{회사}.{서비스}.{도메인}` | `com.example.lms.attendance` |
| domain/model | `{도메인}.domain.model` | `attendance.domain.model` |
| application/service | `{도메인}.application.service` | `attendance.application.service` |
| interfaces/web | `{도메인}.interfaces.web` | `attendance.interfaces.web` |

### 클래스

| 유형 | 접미사 | 예시 |
|------|--------|------|
| Entity | 없음 | `Attendance`, `Employee` |
| Value Object | 없음 | `WorkSchedule`, `TimeRange` |
| Aggregate Root | 없음 | `Attendance` |
| Domain Service | `DomainService` | `AttendanceCalculationDomainService` |
| Use Case (Interface) | `UseCase` | `CheckInUseCase` |
| Use Case (Impl) | `Service` | `CheckInService` |
| Input Port | `UseCase` | `CheckInUseCase` |
| Output Port | `Port` | `AttendancePort`, `EmployeePort` |
| Repository 구현 | `Adapter` | `AttendancePersistenceAdapter` |
| External Adapter | `Client` | `PayrollClient` |
| Controller | `Controller` | `AttendanceController` |
| Request DTO | `Request` | `CheckInRequest` |
| Response DTO | `Response` | `AttendanceResponse` |
| Command DTO | `Command` | `CheckInCommand` |
| Query DTO | `Query` | `AttendanceQuery` |
| Exception | `Exception` | `AlreadyCheckedInException` |
| Event | `Event` | `CheckedInEvent` |

### API 경로

| 규칙 | 예시 |
|------|------|
| REST 리소스 복수형 | `/api/v1/attendances` |
| 하이픈 구분 | `/api/v1/work-schedules` |
| 버전 포함 | `/api/v1/...` |
| 액션은 동사 허용 | `/api/v1/attendances/{id}/check-in` |

### 변수/필드

| 규칙 | 예시 |
|------|------|
| camelCase | `checkInTime`, `employeeId` |
| Boolean은 is/has/can 접두사 | `isActive`, `hasPermission` |
| 컬렉션은 복수형 | `employees`, `schedules` |
| ID 필드는 `{entity}Id` | `attendanceId`, `employeeId` |

## DDD 패턴 가이드

### Entity
```kotlin
@Entity
@Table(name = "attendances")
class Attendance(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    // 비즈니스 로직을 Entity 내부에
    fun checkIn(time: LocalDateTime) { ... }
)
```

### Value Object
```kotlin
@Embeddable
data class TimeRange(
    val startTime: LocalDateTime,
    val endTime: LocalDateTime
) {
    init { require(startTime.isBefore(endTime)) }
}
```

### Use Case (Port)
```kotlin
interface CheckInUseCase {
    fun execute(command: CheckInCommand): AttendanceId
}
```

### Use Case 구현
```kotlin
@Service
@Transactional
class CheckInService(
    private val attendancePort: AttendancePort,
    private val employeePort: EmployeePort
) : CheckInUseCase {
    override fun execute(command: CheckInCommand): AttendanceId {
        // 1. 직원 확인
        // 2. 중복 출근 검증
        // 3. 출근 기록 생성
        // 4. 이벤트 발행
    }
}
```

## 테스트 규칙

| 규칙 | 설명 |
|------|------|
| 테스트 프레임워크 | JUnit 5 + MockK |
| 테스트 어노테이션 | `@Tag("TC-xxx")` |
| DB 테스트 | Testcontainers (MySQL) |
| 통합 테스트 | `@SpringBootTest` |
| 단위 테스트 | Plain Kotlin + MockK |
| 네이밍 | `should_결과_when_조건` 또는 백틱 함수명 |

```kotlin
@Tag("TC-ATT-001-01")
@Test
fun `should create attendance when valid check-in`() {
    // Given
    // When
    // Then
}
```

## Gradle 멀티모듈 (대규모 프로젝트)

```
settings.gradle.kts:
  include("domain")
  include("application")
  include("infrastructure")
  include("interfaces")
  include("bootstrap")     # Spring Boot main + 조립
```

## 이 프리셋을 사용하지 않아야 할 때

- 프로젝트가 Java, Python, TypeScript 등 다른 언어인 경우
- Hexagonal이 아닌 다른 아키텍처 패턴을 사용하는 경우
- 모노리스가 아닌 마이크로서비스 특화 구조가 필요한 경우

이 경우 새 프리셋 파일을 `presets/` 디렉토리에 추가하세요.
