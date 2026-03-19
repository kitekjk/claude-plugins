# 네이밍 가이드 (Naming Guide)

> 생성 주체: design-analyzer
> 생성 시점: 파이프라인 ① 단계
> 참조 출처: 코드 구조 분석 (existing-project) 또는 preset (new-project)

---

## 클래스 네이밍 규칙

| 역할 | 접미사 패턴 | 예시 |
|-----|-----------|------|
| Use Case 인터페이스 | `{Name}UseCase` | `CreateOrderUseCase` |
| Use Case 구현체 | `{Name}Service` | `CreateOrderService` |
| Repository 인터페이스 (Port) | `{Name}Port` | `OrderPort` |
| Repository 구현체 (Adapter) | `{Name}PersistenceAdapter` | `OrderPersistenceAdapter` |
| REST Controller | `{Name}Controller` | `OrderController` |
| Temporal Activity 인터페이스 | `{Name}Activity` | `SapPoSendActivity` |
| Temporal Activity 구현체 | `{Name}ActivityImpl` | `SapPoSendActivityImpl` |
| Temporal Workflow 인터페이스 | `{Name}Workflow` | `PoProcessingWorkflow` |
| Temporal Workflow 구현체 | `{Name}WorkflowImpl` | `PoProcessingWorkflowImpl` |
| Kafka Consumer | `{Name}Consumer` | `OrderEventConsumer` |
| 도메인 엔티티 | `{Name}` | `Order`, `OrderItem` |
| DTO (요청) | `{Name}Request` | `CreateOrderRequest` |
| DTO (응답) | `{Name}Response` | `CreateOrderResponse` |
| 이벤트 | `{Name}Event` | `OrderCreatedEvent` |
| 예외 | `{Name}Exception` | `OrderNotFoundException` |

## 패키지 네이밍 규칙

```
{루트 패키지}/
├── domain/
│   ├── {도메인명}/          # 도메인 엔티티, 값 객체, 도메인 서비스
│   └── ...
├── application/
│   ├── {도메인명}/          # Use Case, Port, DTO
│   └── ...
├── infrastructure/
│   ├── persistence/         # Repository 구현체
│   ├── external/            # 외부 시스템 어댑터
│   └── config/              # 설정 클래스
└── interfaces/
    ├── rest/                # REST Controller
    ├── event/               # 이벤트 리스너/컨슈머
    └── schedule/            # 스케줄러
```

## API 경로 규칙

| 규칙 | 형식 | 예시 |
|-----|------|------|
| 리소스 복수형 | `/api/{resources}` | `/api/orders` |
| 계층 구조 | `/api/{parent}/{id}/{child}` | `/api/orders/123/items` |
| 동사 금지 | 명사 사용 | `/api/orders` (O), `/api/createOrder` (X) |
| 케이스 | 소문자 케밥케이스 | `/api/purchase-orders` |
| 버전 | `/api/v{N}/{resource}` | `/api/v1/orders` |

### HTTP 메서드 매핑

| 동작 | HTTP 메서드 | 경로 예시 |
|-----|-----------|---------|
| 생성 | POST | `POST /api/orders` |
| 전체 조회 | GET | `GET /api/orders` |
| 단건 조회 | GET | `GET /api/orders/{id}` |
| 전체 수정 | PUT | `PUT /api/orders/{id}` |
| 부분 수정 | PATCH | `PATCH /api/orders/{id}` |
| 삭제 | DELETE | `DELETE /api/orders/{id}` |

## Spec ID 네이밍 규칙

```
SPEC-{PREFIX}-{DOMAIN}-{NNN}-{name}
```

| 구성요소 | 설명 | 예시 |
|---------|------|------|
| `{PREFIX}` | 프로젝트 약어 (2~4자 대문자) | `SCM`, `PES`, `OMS` |
| `{DOMAIN}` | 도메인 약어 (대문자) | `ORDER`, `USER`, `PO` |
| `{NNN}` | 3자리 순번 | `001`, `002` |
| `{name}` | 기능명 (소문자 케밥케이스) | `create-order`, `sap-po-send` |

### 예시

- `SPEC-SCM-ORDER-001-create-order`
- `SPEC-SCM-PO-002-sap-po-send`
- `POLICY-ORDER-001`
- `POLICY-NFR-001`
