# LLD-P00. Promise Data Strategy

> **Page ID**: 235014369

---

|  |  |

| --- | --- |

| Author | [김지환/Core-E Catalog Platform jihwan.kim2](https://wiki.team.musinsa.com/wiki/people/712020:e4f6daa8-4c8c-4273-8ba6-77173f6f1109?ref=confluence) |

| Reviewers | - [박현준/Core-E Catalog Platform hyunjun.park](https://wiki.team.musinsa.com/wiki/people/712020:c4cfe18d-d170-4bb7-a4d7-55b96c4087b3?ref=confluence) - [김대일/Core Engineering irondikim](https://wiki.team.musinsa.com/wiki/people/712020:9e7487b6-e6a2-43f7-bd35-d5da8eabc0f6?ref=confluence) - [백현우/Core-E Catalog Platform hyunwoo.baig](https://wiki.team.musinsa.com/wiki/people/712020:4df62b90-4355-4159-b3c0-4ee30ff6451d?ref=confluence) - [황두리/Core-E Catalog Platform duri.hwang](https://wiki.team.musinsa.com/wiki/people/712020:8aa04b59-9c5b-432b-b616-58e0017684cc?ref=confluence) - [류욱상/Core-E Catalog Platform wooksang.ryu](https://wiki.team.musinsa.com/wiki/people/712020:f5ce9f79-b8c5-4bdd-a278-f9e5750a3e06?ref=confluence) - [정규택/Core-E Catalog Platform kyutaek.jung](https://wiki.team.musinsa.com/wiki/people/712020:663cf68a-5f24-480d-8345-e43508f9a9d5?ref=confluence) - [김도영/Core-E Catalog Platform doyoung.kim](https://wiki.team.musinsa.com/wiki/people/712020:63a3bfba-b8b3-4a2f-b1b4-d41160a57469?ref=confluence) |

| On this page |  |

# 1. Glossary


| **Term** | **Description** |

| --- | --- |

| **Promise** | 특정 시점(Cut-off)까지 주문을 완료한다는 조건 하에, **확정된 출고일만 약속함. 또는 도착일을 함께 약속함**. |

| **Cutline** | **Promise를 설정**하는 원자적 단위. Region(배송지), ShippingType(배송형태), FC(출고지) 정보와 CutOff, PSD, PDD를 포함 |

| **PSD** | Promised Ship Date. 고객에게 약속하는 출고예정일 |

| **PDD** | Promised Delivery Date. 고객에게 노출되는 최종 상품 도착 보장일 |

| **ShippingOffer** | 판매자 및 물류 소스(1P/3P), 고객배송지의 제약 조건 하에, **비용(배송/반품비)**을 정의함. |

| **Hard Failure** | 핵심 의존성 조회 실패로 인해 서비스 불능 상태가 된 경우 |

| **Soft Failure** | 의존성의 조회 실패로 Default Promise를 반환하여 기능이 심각하게 저하된 상태 |

| **SPOF** | Single Point of Failure. 장애 시 Fail-fast 처리함 |

| **Default Promise** | 외부 시스템 장애 시 주문 차단을 막기 위해 반환하는 사전에 정의된 보수적 약속 |

# 2. Problem Statement

> **Scope**: 이 문서는 **주문 시점(Order Critical Path)**의 데이터 수집 전략을 다룹니다.  
> 전시 지면(PLP, PDP, 검색 등)의 Promise 데이터 서빙 전략은 [LLD-P11. Display Promise Data Serving Strategy](/wiki/spaces/PRODUCTS/pages/268309035/LLD-P11.+Display+Promise+Data+Serving+Strategy)를 참조하세요.

Core Promise System은 단일 상품 조회 시 **P95 50ms**, 최대 **114,000 TPS**라는 극한의 성능 목표를 달성해야 합니다. 그러나 데이터를 처리할 때 단일 아키텍쳐로는 각기 다른 특성을 가진 데이터 도메인들을 효율적으로 처리하는 데 구조적 한계가 있습니다. 일반적인 원격 조회 방식조차 114k TPS 환경에서는 빈번한 네트워크 왕복과 직렬화/역직렬화 오버헤드로 인해 Latency 목표 달성을 위협하는 주요 병목이 됩니다. 이러한 각 도메인의 물리적 제약과 상충 관계를 극복하기 위해, 데이터 특성에 따라 최적화된 개별 서빙 전략 수립이 필수적입니다.


| **도메인** | **데이터 특성** | **주요 기술적 난제** |

| --- | --- | --- |

| **Catalog** | 대용량, Update 되지 않음  조회 비중 압도적 | 2,600만 건 이상의 데이터를 **10ms 이내**에 조회해야 함과 동시에 원천 데이터 변경 시 **5분 이내**에 동기화해야 하는 요구사항. |

| **Inventory** | 초고변동성  SPOF  대량 조회 | **Fan-out 트래픽 처리:** PLP 진입 시 수십 개의 상품 재고를 한 번에 조회.  재고 데이터는 매우 빠르게 변하므로 캐싱할 경우 신선하지 않은 데이터를 사용할 확률이 매우 높음  **통제 가능한 Latency:** 재고 시스템에서 40ms 이내 data serving 보장 |

| **Logistics Configuration** | 고빈도 조회  외부 시스템 소유 | 외부 시스템의 DB/API 안정성을 완벽히 통제 불가.  **장애 전파 (Cascading Failure):** 외부 시스템 장애 시 Promise 계산 전체가 불가능해지는 강한 의존성 |

# 3. Functional Requirements


| **Type** | **Requirement** | **Description** |

| --- | --- | --- |

| **Must-have** | **Promise 계산 및 조합** | 클라이언트로부터 `zipcode`, `productId(or List)`, `optionCode(Optional)`, `quantity`, `countryCode` 정보를 입력받아 데이터를 수집. 상품정보, 재고, `Cutline/ShippingOffer`, `Strategy`를 합성하여 최적의 Promise 산출 |

| **Must-have** | **계층적 입력 지원** | `productId`를 필수 파라미터로, `optionCode`를 선택적(Optional) 파라미터로 수용 |

| **Must-have** | **Promise 반환** | Cutline(Cutoff, PSD, PDD), ShippingOffer(shippingFee, returnFee) 포함 |

| **Must-have** | **Inventory 로 부터 재고 정보 및 가용성 조회** | SKU의 OOS 여부, 가용 재고가 존재하는 fcCode list와 각 FC의 잔여 수량 |

| **Must-have** | **Catalog 로 부터 상품 정보 조회** | MFS/3p Logistics 여부, 무배당발 가능 여부, 판매 가능 국가 리스트 등 |

| **Must-have** | **Logistics Configuration Provider 로 부터 Cutline/ShippingOffer 조회** | zipcode, sku, fcCode list 제공하고 Cutline, ShippingOffer 조회 |

| **Must-have** | **Strategy 의 조회** | 현재 Promise Context(지역, 고객 등급 등)를 기반으로 적용할 수 있는 Strategy를 조회한다. |

| **Must-have** | **Strategy 적용 및 위계 처리** | 조회한 Strategy들을 Promise 산출에 반영한다. 서로 상충하는 Action을 가진 Strategy들에 대해 적절한 위계를 통해 하나만 적용하거나 합성하여 최종 Promise를 도출할 수 있다. |

| **Must-have** | **Fail-fast (Inventory)** | Inventory 시스템은 SPOF로 간주. 재고 조회 실패나 SLO 초과 지연 발생 시 즉시 에러 반환 (서비스 불능 상태) |

| **Must-have** | **Fallback (Non-Critical)** | UDH, Logistics 등 Inventory 외의 외부 시스템 장애 시에는 주문 흐름을 막지 않음 |

| **nice-to-have** | **Promise 산출 근거의 역추적** | Promise가 어떤 근거로 어떻게 계산된 값인지 역추적할 수 있어야 한다. |

| **nice-to-have** | **독립적인 Strategy 시스템의 구축** | Strategy를 관리/제공하는 독립적인 시스템을 구축한다. |

| **nice-to-have** | **Configuration/Strategy 변경 시뮬레이션** | Operator가 Logistics Configuration 혹은 Strategy를 변경/추가 할 때 시스템에 미치는 영향을 시뮬레이션 해볼 수 있는 dry-run 기능을 제공한다. |

# 4. Non-Functional Requirements

## 4.1. Performance & Scalability

### 4.1.1. Promise API Latency


| **Component** | **Type** | **Requirement** |

| --- | --- | --- |

| **Promise 조회 API (상품 단건)** | Latency | **P95 50ms 이하** |

| **Promise 조회 API (옵션 리스트)** | Latency | **P95 50ms 이하** |

| **Promise 조회 API (옵션 단건)** | Latency | **P95 10ms 이하** |

| **Promise 조회 API (List)** | Latency | **P95 100ms 이하** (최대 100개 상품) |

| **System Total** | Throughput | **Target 114,000 TPS**  ([Datadog APM 기준](https://app.datadoghq.com/apm/entity/service%3Apromise-api) 현재 피크 66,000 TPS × 1.2³(3년 간 대응 가능한 수준)) |

### 4.1.2. Data Source Fetch Latency

> **Latency Budget 산정 근거**: Promise Calculation Pipeline([LLD-P01](../P01-Calculation-Pipeline-Design/DOCUMENT.md))은 Phase 1에서 Catalog와 Inventory를 **병렬 조회**합니다. 따라서 개별 Data Source의 Latency 합이 아닌, **Critical Path 기준**으로 Budget을 산정합니다.

```
Pipeline Critical Path (P99 50ms 목표):
┌─────────────────────────────────────────────────────────────┐
│ Phase 1 (병렬): max(Catalog, Inventory) ≤ 25ms             │
│ Phase 2 (순차): Logistics Config ≤ 10ms                    │
│ Phase 3 (순차): Strategy + Calculation ≤ 5ms               │
│ Phase 4 (순차): Assembly ≤ 5ms                             │
│ 네트워크/직렬화 오버헤드: ~5ms                              │
├─────────────────────────────────────────────────────────────┤
│ Total: 25 + 10 + 5 + 5 + 5 = 50ms                          │
└─────────────────────────────────────────────────────────────┘
```


| **Data Source** | **Type** | **Requirement** | **Phase** | **비고** |

| --- | --- | --- | --- | --- |

| **Inventory** | Latency | **P99 25ms 이하** | Phase 1 (병렬) | 재고 시스템 SLO 기준, ALB 경유 포함.  Catalog와 병렬 실행되므로 Phase 1의 Critical Path 결정 |

| **Catalog (UDH)** | Latency | **P99 10ms 이하** | Phase 1 (병렬) | UDH Data Serving Layer 조회 |

| **Logistics Config** | Latency | **P99 10ms 이하** | Phase 2 (순차) | Redis MGET 기준, 네트워크 오버헤드 포함 |

| **Strategy** | Latency | **P99 1ms 이하** | Phase 3 (순차) | In-memory 조회 |

| **Calculation** | Latency | **P99 4ms 이하** | Phase 3 (순차) | PSD/PDD 로컬 계산, Strategy와 동일 Phase |

### 4.1.3. Scalability & Scale-out


| **Component** | **Type** | **Requirement** | **비고** |

| --- | --- | --- | --- |

| **Promise Pod** | Scale-out 완료 시간 | **3분 이내** | 메트릭 수집 → 스케일 결정 → Pod 생성 → Readiness 통과 |

| **Promise Pod** | Scale-out 대응 | 트래픽 급증 시 수평 확장 지원 | HPA/KEDA 기반 자동 증설 |

| **Promise Pod** | Scale-out 후 트래픽 밸런싱 | **30초 이내** | Scale-out 후 연결된 pod 의 부하를 막기 위한 rebalancing 과정 |

## 4.2. Availability & Reliability


| **Metric** | **Threshold** | **Action** |

| --- | --- | --- |

| **Hard Failure** | HTTP 5xx > 1% (Inventory) | 즉시 장애 간주 (SLA 차감), Fail-fast |

| **Soft Failure** | Default Promise 반환율 ≥ 5% | 장애 간주 (SLA 차감) |

| **Degradation** | Default Promise 반환율 < 5% | 정상 가동 간주, Alert 발송 |

| **Data Consistency** | Catalog/Config 변경 반영 | 5분 이내 반영 |

# 5. Goal / Non-Goal

## 5.1. Goal

- **도메인 특성에 따른 최적의 데이터 거점 수립:** 각 도메인 데이터가 가진 변동성, 크기, 읽기 빈도 등 물리적 특성을 분석하여, 성능 목표를 달성할 수 있는 최적의 저장소 및 참조 계층 구조를 정의
- **고속 재고 인지 능력(Inventory Awareness) 확보:** 실시간성이 생명인 재고 및 위치 정보를 지연 없이 참조하여 오판매를 원천 차단
- **대규모 조회의 효율적 처리(Fan-out Optimization):** 상품 목록 조회 시 발생하는 다량의 데이터 동기 요청에 대해 네트워크 부하를 최소화

## 5.2. Non-Goal

- **상태 변경 및 데이터 관리 (State Mutation):** Promise 시스템은 읽기 전용 레이어
- **미시적 계산 알고리즘 (Micro-Logic):** 최종 약속 날짜를 산출하는 구체적인 수식이나 비즈니스 정책의 세부 가공 로직은 포함하지 않음
- **엄격한 실시간 정합성 강제 (Strict Consistency):** 비즈니스 허용 범위 내에서 Eventual Consistency 모델 지향

# 6. Proposed Design: Data Fetching Layer Strategy

## 6.1. 외부 데이터 조회 전략

Core Promise System은 **114,000 TPS**의 대규모 트래픽과 **P99 50ms**의 성능 목표를 달성하기 위해 각 도메인의 데이터 특성에 최적화된 데이터 서빙 전략을 적용합니다.


| **도메인** | **원천/주 저장소** | **서빙 전략** | **프로토콜** | **동기화 방식** | **장애 대응 전략** |

| --- | --- | --- | --- | --- | --- |

| **Inventory** | Inventory Service | **Direct RPC Call** | gRPC | **Strict Real-time** (Strong Consistency) | **Hard Failure** (Fail-fast) |

| **Catalog** | Unified Data Hub | **Data Serving Layer** (Standard API) | gRPC / REST | **Centralized NRT** (< 10s 지연) | **Soft Failure** (Default Promise 반환) |

| **Logistics** | Data Mart + Redis | **Redis Cluster** (MGET) | Redis Protocol | **Sync Worker** (5분 주기) | **Soft Failure** (Default Promise 반환) |

| **Strategy** | In-memory | **In-memory** | - | - | **Hard Failure** (Fail-fast) |

### 6.1.1. 재고 데이터 조회 아키텍쳐: Real-time gRPC with ALB

초고변동성 데이터를 다루며, 데이터 불일치가 곧 오판매(Overselling)로 이어지는 핵심 시스템입니다.

- **Challenge (제약 사항):**

  - **High Volatility & SPOF:** 재고는 빠르게 변하여 캐싱이 불가능하며, 부정확한 재고 정보로 Promise를 계산할 경우 치명적인 비즈니스 결함이 예상됩니다.
  - **Fan-out Overhead:** PLP 진입 시 수십 개 상품을 동시 조회해야 하므로 REST API로 조회 시 헤더 오버헤드나 조회하는 데이터의 크기가 병목이 됩니다.
  - **Sticky Connection:** gRPC의 장기 연결 특성상 특정 파드에 부하가 집중될 위험이 있습니다.
  - **Re-balancing 한계:** Client-side LB는 이미 연결된 connection에 대해 re-balancing을 수행하지 않아, scale-out 시 새 팟에 트래픽이 분산되지 않습니다.
- **Serving Strategy (조회 전략):**

  - **Direct RPC Call (Brokerless):** Redis나 메시지 브로커를 거치지 않고 Inventory 서비스와 gRPC와 Protocol Buffer를 사용해 직접 통신하여 Latency를 최소화합니다.

    - Protocol Buffer의 고압축 바이너리를 통해 fan-out 상황의 대용량 데이터 크기로부터 오는 latency 문제를 해결합니다.
    - 빠르게 실시간 조회 함으로서 Caching으로 인한 데이터의 정합성 오류를 해결합니다.
    - gRPC를 선택함으로서 고 TPS 구간에서 tail latency의 안정화를 기대합니다.
  - **Server-side L7 Load Balancing (ALB):** K8s 내부 ALB를 통해 gRPC 요청을 자동 분산하며, 증설 순서와 무관하게 트래픽을 재분배합니다.

    - ALB가 Server-side load balancing을 수행하여 Inventory pod 간 트래픽 균등 분산
    - Scale-out 시 즉시 새 팟에 트래픽 분산 (Re-balancing 자동화)
    - Promise와 Inventory 독립적 증설 가능 (증설 순서 의존성 제거)
- **Data Synchronization (데이터 동기화):**

  - 별도의 동기화 저장소를 두지 않고, 원천 시스템(Core Inventory)의 상태를 실시간으로 조회합니다.
  - 따라서 동기화 메커니즘은 별도로 필요하지 않습니다.
- **Consistency Guarantee (정합성 목표):**

  - 항상 최신의 물리 재고 상태를 조회함을 보장합니다.
- **Key Technology (기술 스택):**

  - **Protocol:** gRPC over HTTP/2 (Multiplexing).
  - **Serialization:** Protobuf v3 (High-performance serialization).
  - **Load Balancer:** K8s 내부 ALB (gRPC protocol support)
- **Resilience & Fallback (장애 대응):**

  - **Fail-fast:** 재고 조회 실패 시 **Hard Failure** 상태로 간주하며 추측성 응답을 하지 않고 즉시 **에러를 반환**합니다. 품절 상태로 내려주면 일반 서비스 상황과 구별되지 않으므로, 서비스 불능 상태를 명확히 구분합니다.
  - **Infra Protection:** 연속 에러 발생 시 Circuit Breaker가 작동하여 해당 파드를 제외하며, 일시적 오류는 40ms 예산 내에서 투명하게 재시도(Retry)합니다.

### 6.1.2. 상품 속성 조회 아키텍쳐: real-time call with UDH

변경 빈도가 낮고 데이터 양이 방대한(26M) 상품 메타데이터를 전사 공통 데이터 허브인 **UDH**를 통해 조회하여, 데이터 복제 비용을 절감하고 정합성을 극대화하는 전략입니다.

- **Challenge (제약 사항):**

  - **Data Silo & Redundancy:** 여러 마이크로서비스가 유사한 상품 데이터를 개별적으로 복제하여 관리함에 따른 운영 비용 및 스토리지 낭비가 발생합니다.
  - **SLA 부재:** 개별 시스템별로 복제된 데이터의 가용성 및 정합성 보장 수준이 불분명합니다.
  - **Latency Constraint:** 원천 API(Core Catalog)는 Promise의 성능 목표(P99 50ms)를 직접 지원하기에 응답 지연이 큽니다.
- **Serving Strategy (조회 전략):**

  - **UDH Data Serving Layer 활용:** Promise 계산에 필수적인 속성(MFS\_Flag, Country\_Codes, Policy\_ID 등)을 UDH의 읽기 최적화 저장소(Data Serving Layer)로부터 직접 조회합니다.
  - **Standardized API & Bulk Fetch:** UDH가 제공하는 표준화된 API를 사용하며, 다건 조회 시 Single-Hop 수준의 성능을 보장받을 수 있도록 UDH 내부 캐시 레이어를 활용합니다.
- **Data Synchronization (데이터 동기화):**

  - **Centralized Pipeline:** Promise 시스템이 직접 Kafka를 구독하는 대신, UDH가 중앙에서 Source of Truth(Core Catalog)의 변경 사항을 감지하여 통합 관리합니다.
  - **UDH 자동 갱신:** 전사 공통 데이터 파이프라인을 통해 Promise 전용 저장소 없이도 최신 데이터를 공급받습니다.
- **Consistency Guarantee (정합성 목표):**

  - **Near-Real-Time (NRT):** 원천 데이터 변경 후 UDH 서빙 레이어 반영까지 \*\*10초 이내(P99)\*\*의 지연 시간을 보장받아 기존 목표(5분) 대비 정합성을 크게 개선합니다.
- **Key Technology (기술 스택):**

  - **Interface:** UDH Standardized API (gRPC/REST)
  - **Storage (UDH Internal):** Common Data Storage (Primary-Replica or Cluster)
  - **Serialization:** Protobuf (성능 및 페이로드 최적화 필요 시 UDH와 협의)
- **Resilience & Fallback (장애 대응):**

  - **Soft Failure 처리:** UDH 장애 또는 타임아웃(20ms) 발생 시, 주문을 차단하지 않고 즉시 **Default Promise**를 반환하여 비즈니스 연속성을 유지합니다.
  - **Circuit Breaker:** UDH API의 에러율이 임계치를 초과할 경우 회로를 차단하여 시스템 연쇄 장애를 방지합니다.

### 6.1.3. Logistics Configuration 조회 아키텍쳐: Redis Cluster with Bulk Fetch

FC별 운영 정책(Cutline, ShippingOffer)을 관리하며, 모든 Promise 계산 요청마다 필수로 참조되는 **Hot Path**입니다.

- **Challenge (제약 사항):**

  - **Legacy Dependency:** 외부 시스템(배송팀 DB)의 안정성을 완벽히 통제할 수 없습니다.
  - **Hot Path:** 모든 계산 요청마다 N개 FC의 설정을 조회해야 하므로 초저지연이 요구됩니다.
  - **데이터 크기 불확실:** 실측 전까지 정확한 크기를 알 수 없어 Local Cache 리스크 판단 어려움.
- **Serving Strategy (조회 전략):**

  - **Redis Cluster with Bulk Fetch:** Sync Worker가 DB 데이터를 Redis로 동기화하고, 앱은 Redis만 조회합니다.

    - **MGET 사용:** N개 FC 데이터를 1회 네트워크 호출로 일괄 조회 (Loop 조회 금지)
    - **데이터 크기 무관:** Redis는 데이터 크기와 무관하게 안정적으로 동작
    - **전환 용이:** 추후 데이터 크기 실측 후 Local Cache 전환 가능
- **Data Synchronization (데이터 동기화):**

  - **Sync Worker (K8s CronJob):** Data Mart DB → Redis로 주기적 동기화
  - **주기:** 5분 또는 변경 감지 시
  - **방식:** Full Refresh 또는 Delta Sync
- **Consistency Guarantee (정합성 목표):**

  - **Eventual Consistency (< 5 min):** 운영 정책 변경 시 5분 이내 전파를 목표로 합니다.
- **Key Technology (기술 스택):**

  - **Serving Layer:** Redis Cluster (Master-Slave Replication)
  - **Connection:** Lettuce Connection Pool (Timeout: 10ms)
- **Resilience & Fallback (장애 대응):**

  - **Soft Failure:** Redis 조회 실패 시 DB fallback 없이 **Default Promise**를 반환합니다.

    - 부분 데이터로 응답하거나 해당 항목 제외
    - 전체 시스템 안정성 우선

### 6.1.4. Strategy 조회 아키텍쳐

물리적 제약(재고, 물류)과 무관하게 비즈니스 목적(프로모션, 재해 방어 등)에 따라 약속을 조정하는 '두뇌' 역할을 하는 시스템입니다.

- **Challenge (제약 사항):**

  - **Rule-Based Execution:** 단순 데이터 조회가 아니라, 조건(Condition)과 행위(Action)로 이루어진 규칙을 메모리상에서 평가해야 합니다.
  - **High Risk:** 특정 지역 출고 제한(예: 폭설로 인한 강원도 배송 불가) 같은 방어 전략이 누락될 경우, 물리적으로 가능하더라도 비즈니스적으로 불가능한 약속을 노출하게 됩니다.
  - **Unstructured Data:** 정형화된 스키마보다는 다양한 조건의 조합으로 이루어진 비정형 데이터입니다.
- **Serving Strategy (조회 전략):**

  - **Fetch Once, Evaluate Many:** Strategy는 사전에 적재하고, 요청 시 **네트워크 호출 없이 메모리 평가**
  - **Context-Based Matching:** region, platform, customer type, event tag 등 문맥 기반 적용
  - **Non-Blocking Path:** Promise Hot Path에서 Strategy 조회로 인한 대기 금지
- **Data Synchronization (데이터 동기화):**

  - **[추후 설계]** 현재 Strategy 에 대한 구체적 요구사항이 없으므로, 확장 시 별도 설계 예정입니다.
  - **In-Memory Snapshot:** Promise 애플리케이션 로컬 메모리에 Read-only 적재
- **Consistency Guarantee (정합성 목표):**

  - **Eventual Consistency:** 정책 반영 지연 최대 5분 허용
- **Key Technology (기술 스택):**

  - **Storage:** Application In-Memory
- **Resilience & Fallback (장애 대응):**

  - **Hard Failure:** Strategy는 In-memory로 동작하므로 별도 장애 대응이 없습니다. Strategy 데이터 누락 시 비즈니스적으로 불가능한 약속을 제공할 수 있어 **서비스 불능 상태**로 처리합니다.

---

## 6.2. Promise 산출 근거 추적성 아키텍처: Hash-based Audit Strategy

> **[추후 설계]** 현재 MVP 범위에서 제외합니다. 새로운 저장소(NoSQL, Object Storage) provisioning에 따른 복잡도 증가 대비 현 시점의 비즈니스 임팩트가 제한적이라고 판단했습니다. MVP 단계에서는 기존 OpenSearch 기반 로그 인프라를 활용하여 디버깅 용도로 운영하고, 추후 요구사항이 구체화되면 아래 설계를 기반으로 전용 아키텍처를 구축합니다.

특정 시점의 배송 약속(Promise)이 어떤 데이터와 로직에 의해 산출되었는지 사후에 역추적하기 위한 아키텍처입니다. 메인 API의 Latency에 영향을 주지 않기 위해 **비동기 스냅샷 포인터 저장 방식**을 채택합니다.

- **Challenge (제약 사항):**

  - **Performance Isolation:** 초당 최대 114k TPS를 처리하는 메인 API의 응답 속도(10ms~50ms)에 기록 로직이 영향을 주어서는 안 됩니다.
  - **Data Volatility:** 상품(Catalog) 및 물류(Logistics) 데이터는 5분 단위로 변경되므로, 조회 시점의 버전 정보가 없으면 사후 복기가 불가능합니다.
  - **Storage Cost:** 모든 요청을 전수 저장할 경우 발생하는 막대한 인프라 비용과 쓰기 부하를 관리해야 합니다.
- **Tracing Strategy (추적 전략):**

  - **차등 샘플링 (Differentiated Sampling):** 서비스 중요도에 따라 저장 비중을 조절하여 리소스를 최적화합니다.

    - **PLP (상품 목록):** 통계적 분석을 위해 0.1% 확률적 샘플링 적용.
    - **PDP/장바구니:** CS 대응을 위해 1~5% 중비중 샘플링 적용.
    - **주문서 작성:** 결제와 직결된 '계약' 단계이므로 100% 전수 기록.
  - **비동기 기록 (Asynchronous Logging):** 메인 로직 응답 후, 별도 스레드에서 Hash화된 Audit Key만 저장소에 기록하여 사용자 응답 지연을 방지합니다.
- **Data Model (Audit Hash 구조):**

  - 단순 결과값이 아닌, 산출에 사용된 데이터의 \*\*'포인터(ID/Version)'\*\*를 조합하여 저장합니다.

    - **Audit Hash:** Catalog 버전, Logistics 정책 ID, Strategy ID 리스트 등을 조합한 Hash 값.
    - **Trace ID:** 요청 전체를 식별하는 고유 UUID.
    - **Result Snapshot:** 최종 산출된 PSD(출고예정일) 및 PDD(도착예정일).
- **Key Technology (기술 스택):**

  - **Ingestion:** Kafka를 통한 비동기 로그 수집.
  - **Short-term Storage:** Document 기반의 **NoSQL(DynamoDB)** - 78k TPS 이상의 초고속 쓰기와 TTL(Time-To-Live) 기능을 통한 단기 데이터 관리.
  - **Long-term Archiving:** **Object Storage (S3)** - 전수 로그 장기 보관 및 분석용(Athena 활용).
- **Resilience & Reliability (장애 대응):**

  - **Impact Isolation:** 추적 기록 저장소(DynamoDB 등) 장애가 발생하더라도 메인 Promise 계산 로직은 중단 없이 정상 응답을 반환합니다.
  - **Verification (Phase 2):** 향후 CS 비효율 증가 시, 응답에 Metadata(Hash)를 주입하고 주문 시점에 서버 계산값과 비교 검증하여 CS 발생을 원천 차단하는 방식으로 고도화합니다.

## 6.3. 공통 장애 대응 아키텍처

개별 시스템의 전략을 넘어, Promise 시스템 전체가 장애 상황에서 어떻게 생존할 것인지를 정의하는 **계층적 방어(Tiered Defense)** 구조입니다.


| **장애 등급** | **정의** | **판단 기준 (Threshold)** | **대응 및 가용성(SLA) 반영** |

| --- | --- | --- | --- |

| **Hard Failure** (가용성 장애) | 서비스가 불능이거나, 핵심 의존성(Inventory)이 실패한 상태 | **HTTP 5xx Error** > 1% (5분 평균) **Inventory 조회 실패** (전체) | **즉시 장애 간주** (SLA 차감)  **Fail-fast:** 재고 조회 실패 시 연산 중단 및 에러 반환 |

| **Soft Failure** (기능적 장애) | API는 정상 응답(200 OK)하나, 데이터 누락으로 **Default Promise**가 반환된 상태 | **Default Promise 반환율** ≥ **5%** (Critical Threshold) | **장애 간주** (SLA 차감) 5% 이상 대량 발생은 단순 오류가 아닌 시스템적 결함으로 판단 |

| **Degradation** (품질 저하) | 간헐적인 데이터 누락으로 Default Promise가 소량 반환된 상태 | **Default Promise 반환율** < **5%** (Warning Threshold) | **정상 가동 간주** (SLA 차감 X) 운영 알림(Alert)만 발송하여 데이터 수정 유도 |

- **의존성 시스템별 장애 대응 매트릭스 (Dependency Failure Matrix)**


| **의존 시스템** | **데이터 특성** | **실패 시 Promise 시스템 상태** | **대응 전략 (Action)** | **근거** |

| --- | --- | --- | --- | --- |

| **Inventory** | 실시간성 필수, 초고변동성 | **Hard Failure (장애)** | **Fail-fast** 또는 **전면 차단** | 재고 정보가 없으면 배송 약속 자체가 성립 불가. SPOF로 규정 |

| **Catalog** | 불변에 가까움, Read-Heavy | **Soft Failure (저하)** | 즉시 **Default Promise** 반환 | 데이터 변경이 드물어 보수적 값으로 방어 가능 |

| **Logistics Config** | 변경 빈도 낮음 | **Soft Failure (저하)** | 즉시 **Default Promise** 반환 | 컷라인/비용 정보 누락 시 보수적 값으로 방어 |

| **Strategy** | 비정형 규칙 | **Hard Failure (장애)** | **Fail-fast** 또는 **전면 차단** | 비즈니스 전략 누락 시 실현 불가능한 약속 제공 위험 |

- **장애 판단을 위한 복합 지표(Composite Metrics) 도입**

  - **Availability (가용성):** `(전체 요청 - (Hard failure + Soft failure)) / 전체 요청`
  - **Quality (품질):** `Default Promise 반환 건수 / 전체 성공 응답`
- **Circuit Breaker 및 Fallback 정책**

  - **Inventory (SPOF):** Circuit Open 시 **Fail-fast**. 배송 약속 계산을 중단하고 즉시 장애를 전파합니다.
  - **Catalog / Config:** Circuit Open 시 **Fallback 모드** 진입. 즉시 **Default Promise**를 반환하여 주문 흐름을 유지합니다.
  - **Strategy:** Circuit Open 시 Fail-fast. 보장 불가능한 Promise를 제공하는 것을 막기 위해 즉시 장애를 전파합니다.

## 6.4. 사전에 정의된 보수적 Promise

- 각종 예외나 시스템 failure로 인한 Promise의 비정상 상태에서 서비스의 중단을 막기 위해 fallback으로 제공할 default Promise의 값을 의미합니다.
- 기존 Promise에서 Fallback으로 사용하던 값을 기반으로 작성
- fall-back Promise (TBU)

  - cutline

    - PSD : NOW + 3D (work day 기준)
    - PDD : PSD + 2D (work day 기준)
  - shippingOffer

    - shippingFee : 0
    - returnFee : 2500

# 7. Appendix

## 7.1. 참고 자료

1. [Promise Requirement](https://wiki.team.musinsa.com/wiki/spaces/PRODUCTS/pages/235013662/Core+Promise+System?atl_f=PAGETREE)
2. [Promise Inventory data fetch 전략](/wiki/spaces/PRODUCTS/pages/253100901/Promise+Inventory+data+fetch)
3. [Promise Catalog data fetch 전략](/wiki/spaces/PRODUCTS/pages/235014473/Promise+Catalog+data+fetch)
4. [Promise Cutline/ShippingOffer data fetch 전략](/wiki/spaces/PRODUCTS/pages/252675928/Promise+Cutline+ShippingOffer+data+fetch)
5. [Promise 산출 근거 추적성 및 신뢰도 확보 전략](/wiki/spaces/PRODUCTS/pages/256153404/Promise)
6. [기존 Promise 시스템에서 사용하던 default promise](/wiki/spaces/claim/pages/202245814/Promise+API)