# ddd-clean-kotlin

> **사용 시점**: new-project 모드에서 orchestrator가 자동 선택하는 기본 preset
> **목적**: DDD + Clean Architecture 기반 Kotlin Spring Boot 프로젝트의 아키텍처 규칙 정의

---

## 기술 스택

| 항목 | 버전 / 선택 |
|------|-----------|
| 언어 | Kotlin 2.x |
| 프레임워크 | Spring Boot 3.x |
| JDK | 21 (Virtual Threads 지원) |
| 빌드 도구 | Gradle (Kotlin DSL) |
| DB | MySQL 8.x |
| ORM | Spring Data JPA + Hibernate |
| 테스팅 | JUnit 5 + MockK + Testcontainers |
| 비동기 | Kotlin Coroutines (선택) |

---

## 레이어 구조 (Clean Architecture)

```
src/main/kotlin/{basePackage}/
├── domain/                         # 도메인 레이어
│   ├── model/                      # 엔티티, 값 객체, 애그리거트
│   ├── service/                    # 도메인 서비스
│   └── event/                      # 도메인 이벤트
│
├── application/                    # 애플리케이션 레이어
│   ├── usecase/                    # Use Case 인터페이스 및 구현체
│   ├── port/                       # 포트 (인터페이스)
│   │   ├── in/                     # 인바운드 포트
│   │   └── out/                    # 아웃바운드 포트
│   └── dto/                        # 애플리케이션 DTO
│
├── infrastructure/                 # 인프라 레이어
│   ├── persistence/                # 영속성 어댑터
│   │   ├── entity/                 # JPA 엔티티
│   │   ├── repository/             # Spring Data Repository
│   │   └── adapter/                # 영속성 어댑터 구현체
│   ├── external/                   # 외부 시스템 어댑터
│   │   ├── client/                 # HTTP/gRPC 클라이언트
│   │   └── adapter/                # 외부 어댑터 구현체
│   └── config/                     # 인프라 설정 (DB, 캐시, MQ 등)
│
└── interfaces/                     # 인터페이스 레이어
    ├── rest/                       # REST Controller + DTO
    │   └── dto/
    ├── event/                      # Kafka Consumer / Producer
    ├── scheduler/                  # @Scheduled 클래스
    └── temporal/                   # Temporal Activity/Workflow 구현체
```

---

## 레이어 의존성 규칙

```
interfaces/ → application/ → domain/
infrastructure/ → application/
infrastructure/ → domain/

[금지]
domain/ → application/
domain/ → infrastructure/
application/ → infrastructure/
application/ → interfaces/
```

- **domain**은 외부 의존성 없음 (순수 비즈니스 로직)
- **application**은 인터페이스(Port)만 알고 구현체를 직접 참조하지 않음
- **infrastructure**와 **interfaces**는 application 포트를 구현하거나 호출

---

## 네이밍 규칙

### 클래스 네이밍

| 유형 | 패턴 | 예시 |
|------|------|------|
| Use Case 인터페이스 | `{Name}UseCase` | `CreateOrderUseCase` |
| Use Case 구현체 | `{Name}Service` | `CreateOrderService` |
| 인바운드 포트 | `{Name}UseCase` (UseCase와 동일) | `CreateOrderUseCase` |
| 아웃바운드 포트 | `{Name}Port` | `OrderPersistencePort` |
| 영속성 어댑터 | `{Name}PersistenceAdapter` | `OrderPersistenceAdapter` |
| 외부 어댑터 | `{Name}Adapter` | `SapApiAdapter` |
| REST Controller | `{Name}Controller` | `OrderController` |
| REST 요청 DTO | `{Name}Request` | `CreateOrderRequest` |
| REST 응답 DTO | `{Name}Response` | `CreateOrderResponse` |
| Kafka Consumer | `{Name}EventConsumer` | `OrderEventConsumer` |
| Temporal Activity 인터페이스 | `{Name}Activity` | `SapPoSendActivity` |
| Temporal Activity 구현체 | `{Name}ActivityImpl` | `SapPoSendActivityImpl` |
| Temporal Workflow 인터페이스 | `{Name}Workflow` | `PoProcessingWorkflow` |
| Temporal Workflow 구현체 | `{Name}WorkflowImpl` | `PoProcessingWorkflowImpl` |
| JPA 엔티티 | `{Name}JpaEntity` | `OrderJpaEntity` |
| 도메인 엔티티 | `{Name}` | `Order` |
| 값 객체 | `{Name}` | `Money`, `OrderId` |

### 패키지 네이밍

| 기준 | 규칙 |
|------|------|
| 도메인 기준 분리 | `order`, `payment`, `inventory` 등 도메인으로 1차 분리 |
| 레이어 2차 분리 | `domain`, `application`, `infrastructure`, `interfaces` |
| 예시 | `com.example.order.application.usecase` |

### API 경로 규칙

| 규칙 | 예시 |
|------|------|
| 복수형 명사 사용 | `/api/orders`, `/api/payments` |
| 소문자 kebab-case | `/api/purchase-orders` |
| 버전 prefix | `/api/v1/orders` |
| 계층 표현 | `/api/orders/{orderId}/items` |

---

## 진입점 정의 (entryPoints)

이 preset은 contract.json의 기본 5개 진입점을 그대로 사용합니다.

| 유형 | 위치 | 클래스 패턴 |
|------|------|-----------|
| REST API | `interfaces/rest/` | `*Controller` |
| Temporal Activity | `interfaces/temporal/` | `*ActivityImpl` |
| Temporal Workflow | `interfaces/temporal/` | `*WorkflowImpl` |
| Kafka Consumer | `interfaces/event/` | `*EventConsumer` |
| Scheduler | `interfaces/scheduler/` | `@Scheduled` 포함 클래스 |

---

## 테스트 전략

| 레이어 | 테스트 유형 | 도구 |
|--------|-----------|------|
| domain/ | 단위 테스트 | JUnit 5 + MockK |
| application/ | 단위 테스트 | JUnit 5 + MockK |
| infrastructure/ | 통합 테스트 | JUnit 5 + Testcontainers |
| interfaces/ | 통합 테스트 | JUnit 5 + MockMvc / MockK |
| 전체 흐름 | E2E 테스트 | JUnit 5 + Testcontainers |

### 테스트 네이밍

```kotlin
// 메서드명: {대상 메서드}_{상황}_{기대 결과}
@Test
fun `createOrder 유효한 주문 요청 시 주문이 생성된다`() { ... }

@Test
fun `createOrder 재고 부족 시 InsufficientStockException 발생한다`() { ... }
```

---

## customEntryPoints 확장 가이드

이 preset의 기본 진입점 외에 추가 진입점이 필요한 경우 contract.json을 수정합니다.

### 추가 방법

`contract.json`의 `identificationRules.customEntryPoints`에 추가:

```json
"customEntryPoints": [
  "gRPC Service (ServiceImpl 클래스)",
  "WebSocket Handler (WebSocketHandler 클래스)",
  "Batch Job (JobLauncher / Step 구현체)"
]
```

### 추가 예시

| 진입점 유형 | 클래스 패턴 | 위치 | 추가 이유 |
|-----------|-----------|------|---------|
| gRPC Service | `*ServiceImpl` (gRPC 생성 base 상속) | `interfaces/grpc/` | 외부 gRPC 클라이언트 요청 처리 |
| WebSocket Handler | `*WebSocketHandler` | `interfaces/websocket/` | 실시간 채팅, 알림 처리 |
| Batch Job Step | `*Tasklet` / `*ItemProcessor` | `infrastructure/batch/` | 대용량 데이터 처리 |

### customEntryPoints 추가 시 주의사항

1. usecase-identifier에게 새 진입점 유형을 명확히 안내해야 합니다.
2. 네이밍 규칙 테이블에 새 유형의 패턴을 추가합니다.
3. lld-to-spec.md의 진입점 유형별 매핑 규칙 테이블을 업데이트합니다.

---

## Spec 파일 위치

이 preset을 사용하는 프로젝트의 Spec 저장 경로:

| 유형 | 기본 경로 |
|------|---------|
| UC Spec | `docs/specs/` |
| Policy | `docs/policies/` |
| Foundation | `docs/` |

> `contract.json`의 `storagePaths.pathFlexibility = true`이므로 사용자가 경로를 변경할 수 있습니다.
