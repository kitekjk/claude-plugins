# LLD → Spec 매핑 규칙 (lld-to-spec)

> **참조 에이전트**: usecase-identifier(②), usecase-writer(⑤), test-scenario-writer(⑧)
> **목적**: LLD의 각 요소가 어느 Spec 요소로 변환되는지 정의

---

## 기본 원칙

**UC 식별이 FR 매핑보다 먼저 수행되어야 합니다.**

1. usecase-identifier가 구현 클래스 → UC 목록을 먼저 확정합니다.
2. identification-verifier가 UC 목록의 완전성·1:1 매핑을 검증합니다.
3. 검증 통과 후에야 usecase-writer가 FR → 기본 흐름 변환을 시작합니다.

이 순서를 지키지 않으면 UC 유형 오분류와 병합 매핑이 발생합니다.

---

## LLD 요소 → Spec 매핑 테이블

| LLD 요소 | Spec 매핑 대상 | 담당 에이전트 | 비고 |
|---------|--------------|------------|------|
| 구현 클래스 (진입점) | UC 식별 목록 → Spec 파일 | usecase-identifier | 클래스 1개 = Spec 파일 1개 |
| FR (기능 요구사항) | 기본 흐름 (번호 리스트) | usecase-writer | FR → 자연어 단계로 변환 |
| FR 검증 기준 | 테스트 시나리오 (Given-When-Then) | test-scenario-writer | positive/negative/edge-case 포함 |
| 클래스 / 컴포넌트 설계 | 수정 대상 파일 + dependsOn | usecase-writer | 의존 클래스 → dependsOn yaml |
| 설계 판단 / 트레이드오프 | 대안 흐름 + Policy | usecase-writer + policy-extractor | 단순 판단 → 대안 흐름, 재사용 규칙 → Policy |
| 미해결 리스크 | 엣지 케이스 테스트 시나리오 | test-scenario-writer | 리스크 1개 = 엣지 케이스 시나리오 1개 이상 |
| DB 스키마 | model Spec 필드 정의 | usecase-splitter (분해 시) | 분해 대상에서만 생성 |
| API 설계 (request/response) | 수정 대상 파일 (Controller/DTO) | usecase-writer | request → {Name}Request, response → {Name}Response |
| 시퀀스 다이어그램 | 기본 흐름 단계 순서 | usecase-writer | 호출 순서 → 기본 흐름 단계 번호 |

---

## 진입점 유형별 매핑 규칙

### 1. REST API

| LLD 항목 | Spec 매핑 |
|---------|---------|
| 엔드포인트 (`POST /api/orders`) | Spec 파일명 (`SPEC-{PREFIX}-ORDER-001-create-order.md`) |
| request body 구조 | 수정 대상 파일: `{Name}Request.kt` |
| response body 구조 | 수정 대상 파일: `{Name}Response.kt` |
| Controller 메서드 | 기본 정보 `구현 클래스: OrderController.createOrder` |
| HTTP 상태 코드 | 검증 조건에 포함 |

**예시:**
```
LLD: POST /api/orders → OrderController.createOrder()
Spec: SPEC-SCM-ORDER-001-create-order.md
  기본 정보:
    진입점 유형: REST API
    구현 클래스: OrderController.createOrder
  수정 대상 파일:
    - interfaces/rest/OrderController.kt
    - interfaces/rest/dto/CreateOrderRequest.kt
    - interfaces/rest/dto/CreateOrderResponse.kt
```

---

### 2. Temporal Activity

| LLD 항목 | Spec 매핑 |
|---------|---------|
| ActivityImpl 클래스명 | Spec 파일명 (camelCase → kebab-case) |
| Activity 파라미터 타입 | 기본 흐름 1단계: "입력: {파라미터 목록}" |
| Activity 반환 타입 | 기본 흐름 마지막 단계: "반환: {반환 타입}" |
| 재시도 설정 | 관련 정책 또는 대안 흐름에 반영 |

**예시:**
```
LLD: SapPoSendActivityImpl implements SapPoSendActivity
Spec: SPEC-SCM-SAP-001-sap-po-send.md
  기본 정보:
    진입점 유형: Temporal Activity
    구현 클래스: SapPoSendActivityImpl
  기본 흐름:
    1. 입력 수신: SendPoRequest (poId, lineItems)
    2. SAP API 호출: POST /sap/po/send
    3. 응답 검증: status = SUCCESS
    4. 반환: SendPoResult (success, sapPoId)
```

---

### 3. Temporal Workflow

| LLD 항목 | Spec 매핑 |
|---------|---------|
| WorkflowImpl 클래스명 | Spec 파일명 |
| Workflow 시퀀스 | 기본 흐름 단계 (Activity 호출 순서) |
| 보상 트랜잭션 | 대안 흐름에 반영 |
| 타임아웃 설정 | 관련 정책에 반영 |

**예시:**
```
LLD: PoProcessingWorkflowImpl - Activity 호출 순서: sapSend → inventoryUpdate → notify
Spec: SPEC-SCM-PO-001-po-processing.md
  기본 흐름:
    1. PO 처리 시작 신호 수신
    2. SapPoSendActivity 실행
    3. InventoryUpdateActivity 실행
    4. NotificationActivity 실행
    5. PO 상태를 COMPLETED로 업데이트
  대안 흐름:
    2a. SapPoSendActivity 실패: SapPoSendActivity 재시도 (POLICY-SCM-001 참조)
```

---

### 4. Kafka Consumer

| LLD 항목 | Spec 매핑 |
|---------|---------|
| Consumer 클래스명 | Spec 파일명 |
| 이벤트 페이로드 구조 | 기본 흐름 1단계: "입력 이벤트: {페이로드 구조}" |
| 토픽명 | 기본 정보 또는 기본 흐름 1단계 |
| 에러 핸들링 전략 | 대안 흐름에 반영 |

**예시:**
```
LLD: OrderEventConsumer - topic: order-events, payload: OrderCreatedEvent
Spec: SPEC-SCM-ORDER-002-order-event.md
  기본 정보:
    진입점 유형: Kafka Consumer
    구현 클래스: OrderEventConsumer
  기본 흐름:
    1. order-events 토픽에서 OrderCreatedEvent 수신
    2. 이벤트 유효성 검증 (orderId, eventType)
    3. 주문 처리 서비스 호출
    4. 처리 완료 후 오프셋 커밋
```

---

### 5. Scheduler

| LLD 항목 | Spec 매핑 |
|---------|---------|
| `@Scheduled` 메서드명 | Spec 파일명 |
| 스케줄 주기 (cron / fixedRate) | 기본 정보 또는 개요에 반영 |
| 실행 로직 | 기본 흐름 단계 |
| 중복 실행 방지 | 관련 정책에 반영 |

**예시:**
```
LLD: @Scheduled(cron = "0 0 1 * * *") dailySync() in SyncScheduler
Spec: SPEC-SCM-SYNC-001-daily-sync.md
  기본 정보:
    진입점 유형: Scheduler
    구현 클래스: SyncScheduler.dailySync
  개요:
    매일 오전 1시에 외부 시스템과 데이터를 동기화합니다.
```

---

## FR → 기본 흐름 변환 규칙

FR을 기본 흐름 단계로 변환할 때 아래 원칙을 따릅니다.

| 원칙 | 설명 |
|------|------|
| 자연어 기술 | 코드가 아닌 행위자(시스템) 관점의 자연어 |
| 단계별 번호 | `1. ~ 2. ~ 3. ~` 형식의 순서 있는 목록 |
| 입출력 명시 | 각 단계에서 무엇을 받고 무엇을 반환하는지 |
| FR 1개 → 단계 1개 이상 | FR이 복잡하면 여러 단계로 분해 가능 |
| 구현 코드 금지 | pseudocode도 기본 흐름이 아닌 별도 블록으로 |

---

## 설계 판단 → 대안 흐름 / Policy 분류 기준

| 설계 판단 유형 | 매핑 대상 |
|-------------|---------|
| 이 UC에만 적용되는 예외 처리 | 대안 흐름 |
| 여러 UC에 적용되는 재사용 규칙 | Policy (policy-extractor가 추출) |
| 비기능 요구사항 (성능, 보안) | POLICY-NFR-001 |
| 상태 전이 조건 | 상태 Policy 규칙 |

---

## 주의 사항

- **유형 고정**: usecase-writer는 orchestrator가 지정한 유형을 변경할 수 없습니다.
- **model/service 금지**: writer는 usecase만 생성합니다. model/service는 usecase-splitter가 분해 시에만 생성합니다.
- **DB 스키마 처리**: DB 스키마 변경이 있어도 분해 전에는 수정 대상 파일에만 포함합니다.

---

## 추적성 확인

매핑 완료 후 traceability.md의 TR-L-01~TR-L-04 항목을 확인합니다.
