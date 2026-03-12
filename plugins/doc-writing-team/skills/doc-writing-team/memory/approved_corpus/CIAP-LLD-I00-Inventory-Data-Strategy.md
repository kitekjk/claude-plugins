# CIAP: LLD (LLD-I00. Inventory Data Strategy)

> **Page ID**: 221390862

---

|  |  |

| --- | --- |

| Author | [백현우/Core-E Catalog Platform hyunwoo.baig](https://wiki.team.musinsa.com/wiki/people/712020:4df62b90-4355-4159-b3c0-4ee30ff6451d?ref=confluence) |

| Review Date | 2026. 1. 8. |

| Reviewers | - [김대일/Core Engineering irondikim](https://wiki.team.musinsa.com/wiki/people/712020:9e7487b6-e6a2-43f7-bd35-d5da8eabc0f6?ref=confluence) - [박현준/Core-E Catalog Platform hyunjun.park](https://wiki.team.musinsa.com/wiki/people/712020:c4cfe18d-d170-4bb7-a4d7-55b96c4087b3?ref=confluence) - [김도영/Core-E Catalog Platform doyoung.kim](https://wiki.team.musinsa.com/wiki/people/712020:63a3bfba-b8b3-4a2f-b1b4-d41160a57469?ref=confluence) - [류욱상/Core-E Catalog Platform wooksang.ryu](https://wiki.team.musinsa.com/wiki/people/712020:f5ce9f79-b8c5-4bdd-a278-f9e5750a3e06?ref=confluence) - [황두리/Core-E Catalog Platform duri.hwang](https://wiki.team.musinsa.com/wiki/people/712020:8aa04b59-9c5b-432b-b616-58e0017684cc?ref=confluence) - [김지환/Core-E Catalog Platform jihwan.kim2](https://wiki.team.musinsa.com/wiki/people/712020:e4f6daa8-4c8c-4273-8ba6-77173f6f1109?ref=confluence) - [정규택/Core-E Catalog Platform kyutaek.jung](https://wiki.team.musinsa.com/wiki/people/712020:663cf68a-5f24-480d-8345-e43508f9a9d5?ref=confluence) |

| On this page |  |

# 용어


|  |  |

| --- | --- |

| **용어 (Term)** | **상세 정의 (Description)** |

| **Inventory (통합 재고)** | 물리적 재고(Stock)와 논리적 한도(Slot)를 모두 포함하는 **최상위 집합체(Aggregate Root)**.  **단일 Document**로 관리되며, 트랜잭션의 경계(Scope)가 됩니다. |

| **Slot** | 물리적 재고(SKU Quantity)와는 독립적으로 관리되는 판매 허용 수량의 상한선(Logical Upper Limit)   - <https://wiki.team.musinsa.com/wiki/x/-Q6zD> |

| **SKU (Stock Keeping Unit)** | 물류 센터에서 관리되는 식별 단위(= O-SKU). 시스템 내에서 통합 재고를 식별하는 유니크 키로 사용됩니다. |

| **ATS** | Available To Sell   - SLS에서 CIAP로 연동하는 가용재고 |

| **ATP** | Available to Promise   - CIAP에서 계산하는 판매가능재고 - min( ATS - 선점재고 , Slot.limit - 선점재고 ) = ATP |

---

# 문제 정의

고성능 처리를 위해 도입했던 이중화된 저장소 구조(Redis + DB)와기존 도메인 모델이 글로벌 확장과 멀티 플랫폼이라는 비즈니스 목표를 수행하는 데 있어 기술적 부채로 작용하고 있습니다. (상태 불일치와 구조적복잡성의 한계)

이에 따라 데이터 정합성(Consistency)과 운영 유연성(Business Agility)을 동시에 확보할 수 있는 새로운 아키텍처로의 전환이 필요합니다.


|  |  |  |

| --- | --- | --- |

| **Problem** | **Root Cause** | **Impact** |

| **논리적 재고 분할 불가능** | **재고의 물리적 파편화**  단일 재고 Pool 내에서 판매 채널(무신사, 29CM)이나 목적(일반, 특가)에 따라 수량을 제한하는 기능(Slot)이 부재함. | **판매 유연성 저하**  특정 채널에 할당된 재고가 안 팔려도 타 채널에서 끌어다 쓸 수 없음. 급격한 트래픽 변동이나 프로모션 상황에 유연하게 대응 불가. |

| **신뢰할 수 없는 데이터 정합성** | **이중 저장소(Dual-Store) 아키텍처**  Redis(선반영)와 DB(후반영)가 분리되어 있고 비동기(Kafka)로 연결됨. 장애 발생 시 시점 차이(Lag)로 인해 두 저장소 간 상태 불일치(State Drift)가 필연적으로 발생함. | 시스템 상 재고가 남아있음에도 주문이 불가능하거나, 반대로 재고가 없는데 주문이 되는 현상 발생. 장애 복구 시 "어느 데이터가 맞는가?"를 판단할 수 없음. |

| **복구 불가능한 데이터 오염** | **상태 동기화의 단방향성**  Redis 데이터 휘발 시 DB 데이터를 다시 로드해야 하나, DB가 최신 상태가 아닐 수 있어(Lag) **기준 데이터(Base Data)를 확정할 수 없는 딜레마** 존재. | **원자적 검증 메커니즘 부재**  실제 가용 재고보다 많은 주문을 접수받게 되어, 사후 **강제 주문 취소** 처리로 인한 고객 신뢰도 하락 및 보상 비용 발생. |

| **운영 복잡도 및 장애 전파** | **과도한 컴포넌트 의존성**  단순 재고 차감을 위해 Redis, Lua, Kafka, Consumer, DB 등 너무 많은 컴포넌트가 관여함. | **높은 운영 비용 및 장애 빈도 증가**  포인트 장애(Point Failure) 지점이 많아 장애 전파가 쉽고, 데이터 보정(Reconciliation)을 위한 수동 운영 리소스가 지속적으로 투입됨. |

---

# 기능/비기능 요구사항

상세 내용은 <https://wiki.team.musinsa.com/wiki/x/jhHuDQ> 참조

## 1. Functional Requirements

데이터 모델링(Schema Design)과 트랜잭션 경계(Transaction Boundary)를 결정짓는 부분입니다. 특히 재고의 ‘선점' 로직이 물리/논리적으로 분리되어 있어 원자성 보장이 필수적입니다. 아래 기능적 요구사항을 충족하는 데이터 전략이 필요합니다.


|  |  |

| --- | --- |

| **기능 항목** | **상세 요구사항 (Workflow & Logic)** |

| **재고 선점** | - **Transaction Scope:** `Stock`(물리 재고) + `Slot`(논리 할당) + `Allocation`(주문 내역) 생성이 All-or-Nothing으로 처리되어야 함. - **Validation:** 선점 시 `물리 가용량`과 `슬롯 잔여량`을 동시에 만족해야 함. - **Concurrency:** Hot SKU(이벤트 상품)에 대한 락 경합을 최소화하며 동시성 제어가 필요함. |

| **재고 선점 해제/취소** | - **Atomic Restore:** 선점 해제 시 `Inventory` 수량 변경(Stock/Slot)과 `Allocation` 상태 변경이 All-or-Nothing으로 처리되어야 함. |

| **재고 조정 (Adjustment)** | - **Scope:** 재고 총량을 조정할 때, 진행 중인 주문(Reserved)에는 영향을 주지 않고 전체 수량(Total)만 변경해야 함. |

## 2. Non-Functional Requirements


|  |  |  |

| --- | --- | --- |

| **카테고리** | **항목** | **목표치/요구사항** |

| **Consistency** | **Transactional Consistency** | - **Consistency:** 재고 선점/해제/조정 등 Write 작업에 대해 **강력한 데이터 정합성** 보장 (Partial Success 불허). - **Isolation:** 재고 부족 시 DB 레벨에서 즉시 거부(Fail-fast)하여 애플리케이션 부하 감소. |

| **Throughput** | **Write Throughput** | - **Target:**    - **평상시: 80 TPS**   - **피크: 1,000 TPS 이상** (이벤트/선착순 상황 대비). - **Hot Key Strategy:** 특정 SKU에 트래픽이 집중될 때 DB Lock 경합을 최소화하는 전략 필요 (e.g. Redis Pre-decrement 후 Async DB Write 고려 등). |

| **Throughput** | **Read Throughput** | - **Target:**    - Source of Truth      - **평상시: 160 TPS**     - **피크: 2,000 TPS 이상** (DB 직접 조회)   - Materialized View (fyi. Read MV는 별도 LLD에서 더 상세히 다룸)      - 평상시: 12000 TPS     - 피크: 140000 TPS - **Strategy:** Promise 계산이나 전시 영역은 Master DB가 아닌 Materialized View(MV)나 Read Replica를 바라보도록 설계. |

| **Latency** | **DB Latency** | - **Read: P95 30ms** - **Write:** P95 **20ms**    - API SLO 50ms 보장을 위해 최대 30ms를 SLO로 정의 |

| **Scalability** | **Data Growth** | - **Capacity:** 데이터 **10배 증가** 시에도 아키텍처 변경 없이 대응 가능해야 함 (Sharding 또는 Partitioning 고려). |

| **Auditability** | **Audit Log** | - **Immutability:** 모든 변경(선점, 해제, 조정 등)에 대해 **100% 불변 로그**를 기록해야 함. - **Traceability:** 주문번호, SKU, 날짜 등으로 역추적 가능해야 함. |

---

# Goal, Non-Goal

## Goal

이 문서를 통해 해결하고자하는 목표입니다.

- Core Inventory에서 필요한 핵심 기능을 정의합니다.
- Core Inventory의 핵심 기능에 필요한 도메인을 설계합니다.
- Core Inventory의 핵심 기능을 충족하는 DB를 결정합니다.
- 결정된 DB와 도메인 디자인을 통해 핵심 기능을 어떻게 충족하는지 작성합니다.

## Non-Goal

이 문서에서는 다루지 않는 목표입니다.

- Core Inventory의 API Interface에 대한 부분은 다루지 않습니다.
- Core Inventory의 Mapping&Relation 관련된 부분은 <https://wiki.team.musinsa.com/wiki/x/YwAdDw> 에서 다룹니다.
- Core Inventory의 가용 재고 조정 이벤트 파이프라인에 대한 부분은 별도의 LLD에서 다룹니다.
- Core Inventory의 상품/옵션별 재고 데이터 제공을 위한 부분은 별도의 LLD에서 다룹니다.
- Core Inventory의 핵심 기능에 대한 상세한 워크플로는 별도의 LLD에서 다룹니다.
- Data Migration, Verification, Integration Process, Reconciliation 등의 대한 부분은 별도의 LLD에서 다룹니다.

---

# 제안하는 디자인

## Data Storage Strategy & Technical Decision

[ADR: DB](/wiki/spaces/PRODUCTS/pages/187206528/ADR+DB#ADR-DB001%3A-Inventory-DB) 에 기반하여 데이터베이스를 선정.

<https://wiki.team.musinsa.com/wiki/x/8BaQDw> 에 따라 ScyllaDB를 추가 검토를 진행합니다.

### 1. DynamoDB 선정 배경 (Decision Drivers)

이커머스의 핵심인 재고 시스템으로서, **무한한 확장성**과 **예측 가능한 성능**을 보장 및 **대규모 데이터 처리**가 핵심 요구사항이다. 무중단 확장성(Scale-out)과 **데이터 정합성**을 동시에 만족해야 한다. 이를 위해 도메인 처리 모델로 Model C (No-Tx, Single Item Atomic Loop)를 채택하고, 이를 구현할 핵심 저장소로 **Amazon DynamoDB**를 선정한다.

#### 1-1. 쓰기 성능의 무한 수평 확장성 (Unbounded Write Scalability)

- **RDBMS의 한계 (Vertical Scaling Ceiling):**

  - 쓰기 트래픽 분산을 위해 샤딩(Sharding) 도입 시 라우팅 및 리밸런싱 로직 구현 등 애플리케이션 복잡도가 급증한다.
  - Scale-Up만으로는 물리적 한계에 도달하여, 초당 수만 건의 선착순 쓰기 요청을 감당할 수 없다.
- **MongoDB의 한계 (Scaling Performance Jitter):**

  - 샤딩을 지원하나, 노드 확장(Scale-out) 시 데이터가 이동하는 **청크 마이그레이션(Chunk Migration)** 과정이 필수적이다.
  - 제조사는 투명한 절차라 설명하지만, 실제 고부하 상황(Online Critical Path)에서는 이 리밸런싱 작업이 성능 지표에 영향을 주어 사실상의 장애(Latency Jitter)를 유발할 수 있다.
- **DynamoDB의 우위 (Zero-Ops Partitioning):**

  - 트래픽이나 용량이 임계치를 넘으면 내부적으로 파티션을 자동 분할(Splitting)하여 즉시 용량을 확보한다.
  - 데이터 물리 이동에 따른 대기 시간이나 성능 저하 없이 **선형적으로 무한 확장(Linearly Scalable)** 가능하여 인프라 병목을 원천 차단한다.

#### 1-2. 데이터 규모와 무관한 O(1) 성능 보장 (Predictable Performance)

- **RDBMS의 한계 (O(log N) Degradation):**

  - B-Tree 인덱스 구조로 인해 데이터가 수억 건으로 누적될수록 인덱스 깊이(Depth)가 깊어져 조회 및 쓰기 지연이 증가한다.
- **MongoDB의 한계 (Operations Overhead):**

  - 데이터가 많아질수록 밸런서(Balancer) 관리 및 인덱스 최적화 비용이 증가하며, 적절하지 않은 샤드 키 선정 시 특정 샤드에 부하가 집중되는 핫스팟 이슈가 발생할 수 있다.
- **DynamoDB의 우위 (Consistent Hashing & O(1)):**

  - 분산 해시 테이블(DHT) 구조를 기반으로 하여, 데이터가 1GB이든 100TB이든 상관없이 Partition Key 해싱을 통해 데이터 위치를 즉시 특정한다.
  - 데이터 규모와 무관하게 **항상 일정한 한 자릿수 밀리초(Single-digit ms) 응답 속도**를 보장한다.

#### 1-3. 고동시성 연결 처리 및 고가용성 (Concurrency & High Availability)

- **RDBMS의 한계 (Connection Exhaustion):**

  - Stateful TCP 연결을 맺으므로, 대규모 이벤트 시 `Max Connections` 제한에 도달하여 서비스 중단 위험이 크다.
- **MongoDB의 한계 (Write Downtime during Failover):**

  - 장애 발생 시 Replica Set이 새로운 Primary를 선출(Election)하는 동안(통상 수 초~12초) **쓰기 불가(Write Unavailability)** 구간이 존재한다.
  - 재고 시스템의 핵심인 주문 처리 경로에서 수 초간의 다운타임은 치명적이다.
- **DynamoDB의 우위 (Stateless & Zero Downtime):**

  - Stateless HTTP 통신을 사용하여 수만 개의 람다 인스턴스가 동시에 요청해도 연결 병목이 없다.
  - 완전 관리형 서비스로 장애 감지 및 복구 시 애플리케이션 관점에서의 쓰기 중단(Downtime)이 없다.

#### 1-4. 쓰기 경합 해소 및 트랜잭션 비용 (Contention Resolution)

- **RDBMS의 한계 (Locking Overhead):**

  - Row Lock 기반 제어는 대기 트랜잭션 증가 시 CPU 사용량 급증 및 데드락(Deadlock) 위험을 유발한다.
- **MongoDB의 한계 (Multi-Document Tx Cost):**

  - 샤딩 환경에서의 멀티 도큐먼트 트랜잭션은 높은 성능 비용을 유발한다.
  - 데이터 유실 방지를 위해 `WriteConcern: Majority`를 강제하면 Latency가 증가하여 고성능 목표와 상충된다.
- **DynamoDB의 우위 (Atomic Operations):**

  - `UpdateItem` API는 락 대기 없이 메모리 레벨 래치(Latch)만으로 원자적 연산을 수행한다.
  - PoC 결과, 트랜잭션 없이도 **1,000 TPS 이상의 고경합 상황에서 100% 처리율**을 달성함이 입증되었다.

### 2. 기술적 트레이드오프 (Trade-off Analysis)


|  |  |  |  |

| --- | --- | --- | --- |

| **구분** | **장점 (Pros)** | **단점/제약 (Cons)** | **해결 방안 (Mitigation)** |

| **성능** | **Microsecond 단위의 쓰기 속도**  Atomic Update로 락 대기 시간 최소화 | **Hot Partition 한계**  단일 파티션당 1,000 WCU 물리적 제한 존재 | 초대형 핫딜 상품의 경우 **별도 핫 파티션** 처리 검토 |

| **확장성** | **무한 수평 확장**  서버 관리 없이 트래픽에 따라 자동 확장 | **Throughput 비용**  프로비저닝 용량 초과 시 Throttling 발생 | **AWS SDK의 자동 재시도(Exponential Backoff)** 로직으로 유실 없이 처리 |

| **데이터 모델** | **Schema-less**  유연한 속성 추가 가능 | **복잡한 쿼리 불가**  Join 연산 미지원, 제한적 필터링 | **Read MV 별도 구성** |

| **정합성** | **단일 아이템 강한 정합성**  `UpdateItem` 시점의 데이터 무결성 보장 | **복합 연산 제약**  `qty - reserved >= order` 같은 수식 불가 | **애플리케이션 레벨 검증** 및 사후 **보상 트랜잭션(Rollback)** 프로세스로 해결 (Model C 검증 완료) |

| **운영** | **Fully Managed**  OS 패치, 샤딩, 복제 등 운영 요소 제로 | **모니터링 복잡성**  Hot Key 감지를 위한 별도 모니터링 필요 | CloudWatch Contributor Insights 활용하여 Hot Key 실시간 추적 |

---

## Domain Design

![image-20260108-062519.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/221390862/image-20260108-062519.png?version=1&modificationDate=1767853521001&cacheVersion=1&api=v2&width=721&height=693)


| **Domain** | **Description** |

| --- | --- |

| **Inventory** | Core Inventory System에서 관리하는 통합 재고의 단위. **단일 문서 내에서 물리 재고와 논리 슬롯의 가용량을 동시에 연산**합니다. 1P/3P 구분이나 FC 위치에 구애받지 않는 '컨테이너' 역할을 수행합니다.   - 역할    - 여러 판매 채널에 대한 통합 재고 관리를 지원합니다.   - 여러 SellerItem에 대한 통합 재고 관리를 지원합니다.   - 여러 FC로 분리된 동일한 무신사SKU에 대한 통합 관리를 지원합니다.   - 1P/2P 재고와 3P 재고의 통합 관리를 지원합니다. - 주요 속성    - stockBuckets: 물리 재고 보관함 (Map). Key에 위치(FC)와 성격(1P/3P)을 포함하여 다양한 형태의 재고를 격리 보관합니다.   - slotBuckets: 논리 슬롯 보관함 (Map). 판매 채널이나 프로모션 단위로 한도를 설정하며, Tag를 통해 검색 및 용도를 구분합니다.   - skuId: 물리적 물성 ID (1P는 필수, 3P는 Optional) |

| **StockBucket** **(Embedded Value)** | 물리적 위치(FC)와 관리 주체(1P/3P)별로 실물 재고 수량을 관리하는 최소 보관 단위입니다. Inventory 내 N개가 존재할 수 있습니다.   - 역할    - 실제 가용 수량은 관리합니다.   - FC 별로 분리될 수 있습니다.   - 하나의 Inventory 내에서 물리적으로 분리되어야 하는 재고를 개별적으로 관리합니다. 실물 수량(`availableToSellQuantity`)과 선점 수량(`reservedQuantity`)을 보유하며, 물리적 가용량 계산의 원천이 됩니다. - 주요 속성    - locationCode: 재고가 위치한 물리적 장소 식별자 (e.g. FC 코드)   - manageType: 재고 관리 주체 (1P: 자사 직접 관리, 3P: 파트너 관리)   - availableToSellQuantity: 현재 보유 중인 실물 총량   - reservedQuantity: 주문에 의해 선점되어 출고 대기 중인 수량   - remainingQuantity: `quantity - reserved` |

| **SlotBucket** **(Embedded Value)** | 특정 판매 목적이나 채널을 위해 설정된 논리적 판매 한도(Limit) 관리 단위입니다.   - 역할    - 판매 채널이나 이벤트별로 한정 수량을 관리합니다.   - 물리적 재고와 관계없이, 판매 가능한 최대 한도(Limit)를 설정합니다. 물리 재고가 많아도 슬롯 한도가 차면 품절 처리됩니다. - 주요 속성    - limitQuantity: 해당 슬롯에 할당된 최대 판매 가능 수량 (Capacity)   - tags: 슬롯의 용도나 특성을 정의하는 태그   - reservedQuantity: 해당 슬롯을 통해 들어온 주문의 현재 선점 수량   - remainingQuantity: `limit - reserved` |

| **Allocation** | 현재 유효한 주문에 의해 선점 중인 상태를 나타내는 정보입니다.   - 역할    - 주문(`orderId`)과 재고(`inventoryId`), 그리고 사용된 자원(`stockKey`, `slotKey`) 간의 연결 고리입니다.   - 주문 취소 시 이 문서를 찾아 선점을 해제(Rollback)하며, 출고 확정 시 상태를 `SHIPPED`로 변경합니다.   - `allocatedQty`: 현재 선점하고 있는 수량을 명시합니다. |

여기를 클릭하여 펼치기...

```
classDiagram
    direction LR

    namespace Resource_Domain {
        class Inventory {
            <<Collection>>
            String inventoryId PK "key"
            String skuId "SKU 식별자"

            String createdAt "생성일"
            String updatedAt "수정일"
            String deletedAt "제거일"

            Map~String, StockBucket~ stockBuckets
            Map~String, SlotBucket~ slotBuckets
        }

        class StockBucket {
            <<Embedded Value>>
            String stockId "Stock Key"
            String locationCode "Location Code"
            String manageType "1P | 3P"
            Number availableToSellQuantity "Available to Sell 수량"
            Number reservedQuantity "선점 수량"
            Number remainingQuantity "잔여 수량"

            %% 예정 재고 관련
            Number expectedDateTime "입고 예정일 - Timestamp"
        }

        class SlotBucket {
            <<Embedded Value>>
            String slotId "Slot key"
            Number limitQuantity "판매 한도"
            Number reservedQuantity "선점 수량"
            Number remainingQuantity "잔여 수량"
            List tags "검색/구분 태그"
        }
    }

    namespace Audit_State_Domain {
        class Allocation {
            <<Collection>>
            String allocationId PK "Partition Key | platform _ orderId _ inventoryId"
            String orderId "주문 번호"

            String inventoryId "역추적용"
            String skuId "역추적용"
            String stockId "Target Stock Map Key"
            String slotId "Target Slot Map Key"
            String locationCode "ex. FC_CODE"
            String tag "Platform | itemId | eventTag"
            
            String status "RESERVED | SHIPPED"
            Number allocatedQty "선점 수량"

            String createdAt "생성일"
            String updatedAt "수정일"
            String deletedAt "제거일"
        }
    }

    %% Relationships
    Inventory *-- StockBucket : Embedded
    Inventory *-- SlotBucket : Embedded
    Inventory "1" <-- "N" Allocation : Linked

    %% Styling
    style Inventory fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style StockBucket fill:#ffffff,stroke:#e65100,stroke-dasharray: 5 5
    style SlotBucket fill:#ffffff,stroke:#e65100,stroke-dasharray: 5 5
    style Allocation fill:#e1f5fe,stroke:#01579b,stroke-width:2px
```

---

## Index Strategy

### 1. Inventory

물리적 재고(Stock)와 논리적 판매 한도(Slot)를 모두 포함하는 통합 재고의 최상위 집합체(Aggregate Root)입니다.

- **Partition Key (PK):** `inventoryId` (String)

  - **구성:** 통합 재고 문서를 식별하는 고유 키 (ULID)
  - **접근 패턴:** `GetItem`, `UpdateItem`
  - **특징:** 물리적으로 가장 잘 분산되는 유니크 키입니다.
- **Sort Key (SK):** **None**

  - **이유:** 단일 아이템 접근이 주 목적이므로 복합 키 불필요.
- **Secondary Index:**

  - `GSI_Sku`(GSI 1)

    - **목적:** PBO에서 관리하는 물리적 식별 단위인 SKU를 기준으로 통합 재고 문서를 역추적하거나 조회하기 위한 필수 인덱스입니다.
    - **Index Name:** `GSI_Sku`
    - **Partition Key (PK):** `skuId`
    - **Sort Key (SK):** `inventoryId` (ULID)
- **참고:** `StockBucket`(물리 재고)과 `SlotBucket`(논리 슬롯)은 별도 테이블이 아닌 `Inventory` 문서 내의 **Embedded Map** 구조로 관리되므로, 별도의 PK나 GSI가 필요하지 않습니다.

**[샤딩 및 분산 전략]**

- **분산 기준:** `inventoryId`
- **동작 방식:**

  - DynamoDB는 `inventoryId`의 해시값을 계산하여 해당 값이 속하는 파티션에 데이터를 저장합니다.
  - `inventoryId`는 ULID를 사용하므로, 데이터가 특정 파티션에 쏠리지 않고 클러스터 전체에 매우 고르게 분산됩니다.

### 2. Allocation

주문 발생 시 재고 선점 상태와 그 이력을 관리하는 테이블입니다. 트랜잭션의 증거이자 감사 역할을 수행합니다.

- **Partition Key (PK):** `allocationId`

  - **타입:** `String`
  - **구성:** `{platform}_{orderNo}_{inventoryId}` (예: `MSS_ORD1023_INV001`)
  - **선정 이유:**

    - 주문 번호와 상품을 조합하여 유일성(Uniqueness)을 보장합니다.
    - `PutItem` 시 `attribute_not_exists(allocationId)` 조건을 걸어 **중복 선점을 원천 차단**하는 핵심 키입니다.
- **Sort Key (SK):** **없음 (None)**

  - **이유:** `allocationId` 자체가 유니크하므로, 복합 키를 써서 검색할 필요가 없습니다. 단건 조회(`GetItem`) 성능이 가장 빠릅니다.
- **Secondary Index:**

  - `GSI_Inventory_Status` (GSI 1)

    - **목적:** 증분 대사 - 특정 인벤토리에 어떤 주문들이 선점되어 있는지 역추적(Traceability)하기 위한 인덱스입니다.
    - **Index Name:** `GSI_Inventory_Status`
    - **Partition Key (PK):** `inventoryId`

      - **이유:** 특정 재고 ID(`inventoryId`)를 기준으로 묶어서 조회해야 합계(`Sum`)를 구할 수 있습니다.
    - **Sort Key (SK):** `status`

      - **이유:** 전체 내역을 다 가져오면 비효율적입니다. `status = 'RESERVED'`인 항목만 필터링(`Query`)하기 위해 사용합니다.
      - **쿼리 패턴:** `Query(PK=:invId, SK=:reserved)` → 결과의 개수(Count) 또는 수량 합산.
  - `GSI_Status_Date` (GSI 2)

    - **목적:** 대사 - 좀비 상태 정리
    - **Index Name:** `GSI_Status_Date`
    - **Partition Key (PK):**`status`

      - **이유:** 상태가 `RELEASING`인 것만 골라내야 합니다.
    - **Sort Key (SK):** `updatedAt`

      - **이유:** "10분 이상 지난" 건을 찾아야 하므로 **시간 범위 검색**이 필요합니다.
      - **쿼리 패턴:** `Query(PK='RELEASING' AND SK < :ten_mins_ago)`
  - `GSI_Order` (GSI 3)

    - **목적:** 주문 번호(`orderNo`) 하나만 가지고 그 주문에 딸린 모든 선점 내역을 조회할 수 있어야 합니다.
    - **Index Name:** `GSI_Order`
    - **Partition Key (PK):** `orderNo` (String)
    - **Sort Key (SK):** `inventoryId` (String)

**[샤딩 및 분산 전략]**

- **분산 기준:** `allocationId` (Base Table)
- **동작 방식:**

  - **데이터 지역성 (Locality)**

    - **Scatter (분산 저장):**

      - 한 주문(Order #100)에 속한 3개의 상품(A, B, C)이 각각 다른 PK(`..._InvA`, `..._InvB`, `..._InvC`)를 가지게 됩니다.
      - 따라서, 이 3개의 선점 내역은 물리적으로 **서로 다른 파티션에 저장될 확률**이 높습니다.
      - **장점:** 대량 주문 발생 시 쓰기 부하가 여러 파티션으로 분산되어 쓰기 성능(Write Throughput)이 극대화됩니다.
      - **단점:** "주문 #100의 모든 선점 내역 조회" 시에는 GSI(`orderNo`)를 타야 합니다.   
        (하지만 이는 읽기 패턴이므로 허용 가능합니다.)
  - **쓰기 분산 (Write Scalability):** `allocationId`는 개별 선점 건마다 고유하므로, 대량의 주문이 동시에 들어와도 쓰기 요청이 모든 파티션으로 골고루 분산되어 병목 현상을 방지합니다.
  - **읽기 패턴 (GSI 활용):**

    - "특정 주문의 모든 선점 내역 조회" 쿼리는 `orderId` GSI가 위치한 파티션으로 효율적으로 라우팅됩니다.

---

## Domain Object Lifecycle

### 1. Allocation Lifecycle (선점 내역)

`Allocation`은 주문의 흐름에 따라 가장 빈번하게 상태가 변경되는 객체입니다. 앞서 설계한 **중복 방지**와 **무트랜잭션 정합성**을 위해 상태가 중요하게 사용됩니다.

#### **State Definition**


|  |  |  |

| --- | --- | --- |

| **상태 (Status)** | **설명 (Description)** | **주요 트리거 & 액션** |

| **RESERVED** | (Initial State) Inventory 변경이 완료되어 정상적으로 선점된 상태. 주문이 유효하게 성립됨. | - **Trigger:** `Inventory` Atomic Decrement 성공 - **Action:** 주문 진행 가능 |

| **RELEASING** | 선점 해제(출고 또는 취소) 프로세스가 진행 중인 중간 상태. 이중 처리를 막기 위한 Lock 역할. | - **Trigger:** 선점 해제 요청 - **Action:** `Inventory` Atomic Increment/Decrement 수행 |

| **SHIPPED** | 상품이 출고되어 선점이 해제되고, 재고가 영구적으로 소진된 최종 상태. | - **Trigger:** 출고 완료 및 재고 처리 성공 - **Action:** 생명주기 종료 |

| **CANCELLED** | 주문 취소 등으로 선점이 무효화된 상태. | - **Trigger:** 취소 요청, Sweeper에 의한 정리 - **Action:** 보상 트랜잭션(재고 복구) 완료 후 종료 |

---

## DynamoDB Client Configuration Strategy

#### 1. Connection Pool (동시성 처리)


|  |  |  |  |

| --- | --- | --- | --- |

| **설정 항목** | **기본값 (Default)** | **리스크 (Risk)** | **설정 값** |

| **maxConcurrency** | **50** | **치명적.** 초당 수천 건의 주문이 몰릴 때, 51번째 요청부터는 클라이언트 내부 큐에서 대기하다가 `LeaseTimeout`으로 죽습니다. | **500 ~ 1,000** (부하 테스트 후 조정) |

| **connectionAcquisitionTimeout** | **10초** | 커넥션을 얻기 위해 10초나 기다리는 것은 재고 시스템에서 무의미합니다. 빨리 실패하고 재시도하는 게 낫습니다. | **1초 ~ 2초** |

#### 2. Timeouts (응답 속도 및 좀비 방지)

기본 타임아웃은 너무 길어서, 장애 발생 시 스레드 풀 고갈(Thread Starvation)로 이어져 서버 전체를 다운시킬 수 있습니다.


|  |  |  |  |

| --- | --- | --- | --- |

| **설정 항목** | **기본값 (Default)** | **리스크 (Risk)** | **설정 값** |

| **apiCallTimeout**  (총 요청 제한시간) | **Disabled (무한)** | **치명적.** 네트워크가 끊기거나 응답이 안 오면 스레드가 영원히 행(Hang)에 걸립니다. 앱 서버가 멈춥니다. | **2초** (빠른 실패) |

| **apiCallAttemptTimeout**  (개별 시도 제한시간) | **Disabled (무한)** | 재시도(Retry)를 포함한 개별 HTTP 요청이 무한정 대기할 수 있습니다. | **500ms ~ 1초** |

#### 3. Retry Strategy (재시도 전략)

Hot SKU 문제 해결을 위해 재시도 모드 변경이 필요합니다.


|  |  |  |  |

| --- | --- | --- | --- |

| **설정 항목** | **기본값 (Default)** | **리스크 (Risk)** | **설정 값** |

| **RetryMode** | **STANDARD** | 단순 지수 백오프만 수행합니다.  특정 파티션에 부하가 심할 때 클라이언트가 눈치 없이 계속 요청을 보내 **Throttling을 악화**시킵니다. | **ADAPTIVE**  (클라이언트 측 부하 조절)   - 요청 실패(Throttling) 감지 → "아, 서버가 힘든가 보네" → 클라이언트가 스스로 요청 발송 속도를 늦춤 |

| **maxAttempts** | **3회** | (적절함) 너무 많이 늘리면 전체 응답 시간(Latency)이 길어집니다. | **3회** (유지) |

---

## Domain Design Appendix.

### A. Data Schema Decision: Multi-Table Strategy

#### 1. Decision Summary

**물리적 테이블 분리(Multi-Table Strategy)** 를 최종 아키텍처로 채택한다. DynamoDB의 **Single Table Design** 전략(PK 공유 및 PK 분리 운영 포함)을 심도 있게 검토하였으나, 본 프로젝트의 핵심 목표인 "Core 로직의 성능 보호"와 "운영 명확성"을 위해 물리적 분리가 필수적이라고 판단하였다.

#### 2. Selected Schema


|  |  |  |  |

| --- | --- | --- | --- |

| **테이블 명** | **PK (Partition Key)** | **역할** | **트래픽 패턴** |

| **Inventory** | `inventoryId` | 실시간 재고 수량 관리 | **Update Heavy** (Hot Spot 발생) |

| **Allocation** | `allocationId` | 주문 선점 이력 | **Insert Heavy** (Random 분산) |

#### Alternatives Analysis

Single Table Design의 두 가지 패턴에 대해 각각의 기술적 리스크를 분석하고 배제한다.

**1. 패턴 A: PK 공유 방식 (Item Collection) 배제**

- **구조:** `Inventory`와 `Allocation`이 동일한 PK(`InventoryId`)를 공유.
- **배제 사유 (Critical): 파티션 쏠림 (Hot Partition)**

  - 재고 차감 트래픽과 주문 생성 트래픽이 단일 물리 파티션(1,000 WCU)으로 집중된다.
  - 두 부하가 합쳐져 Throttling 임계점에 조기 도달하므로, 시스템 최대 처리량을 스스로 제약하는 결과를 초래한다.

**2. 패턴 B: PK 분리 방식 (Shared Table with Distinct PKs) 배제**

- **구조:** 하나의 물리적 테이블을 사용하되, PK 패턴을 분리(`INV#id`, `ALLOC#id`)하여 데이터 분산 저장.
- **논리:** "어차피 PK가 다르면 분산되므로 파티션 쏠림 문제는 해결되지 않는가?"에 대한 반론.
- **배제 사유 (Major): 자원 간섭 및 이웃 소음 (Resource Coupling & Noisy Neighbor)**

  - **문제점:** 물리적 파티션은 분산되더라도, 테이블 전체의 프로비저닝 된 용량(Throughput)과 버스트 크레딧(Burst Credit)은 공유한다.
  - **리스크:** 대규모 이력 데이터(`Allocation`)에 대한 조회, 백업(Export), 또는 배치 작업으로 인해 테이블 전체의 IO가 급증할 경우, 전혀 상관없는 **재고 차감(**`Inventory`**) 트랜잭션까지 용량 부족으로 스로틀링**될 위험이 존재한다.
  - **기술적 팩트:**

    - DynamoDB의 `TransactWriteItems`는 대상 아이템들이 서로 다른 파티션에 위치할 경우, 테이블이 하나인지 둘인지와 무관하게 **2PC(Two-Phase Commit)** 프로토콜을 사용한다.
    - PK가 다른 재고와 할당 간의 트랜잭션은 **통합 테이블이라 해도 성능상 이점이 전혀 없다.**
  - **결론:** Core 비즈니스(재고)와 Non-Core 비즈니스(이력)의 자원을 물리적으로 격리(Isolation) 한다.

### B. DynamoDB Item Size Strategy

**목적:** Inventory 도큐먼트 내에 `Bucket`을 Embedded 구조로 설계함에 따라, DynamoDB의 단일 아이템 크기 제한(400KB)을 초과할 리스크가 있는지 정량적으로 검증한다.

**가정 및 제약 사항:**

- StockBucket: 최대 10개 미만 (일반적으로 FC는 3~5개 내외)
- SlotBucket: 최대 10개 미만 (일반 판매, 행사, 선물하기 등)

**사이즈 계산 (Estimation):**


|  |  |  |  |  |

| --- | --- | --- | --- | --- |

| **구성 요소** | **속성 내역 (Key + Value + Overhead)** | **개당 크기** | **Max 개수** | **합계** |

| **Header** | `inventoryId` (PK), `skuId` (GSI), Sys Overhead | 약 60 Bytes | 1 | **60 Bytes** |

| **StockBuckets** | Key, `locationId`, `manageType`, `qty`, `reserved` 등 | 약 50 Bytes | 10 | **500 Bytes** |

| **SlotBuckets** | Key, `limit`, `reserved`, `tags` 등 | 약 40 Bytes | 10 | **400 Bytes** |

| **Total** |  |  |  | **~ 960 Bytes** |

**결론:**

- 예상되는 최대 크기는 약 **1KB (960 Bytes)** 수준입니다.
- 이는 DynamoDB의 허용 한도인 **400KB 대비 약 0.25%** 수준으로, 매우 여유로운 용량을 확보하고 있습니다.
- 향후 FC가 확장되거나 슬롯 정책이 복잡해져 데이터가 10배 이상 증가하더라도, Embedded 구조를 유지하는 데 기술적 제약은 없습니다.

---

# 핵심 매커니즘

## 1. 재고 선점

재고 선점은 **"Dual-Condition Atomic Update (이중 조건 원자적 업데이트)"** 방식을 사용하여 수행됩니다. 단일 트랜잭션 내에서 물리 재고와 논리 슬롯이 모두 충족될 때만 선점이 성공하며, 어느 하나라도 부족할 경우 즉시 실패 처리됩니다.

PoC(Proof of Concept) 결과에 따라, 대규모 트래픽 및 Hot SKU 환경에서 최고의 성능과 안정성을 입증한 Model C (Application-Level Saga Pattern)를 재고 선점 아키텍처로 채택합니다.

Poc 진행 문서: <https://wiki.team.musinsa.com/wiki/x/G4O9Dg>

- **근거:** 1,000 VUs Hot SKU 테스트에서 100% 성공률 및 23,193 TPS 달성 , Oversell 테스트에서 오차 없는 무결성 입증.
- **고경합 성능 입증:** 시나리오 테스트 결과, 트랜잭션 기반의 Model A/B는 고경합(Hot SKU) 상황에서 `TransactionConflict`로 인해 성공률이 급락한 반면, Model C는 **100% 성공률 및 오버셀 0건**을 기록하며 안정성을 입증했다.
- **구조적 한계 극복:** Model A가 가진 DB 트랜잭션의 물리적 제한(Item 개수 등)을 Model C는 **단건 루프 처리**를 통해 구조적으로 우회한다.

### **1-1. 핵심 로직**

![image-20260106-084157.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/221390862/image-20260106-084157.png?version=1&modificationDate=1767688918138&cacheVersion=1&api=v2&width=524&height=894)

여기를 클릭하여 펼치기...

```
sequenceDiagram
    autonumber
    participant User as 👤 Promise API
    participant App as ⚙️ Inventory System
    participant RECIPE as 📜 InventoryRecipe
    participant INV as 🗄️ Inventory
    participant ALLOC as 📝 Allocation

    %% [Phase 0] Recipe Resolution
    rect rgb(240, 248, 255)
        Note over App, RECIPE: [Phase 0] 구성품 조회
        User->>App: 1. Reserve 요청<br>(OrderId, SKU, Qty, Tags)
        App->>RECIPE: 2. Get Recipe
        RECIPE-->>App: Component List<br>[{InventoryId, DeductQty}, ...]
    end

    %% [Phase 1] Read & Decision
    rect rgb(255, 250, 240)
        Note over App, INV: [Phase 1] 현재 상태 조회 (Snapshot)
        App->>INV: 3. Read Inventory State
        INV-->>App: Current State<br>• Stock.Available: 100<br>• Stock.Reserved: 50<br>• Slot.Available: 50
        
        App->>App: 4. Select Target & Calc
        Note right of App: • Calculate appliedQty<br>• Check Snapshot (Available >= Qty?)
    end

    %% [Phase 2] Saga Execution Loop
    rect rgb(245, 255, 245)
        Note over App, ALLOC: [Phase 2] Loop (Atomic Update)
        
        loop For Each Component
            
            %% 5. Atomic Update with Available
            App->>INV: 5. Atomic Update (Single Doc)
            Note right of INV: UPDATE (Atomic):<br>1. Stock.Available -= Qty<br>2. Stock.Reserved += Qty<br>3. Slot.Available -= Qty<br>4. Slot.Reserved += Qty<br><br>CONDITION:<br>Stock.Available >= Qty<br>AND Slot.Available >= Qty

            alt ✅ Update Success (Available 차감 성공)
                INV-->>App: OK (Updated)
                
                %% 6. Allocation Log
                App->>ALLOC: 6. Write Allocation Log
                
                alt ✅ Allocation Saved
                    ALLOC-->>App: OK
                    Note right of App: Proceed to Next Component
                
                else ❌ Write Fail / Timeout
                    ALLOC-->>App: Error
                    
                    %% 7. Immediate Compensation
                    Note over App, INV: ⚠️ Immediate Compensation
                    App->>INV: 7. Rollback Atomic Update
                    Note right of INV: ROLLBACK:<br>Stock.Available += Qty<br>Stock.Reserved -= Qty
                    INV-->>App: OK (Restored)
                    App-->>User: 500 System Error
                end

            else ❌ Update Fail (Available 부족)
                INV-->>App: Fail (Condition Not Met)
                
                %% Global Rollback
                Note over App, INV: 🔄 Global Rollback (Saga)
                loop For Previously Success Items
                    App->>INV: Rollback Atomic Update<br>(Available += Qty, Reserved -= Qty)
                end
                
                App-->>User: 409 Out of Stock
            end
        end
    end

    %% Final Response
    App-->>User: 200 OK (All Reserved)
```

데이터베이스의 무거운 트랜잭션(Lock) 대신, Atomic Counter(원자적 증감)와 보상 트랜잭션(Compensating Transaction)을 사용하여 재고의 정합성을 보장합니다.

#### 1-1-1. 재고 선점 프로세스 (Bulk Item Reservation)

"선차감 후검증 (Decrement-then-Check)" 방식을 사용하여 락 대기 시간을 제거합니다.

DB의 트랜잭션 제한(Transaction Limit)을 우회하기 위해 애플리케이션 레벨의 루프(Loop)로 처리합니다.

- **Request:** 재고 선점 요청 (Platform, ProductId, OptionId, Qty).
- **Read:** InventoryRecipe, Inventory 등을 조회합니다.
- **Iterate:** 주문 상품 리스트를 순회하며 개별 상품에 대해 **하위 프로세스**를 수행합니다.

  - **Dual-Condition Atomic Update (재고 차감):**

    - `Inventory` 도큐먼트에 대해 **단일** `UpdateItem` **연산**을 수행합니다.
    - **Condition (전제 조건):**

      - `stockBuckets[{fc}].remainingQuantity >= requestedQty` **AND**
      - `slotBuckets[{slot}].remainingQuantity >= requestedQty`
    - **Action (실행 내용):**

      - Stock: `reservedQuantity += qty`, `remainingQuantity -= qty`
      - Slot: `reservedQuantity += qty`, `remainingQuantity -= qty`
    - 이 과정은 DB 엔진(DynamoDB) 내부에서 원자적(Atomic)으로 수행되므로, Stock은 줄었는데 Slot은 안 줄어드는 불일치(Inconsistency)가 발생하지 않습니다.
  - **Allocation Insert (후 기록):**

    - 재고 차감이 성공하면, `Allocation` 테이블에 `RESERVED` 상태로 선점 이력을 저장합니다.
- **Compensation (실패 시 보상):**

  - 재고는 차감되었으나 `Allocation` 기록이 실패한 경우(Timeout 등), 즉시 보상 트랜잭션(Rollback)을 수행하여 재고를 원상복구합니다.
  - **Global Rollback:** 이미 성공(Case A)으로 기록된 상품들에 대해 역순으로 보상 트랜잭션(Atomic Increment)을 실행하여 전체 상태를 롤백합니다.

**1-1-2. 시나리오:** 재고(Total) 10개 중, 2개를 주문(선점)하는 경우


|  |  |  |  |  |  |

| --- | --- | --- | --- | --- | --- |

| **단계** | **동작 (Action)** | **Available (가용)** | **Reserved (선점)** | **Total (총재고)** | **비고** |

| **Initial** | - | **10** | 0 | 10 | 초기 상태 |

| **Reservation** | **Atomic Update**  (Available -= 2)  (Reserved += 2) | **8** | 2 | 10 | **트랜잭션 없이 단일 오퍼레이션으로 처리**  (Available >= 2 조건 필수) |

| **Fail/Rollback** | **Compensation**  (Available += 2)  (Reserved -= 2) | **10** | 0 | 10 | 할당 실패 또는 타 상품 재고 부족 시 원복 |

| **Ship** | **Outbound**  (Reserved -= 2)  (Total -= 2) | 8 | 0 | **8** | 출고 확정 시 (PBO 연동) |

### 1-2. Trade-off Analysis

#### 1-2-1. Pros (장점)

- **압도적인 성능 (Extreme Performance):**

  - 락(Lock) 경합이 없으므로 DB 파티션 성능을 100% 활용 가능합니다. PoC 기준 **23k TPS**를 기록하여 타 모델(A/B) 대비 약 1.5배 이상의 처리량을 보장합니다.
  - Hot SKU(1,000명 동시 접속) 상황에서도 평균 Latency 41ms로 쾌적한 응답 속도를 제공합니다.
- **완벽한 데이터 무결성 (Zero Oversell):**

  - Atomic Counter 동작 방식 덕분에 동시성 경쟁 상황에서도 정확히 재고 수량만큼만 판매되며, 오버셀(Oversell)이 원천 차단됩니다. (Oversell Test 결과: 100개 재고에 200명 접속 시 정확히 100개 판매, 100개 실패).
- **높은 가용성 및 확장성 (Availability & Scalability):**

  - `TransactionCanceledException`과 같은 DB 레벨의 충돌 에러가 발생하지 않으며, 트래픽 증가에 따라 선형적으로 확장 가능합니다.
- **검증된 자가 치유 능력 (Self-Healing):**

  - 시스템 장애나 강제 에러 상황(빌런 테스트)에서도 보상 트랜잭션을 통해 데이터가 100% 정합성을 유지하며 복구됨을 확인했습니다.

#### 1-2-2. Cons & Risks (단점 및 고려사항)

- **구현 복잡도 증가 (Complexity):**

  - DB가 보장해주는 트랜잭션(All-or-Nothing)을 사용하지 않으므로, 애플리케이션 레벨에서 Saga 패턴(성공/실패 추적 및 보상 로직)을 정교하게 구현해야 합니다. 특히 대량 주문 롤백 로직의 구현 난이도가 높습니다.
- **불필요한 DB 쓰기 연산 (Write Amplification):**

  - 재고가 부족한 상황에서도 일단 `Decrement` 연산(Write)을 수행한 후 `Increment` 연산(Rollback Write)을 수행하므로, **실패한 요청도 DB 쓰기 용량(WCU)을 소모**합니다.
- **네트워크 장애 시 정합성 위험:**

  - `Decrement` 요청은 성공했으나, 애플리케이션 서버가 다운되거나 네트워크 이슈로 응답을 받지 못해 **보상 트랜잭션을 수행하지 못하는 경우** 데이터 불일치가 발생할 수 있습니다. (이에 대한 별도의 Reconciliation(대사) 프로세스 필요).

### 1-3. 대안

<https://wiki.team.musinsa.com/wiki/x/z4K8Dg> 참조

#### **1. 전략의 핵심: "의도(Intent) 먼저 기록하기"**

가장 확실한 방법은 재고를 건드리기 전에 "나 이거 가져갈 거야"라는 의도를 먼저 저장하는 것입니다.   
이를 통해 애플리케이션이 죽더라도 "처리하다 만 건"을 식별할 수 있게 만듭니다.

**권장 프로세스 (2-Phase Commit 유사 방식)**

1. **Phase 1 (Intent):** `Allocation` 테이블에 먼저 저장합니다.
2. **Phase 2 (Action):** `Inventory` 테이블에서 재고를 차감합니다.

이 순서로 변경하면 장애 시나리오가 단순해집니다.

- **1번 직후 사망:** 재고 변동 없음. `Allocation` 데이터는 무시됨. (문제 없음)
- **2번 직후 사망:** 정상 처리됨.

#### **2. 장점**

- **전체 트랜잭션 관점의 중복 처리 속도 (Early Return)**

  - Inventory First (기존):

    - `Inventory` 차감 (성공)
    - `Allocation` 기록 시도 -> **중복 발생(Fail)**
    - `Inventory` 롤백 (보상 트랜잭션 필요)
    - **결과:** 중복 요청임에도 불구하고 **최소 2~3번의 DB 연산**과 롤백 로직이 수행되어야 합니다.
  - **Intent First (제안):**

    - `Allocation` 기록 시도 -> **중복 발생(Fail)** -> **즉시 리턴**
    - **결과:** **단 1번의 DB 연산**만으로 트랜잭션이 깔끔하게 종료됩니다. 롤백할 필요 자체가 없습니다.
- **Inventory Write Command의 사전 차단 (Resource Protection)**

  - 가장 중요한 차이는 "비싼 자원(Inventory)을 건드리느냐 마느냐"입니다.
  - **Inventory First:** 중복 요청이라도 무조건 Inventory 테이블에 Write 부하(WCU)를 줍니다. Hot SKU인 경우 이는 치명적일 수 있습니다.
  - **Intent First:** 중복 요청은 아예 **Inventory 테이블에 도달조차 하지 않습니다.** 가장 부하가 심한 테이블을 보호(Guard)하는 효과가 확실합니다.
- **장애 케이스 및 복구의 단순화 (Simpler Recovery)**

  - **Inventory First:** 재고를 깎고(`Inventory OK`) 할당을 기록하다 죽으면(`Allocation Fail`), "재고만 줄어든 상태"가 됩니다. 이는 데이터 불일치 중 가장 골치 아픈 케이스입니다. (누가 가져갔는지 모르니까요)
  - **Intent First:** 할당 의도를 남기고(`Allocation`) 재고를 깎다가 죽으면(`Inventory Fail`), "의도는 있는데 재고는 안 준 상태"가 됩니다. 이는 단순히 재시도(Retry)만 하면 해결되거나, 시간이 지나면 무효화하면 되는 **안전한 불일치**입니다.

---

## 2. 재고 선점 해제

![image-20260106-101446.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/221390862/image-20260106-101446.png?version=1&modificationDate=1767694487478&cacheVersion=1&api=v2&width=483&height=864)

여기를 클릭하여 펼치기...

```
sequenceDiagram
    autonumber
    participant Client as PBO/Client
    participant App as Inventory System
    participant ALLOC as Allocation (DB)
    participant INV as Inventory (DB)

    Note over Client, App: 1. Release 요청 (OrderId, SKU, Qty)
    Client->>App: Request Release

    %% [Exception Case 1] Validation Phase
    Note over App, ALLOC: [Step 1] 상태 검증 (Idempotency Check)
    App->>ALLOC: Find Allocation (by OrderId)
    
    alt Allocation Not Found (404)
        ALLOC-->>App: Null
        App-->>Client: 404 Not Found (Error)
    else Status == SHIPPED (Already Done)
        ALLOC-->>App: Doc (Status='SHIPPED')
        App-->>Client: 200 OK (Idempotent Success)
    else Status == CANCELLED (Logic Error)
        ALLOC-->>App: Doc (Status='CANCELLED')
        App-->>Client: 409 Conflict (Already Cancelled)
    end

    %% [Exception Case 2] Phase 1 Locking Failure
    Note over App, ALLOC: [Step 2] 상태 전이 (Locking: RESERVED -> RELEASING)
    
    App->>ALLOC: CAS Update (Set RELEASING where Status='RESERVED')
    
    alt DB Connection Error / Timeout
        ALLOC-->>App: Exception
        App-->>Client: 500 Internal Server Error (Retryable)
    else ModifiedCount == 0 (Race Condition)
        ALLOC-->>App: 0 Updated
        App->>ALLOC: Re-Check Status
        alt Status == RELEASING (Processing by other)
            App-->>Client: 202 Accepted (Processing)
        else Status == SHIPPED (Done by other)
            App-->>Client: 200 OK
        end
    end

    %% [Exception Case 3] Phase 2 Inventory Failure
    Note over App, INV: [Step 3] 재고 차감 (No-Tx)
    
    App->>INV: Atomic Decrement (Stock & Slot)
    
    alt DB Error / Timeout (Critical)
        INV-->>App: Exception
        Note right of App: ⚠️ [Risk] Allocation is stuck in 'RELEASING'.<br>Client Retry or Sweeper Job required.
        App-->>Client: 500 Internal Server Error (Retryable)
    else Inventory Not Found / Data Error
        INV-->>App: 0 Updated
        Note right of App: 🚨 [Alert] Data Inconsistency!<br>Manual Intervention needed.
        App-->>Client: 500 Internal Server Error (Non-Retryable)
    end

    %% [Exception Case 4] Phase 3 Finalize Failure
    Note over App, ALLOC: [Step 4] 최종 확정 (RELEASING -> SHIPPED)
    
    App->>ALLOC: Update Status to 'SHIPPED'
    
    alt DB Error / Timeout (Partial Failure)
        ALLOC-->>App: Exception
        Note right of App: ⚠️ [Risk] Inventory Deducted BUT Status is 'RELEASING'.<br>Next Retry will fix this (Idempotency).
        App-->>Client: 500 Internal Server Error (Retryable)
    else Success
        ALLOC-->>App: OK
        App-->>Client: 200 OK (Released)
    end
```

### 2-1. 핵심 로직

트랜잭션 없이 `Inventory`(재고)와 `Allocation`(선점 내역) 두 도큐먼트의 정합성을 맞추기 위해, **Allocation의 상태 변경을 Lock처럼 활용**하는 2-Phase State Transition 패턴을 사용합니다.

- **기본 전략:** `RESERVED` → `RELEASING` **(진행 중)** → `SHIPPED` (완료)
- **목적:** 중간 상태(`RELEASING`)를 두어, 로직 수행 중 장애가 발생하더라도 재시도(Retry) 시 중복 차감을 방지하고 작업을 재개할 수 있도록 합니다.

#### **2-1-1. 선점 해제 프로세스**

1. **Idempotency Check:**

   - `Allocation`을 조회하여 이미 `SHIPPED` 상태라면 성공(OK)을 반환하고 종료합니다.
2. **Phase 1 - State Transition (Locking):**

   - `Allocation`의 상태를 `RESERVED`에서 `RELEASING`으로 변경합니다.
   - **CAS (Compare-And-Swap):** `UPDATE Allocation SET status='RELEASING' WHERE allocationId=... AND status='RESERVED'`
   - 이 단계가 실패(수정된 문서 0개)하면, 다른 프로세스가 처리 중이거나 이미 완료된 것이므로 중단합니다.
3. **Phase 2 - Atomic Inventory Update:**

   - `Inventory`의 수량을 원자적으로 조정합니다 (`$inc`).
   - `Stock.Reserved -= Qty`, `Stock.Quantity -= Qty`
4. **Phase 3 - Finalize State:**

   - `Allocation`의 상태를 `RELEASING`에서 `SHIPPED`로 최종 변경합니다.

#### 2-1-2. 주요 예외 시나리오 및 처리 전략


|  |  |  |  |

| --- | --- | --- | --- |

| **예외 상황 (Scenario)** | **발생 시점** | **원인** | **처리 전략 (Strategy)** |

| **Already Shipped** | Step 1 | PBO의 중복 호출 (네트워크 지연 후 재전송 등) | **200 OK 반환.** (작업을 수행하지 않고 성공으로 간주) |

| **Status Cancelled** | Step 1 | 주문이 이미 취소되었는데 출고 지시가 옴 (비즈니스 로직 꼬임) | **409 Conflict 반환.** 운영자 확인 필요. |

| **Locking Fail (Race Condition)** | Step 2 | 동시에 두 개의 프로세스가 같은 주문을 처리 시도 | **ModifiedCount 확인.** 0이면 현재 상태 재조회 후 200/202 반환. |

| **Inventory DB Error** | Step 3 | 재고 차감 중 DB 타임아웃/연결 끊김 | **500 Error 반환.** Allocation은 `RELEASING` 상태로 남음. 클라이언트 재시도 시 Step 3부터 재개됨. (또는 Sweeper가 처리) |

| **Finalize DB Error** | Step 4 | 재고는 차감됐으나 Allocation 상태 변경 실패 | **500 Error 반환.** 재고는 이미 줄어든 상태. 클라이언트 재시도 시 Step 4 로직(이미 차감됨을 인지하거나, 상태만 업데이트)을 수행하여 정상화. |

#### 2-1-3. 아키텍처 고려사항

1. **Zombie State (**`RELEASING`**) 처리:**

   - 위의 예외(DB Error)들로 인해 `RELEASING` 상태에서 멈춘 건들은 Sweeper Job(보정 배치)이 주기적으로 감지하여 `Step 3` 또는 `Step 4`를 재수행해야 합니다.
2. **Retry Policy:**

   - Client(PBO)는 500 에러를 받으면 반드시 지수 백오프(Exponential Backoff)를 사용하여 재시도해야 합니다.
3. **Alerting:**

   - `Inventory Not Found`와 같은 데이터 불일치 에러는 자동 복구가 불가능하므로 즉시 슬랙/이메일 경보(Alert)를 발송해야 합니다.

### 2-2. Trade-off Analysis

- 이 방식은 DB 트랜잭션 오버헤드를 제거하여 쓰기 성능(Write Throughput)을 극대화할 수 있습니다.
- `Allocation`의 Status Enum(`RESERVED | SHIPPED`)에 `RELEASING`상태를 추가해야 합니다.
- 대신, 애플리케이션 레벨에서 상태 전이(State Transition) 로직을 엄격하게 구현해야 하며, 드물게 발생하는 중간 상태(`RELEASING`) 잔류 건을 처리할 수 있는 **보정 메커니즘(Reconciler)** 구현이 필수적입니다.

### 2-3. 장애 복구 및 정합성 보장

트랜잭션을 사용하지 않기 때문에, **Phase 2(재고 차감) 완료 후 Phase 3(상태 확정) 직전**에 시스템이 다운되면 `Allocation`은 `RELEASING` 상태로 남게 됩니다. 이를 해결하기 위한 전략은 다음과 같습니다.

- **재시도 허용 (Retryable):**

  - PBO나 클라이언트가 Timeout으로 인해 동일 요청을 재전송할 경우, 어플리케이션은 `Allocation` 상태가 `RELEASING`임을 확인합니다.
  - 이 경우, **Inventory 차감 로직을 건너뛰고** 바로 Phase 3(상태 확정)만 재수행하거나, 로그를 확인하여 복구합니다.
  - *(안전한 설계를 위해* `Inventory` *업데이트 여부를 확인할 수 없다면, 별도의 비동기 Sweeper가 필요합니다)*
- **Reconciliation Job (Sweeper):**

  - `RELEASING` 상태로 `N분` 이상 머물러 있는 `Allocation`을 조회하는 배치 잡(Job)을 운영합니다.
  - 이 잡은 해당 건에 대해 `Inventory` 상태를 확인(또는 보정)하고 `SHIPPED`로 상태를 강제 종결(Self-Healing)합니다.

---

## 3. Slot Selection 매커니즘

<https://wiki.team.musinsa.com/wiki/x/jAUND> 참고

슬롯 선택 메커니즘은 주문 요청 시 유입된 다양한 속성(Platform, ItemId, Event 등)을 표준화된 태그(Tag)로 변환하고, 이를 기반으로 Slot 중 가장 적합한 대상을 필터링 및 정렬하여 차감 순서를 결정하는 로직이다.

이 프로세스는 요청 데이터를 '태그(Tag)'로 표준화하여 변환하는 단계, 조건에 부합하는 후보군을 추려내는 **'필터링(Filtering)'** 단계, 그리고 소진 순서를 결정하는 **'정렬(Sorting)'** 단계로 구성된다.

### 3-1. 데이터 모델 명세 (Data Model Specifications)

#### 3-1-1. 할당 요청 모델 (Allocation Request Context)

슬롯 선택을 위해 클라이언트로부터 수신하는 데이터 구조이다.


|  |  |  |

| --- | --- | --- |

| **필드명** | **설명** | **비고** |

| **productId** | 대상 상품의 고유 식별자 | Core 속성 (자동 태그 변환) |

| **platformId** | 주문이 발생한 판매 채널 ID | Core 속성 (자동 태그 변환) |

| **optionId** | 상품의 옵션 식별자 | Core 속성 (자동 태그 변환) |

| **extensionTags** | 비즈니스 확장을 위한 키-값(Key-Value) 리스트 | Extension 속성 (명시적 수신) |

#### 3-1-2. 태그 네임스페이스 정책 (Tag Namespace Policy)

데이터 충돌 방지 및 가독성 확보를 위해, 시스템 내부적으로 사용하는 태그는 약어를 배제하고 **전체 단어(Full Words) 기반의 접두어(Prefix)** 규칙을 따른다.

- **PRODUCT:** 상품 식별자 (예: `PRODUCT:1001`)
- **PLATFORM:** 판매 채널 식별자 (예: `PLATFORM:MSS`)
- **OPTION:** 옵션 식별자 (예: `OPTION:109`)
- **EXTENSION:** 외부에서 주입된 Key를 대문자로 변환하여 Prefix로 사용 (예: `SEASON:SUMMER`)

### 3-2. 알고리즘 상세 로직 (Algorithm Logic)

전체 프로세스는 **[1. 컨텍스트 빌딩] → [2. 후보군 조회] → [3. 적합성 검증] → [4. 우선순위 결정]** 순서로 수행된다.

#### 3-2-1. 단계 1: 태그 컨텍스트 빌딩 (Tag Context Building)

요청 객체(Request DTO)를 분석하여 비교 기준이 될 '쿼리 태그 집합(Query Tag Set)'을 생성한다.

1. **Core 속성 변환 (Auto-Build):**

   - `productId` 존재 시 → `PRODUCT:` 접두어와 결합 (예: `PRODUCT:1001`)
   - `platformId` 존재 시 → `PLATFORM:` 접두어와 결합 (예: `PLATFORM:MSS`)
   - `optionId` 존재 시 → `OPTION:` 접두어와 결합 (예: `OPTION:10`)
2. **Extension 속성 변환 (Explicit-Build):**

   - `extensionTags` 리스트를 순회하며 `Key`와 `Value`를 추출한다.
   - `Key`는 대문자로 정규화(Normalize)하여 접두어로 사용한다.
   - 생성 포맷: `KEY:VALUE` (예: `SEASON:SUMMER`)

#### 3-2-2. 단계 2: 후보군 조회 (Candidate Fetching)

데이터베이스로부터 물리적 차감이 가능한 슬롯들을 1차적으로 조회한다.

- **조회 기준:** 요청된 `productId`에 속하며, 현재 상태가 `ACTIVE`인 모든 슬롯.
- **전략:** 이 단계에서는 정밀한 태그 필터링을 수행하지 않고, 상품에 귀속된 모든 슬롯을 메모리로 로드하여 애플리케이션 레벨에서 매칭을 수행한다.

#### 3-2-3 단계 3: 적합성 검증 (Matching / Filtering)

조회된 후보 슬롯들이 현재 요청(Query Context)을 처리할 수 있는지 검증하여 유효한 슬롯만 남긴다.

- **매칭 원칙 (Subset Logic):** "슬롯이 요구하는 모든 조건(Tag)을 요청이 충족해야 한다."
- **판단 로직:**

  - 슬롯의 태그 집합이 쿼리 태그 집합의 **부분 집합(Subset)** 인지 확인한다.
  - **공용 슬롯(General Slot):** 태그가 비어 있거나 `COMMON` 태그만 가진 슬롯은 제약 조건이 없는 것으로 간주하여 항상 매칭 성공(True)으로 처리한다.
  - **전용 슬롯(Specific Slot):** 슬롯에 `USER_GRADE:VIP` 태그가 설정되어 있다면, 요청 쿼리에도 반드시 `USER_GRADE:VIP` 태그가 포함되어 있어야만 매칭된다.

#### 3-2-4. 단계 4: 우선순위 결정 (Scoring & Sorting)

필터링을 통과한 슬롯들을 대상으로 소진 순서를 정렬한다.

**정렬 기준 (명시적 우선순위):** 슬롯 데이터에 설정된 `priority` 값이 낮은 순서대로 정렬한다. (1순위 > 2순위)

### 3-3. 예외 케이스 처리


|  |  |  |

| --- | --- | --- |

| **시나리오** | **현상 설명** | **시스템 동작 및 결과** |

| **요청 태그 불일치** | 클라이언트 오타 등으로 슬롯의 태그와 정확히 일치하지 않는 경우 | 해당 전용 슬롯과는 매칭에 실패하며, 태그 조건이 없는 **공용 슬롯(Core Slot)으로 자동 Fallback** 되어 처리된다. |

| **태그 없는 슬롯** | 슬롯에 아무런 태그가 설정되지 않은 경우 | 유효한 슬롯 리스트가 비어있으므로 `OutOfStockException`을 발생시켜 주문을 차단한다. |

| **매칭 슬롯 부재** | 조건에 맞는 슬롯이 하나도 없는 경우 | 유효한 슬롯 리스트가 비어있으므로 `OutOfStockException`을 발생시켜 주문을 차단한다. |

| **부분 재고 부족** | 1순위 슬롯만으로는 주문 수량을 충족하지 못하는 경우 | **Waterfall** 방식에 따라 1순위 슬롯을 전량 소진한 후, 부족분을 2순위 슬롯에서 이어서 차감한다. |

---

## 4. 판매 가능 재고 계산 매커니즘

재고 조회는 저장된 데이터를 단순히 반환하는 것이 아니라, 물리적 재고(Stock)의 제약과 논리적 한도(Slot)의 제약을 실시간으로 조합하여 최종 판매 가능 수량(Available Quantity)을 산출하는 과정입니다.

### 4-1. 기본 조회 전략 (Read Strategy)

Core Inventory 시스템은 "물리적 가용량과 논리적 가용량의 교집합"을 계산하여 최종 재고를 노출합니다.

- **실시간 계산 (On-Read Calculation):** DB에 저장된 정적인 값이 아니라, 조회 시점의 `StockBucket`과 `SlotBucket` 상태를 비교하여 동적으로 계산된 값을 반환합니다.
- **제약 조건의 우선순위:** 물리적으로 재고가 존재하더라도 논리적 슬롯(Slot)이 만료되면 판매할 수 없으며, 반대로 슬롯 한도가 남아있더라도 물리적 재고가 없으면 판매할 수 없습니다. 따라서 시스템은 항상 가장 보수적인 값(Minimum Value)을 채택합니다.

### 4-2. 가용량 계산 로직 (Availability Calculation Logic)

클라이언트(PDP, Checkout 등)에게 전달되는 `AvailableQuantity`는 다음 공식을 통해 산출됩니다.

> Available = min(Stock.Remaining, Slot.Remaining)

1. **Physical Availability (물리적 잔여량):**

   - 해당 Inventory에 속한 모든(또는 특정 FC의) `StockBucket`의 잔여 수량 합계입니다.
   - `Stock.Remaining` = `Stock.Quantity` - `Stock.Reserved`.
2. **Logical Availability (논리적 잔여량):**

   - 현재 판매 채널이나 이벤트에 할당된 특정 `SlotBucket`의 잔여 한도입니다.
   - `Slot.Remaining` = `Slot.Limit` - `Slot.Reserved`.
3. **Final Decision (최종 결정):**

   - 위 두 값 중 더 작은 값(Min)이 최종적으로 고객이 구매 가능한 수량이 됩니다.

### 4-3. 계산 시나리오 예시 (Calculation Scenario)

동일한 `Inventory` 상태라도, `Stock`과 `Slot`의 상황에 따라 노출되는 재고가 달라집니다.


|  |  |  |  |  |

| --- | --- | --- | --- | --- |

| **시나리오** | **물리 재고 (Stock Remaining)** | **논리 슬롯 (Slot Remaining)** | **최종 노출 재고 (Result)** | **판단 근거** |

| **Case A** | **100개** (여유) | **10개** (한정 판매) | **10개** | 슬롯 한도에 의해 판매가 제한됨 |

| **Case B** | **5개** (부족) | **50개** (여유) | **5개** | 슬롯은 넉넉하나 실물 재고가 부족함 |

| **Case C** | **0개** (품절) | **10개** (여유) | **0개 (Sold Out)** | 물리 재고 소진으로 인한 품절 |

| **Case D** | **100개** (여유) | **0개** (마감) | **0개 (Sold Out)** | 한정 수량(Slot) 소진으로 인한 판매 종료 |

---

# Appendix.

## 1. Reconciliation Strategy (Sweeper)

현 기능은 “LLD-I10. Reconciliation” 에서 조금 더 자세히 다룹니다.

### 1-1. 개요 (Overview)

No-Transaction 환경(Model C)에서 발생할 수 있는 데이터 불일치(Ghost Deduction) 및 프로세스 중단(Zombie State)을 해소하기 위해, 목적과 주기에 따른 Multi-Track 전략을 사용합니다.

보정(Reconciliation) 작업이 수행되는 그 찰나의 순간에도 실시간 주문(Live Traffic)으로 인해 재고 수량은 계속 변동될 수 있습니다. 이때 단순히 값을 덮어쓰거나 원자적이지 않은 방식으로 처리하면 심각한 문제가 발생합니다.

따라서 각 Sweeper 모드별로 증감 연사자를 이용한 **원자적 처리**가 필요합니다.

- **Mode A. Incremental Sweeper (증분 대사):**

  - **주기:** 30분 간격 실행.
  - **대상:** 최근 30분 내에 "수량이 변동된 적이 있는" Inventory.
  - **목적:** Ghost Deduction(유령 차감)을 빠르게 탐지하여 `Available` 재고를 복구하고 판매 기회 손실 최소화.
- **Mode B. Zombie Sweeper (좀비 정리):**

  - **주기:** 5~10분 간격 실행.
  - **대상:** 선점 해제 중(`RELEASING`) 상태로 10분 이상 멈춘 Allocation.
  - **목적:** 프로세스를 강제 종결(`SHIPPED`)하고, 혹시 모를 Oversell(초과 판매)을 방지하기 위해 보수적으로 재고를 차감.
- **External. WMS Sync (물류 동기화):**

  - **주기:** 이벤트 기반 (수시).
  - **목적:** Mode B에 의해 발생할 수 있는 Under-stock(재고 과소) 현상을 실제 물류 재고 기준으로 최종 보정.
- **Full Sweeper (전수 대사):**

  - **주기:** 1일 1회 (새벽 시간).
  - **목적:** 데이터 정합성 최종 보루 (Safety Net).
  - **Note:** *본 문서의 범위를 벗어나므로 상세 설계를 제외합니다. 전수 검증 프로세스에 대한 상세 내용은 별도의 [Reconciliation System] 문서에서 다룹니다.*

### 1-2. Mode A: Incremental Sweeper (증분 대사)

애플리케이션 크래시로 인해 `Inventory.Reserved`는 증가했으나, `Allocation` 기록이 없는 **Ghost Deduction**을 해결합니다.

- **실행 조건:** 매시 00분, 30분 실행.
- **전제 조건:** `Inventory` 테이블에 `updatedAt` 속성 및 GSI가 존재해야 함.
- **조회 범위 (Time Window):**

  - `TargetTime` = `CurrentTime` - `Buffer(5min)`
  - **Buffer 목적:** 현재 진행 중인 트랜잭션(In-flight)을 건드리지 않기 위해, 최소 5분 전까지의 데이터만 검증.
  - **Query:** `GSI_UpdatedAt` > `(TargetTime - 40min)` (30분 주기 + 여유분 10분 Overlapping)

#### **Step-by-Step Flow**

1. **Targeting (대상 선정):**

   - Inventory 테이블의 GSI(`updatedAt`)를 조회하여, 해당 시간 범위 내에 변경된 `inventoryId` 목록을 추출합니다.
2. **Aggregation (실제 선점량 계산):**

   - 추출된 `inventoryId` 각각에 대해 `Allocation` 테이블을 조회합니다.
   - `Status = 'RESERVED'`인 항목들의 수량을 합산합니다 (`RealReserved = Sum(qty)`).
3. **Verification (검증 및 보정):**

   - `Inventory.reserved` (DB 기록값) **vs** `RealReserved` (실제 합계) 비교.
   - **불일치 시:** `Inventory.reserved` 값을 `RealReserved`로 강제 업데이트(Correction)하여 잘못 잠긴 가용 재고를 복구합니다.

#### Sequence Diagram

![image-20260107-144237.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/221390862/image-20260107-144237.png?version=1&modificationDate=1767796959274&cacheVersion=1&api=v2&width=613&height=661)

여기를 클릭하여 펼치기...

```
sequenceDiagram
    autonumber
    participant Job as Incremental Sweeper
    participant INV as Inventory (DB)
    participant ALLOC as Allocation (DB)

    Note over Job, INV: [Trigger] 30분 주기 실행 (Buffer 5분)

    Job->>INV: 1. Get Modified Inventories<br>(GSI query: updatedAt > T-35m)
    INV-->>Job: List [Inv_A, Inv_B, ...]

    loop For Each Inventory (Inv_A)
        Job->>ALLOC: 2. Query Active Allocations<br>(PK=Inv_A, Filter status='RESERVED')
        ALLOC-->>Job: [ {id:1, qty:2}, {id:2, qty:3} ]
        
        Job->>Job: 3. Calculate Sum (2+3 = 5)
        
        Job->>INV: 4. Check Current Reserved
        INV-->>Job: { reserved: 7 } (Ghost Deduction Found!)
        
        alt Mismatch (7 != 5)
            Note right of Job: 🚨 유령 차감 발견 (차이: 2)<br>앱 크래시로 기록 실패한 건 복구
            Job->>INV: 5. Force Update (reserved = 5)
            INV-->>Job: OK
        end
    end
```

### 1-3. Mode B: Zombie Sweeper (좀비 상태 정리)

선점 해제 시도 중(`RELEASING`) 프로세스가 중단된 건을 찾아 종결시킵니다. 이때 "Oversell 방지"를 최우선으로 하여 **강제 차감 전략**을 수행합니다.

- **실행 조건:** 5~10분 주기 실행.
- **전제 조건:** `Allocation` 테이블에 `Status` GSI가 존재해야 함.
- **조회 범위:** `Status = 'RELEASING'` **AND** `updatedAt < (CurrentTime - 10min)`

#### **Step-by-Step Flow**

1. **Targeting (대상 선정):**

   - `Allocation` 테이블의 GSI를 통해 장시간 `RELEASING` 상태로 멈춰있는 건들을 조회합니다.
2. **Force Decrement (재고 강제 차감):**

   - 해당 주문이 재고를 차감했는지 여부가 불확실하므로, "안전하게 한 번 더 차감"하는 전략을 취합니다.
   - Inventory Update: `quantity = quantity - qty`, `reserved = reserved - qty`
   - ***(Note: 이미 차감된 상태였다면 이중 차감(Double Deduction)이 발생하지만, Oversell보다는 안전합니다.)***
3. **Finalize Status (상태 종결):**

   - `Allocation`의 상태를 `SHIPPED`로 변경하여 생명주기를 종료합니다.
   - 이후 Mode A(증분 대사)가 돌 때, 이 건은 합계에서 제외되므로 `Inventory.Reserved` 수치는 자동으로 정상화됩니다.

#### Sequence Diagram

![image-20260107-151558.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/221390862/image-20260107-151558.png?version=1&modificationDate=1767798960431&cacheVersion=1&api=v2&width=722&height=660)

여기를 클릭하여 펼치기...

```
sequenceDiagram
    autonumber
    participant Job as Zombie Sweeper
    participant ALLOC as Allocation (DB)
    participant INV as Inventory (DB)

    Note over Job, ALLOC: [Trigger] 5~10분 주기 실행<br>(Target: RELEASING 상태로 10분 이상 경과)

    %% 1. 대상 조회
    Job->>ALLOC: 1. Scan Stuck Allocations (GSI Use)
    ALLOC-->>Job: List [ {id:101, qty:2}, ... ]

    loop For Each Zombie Item
        Note right of Job: ⚠️ 재고 차감 여부 불확실.<br>Oversell 방지를 위해 '무조건 차감' 수행.
        
        %% 2. Inventory 원자적 강제 차감 (Atomic Decrement)
        Note over Job, INV: [Critical] 증감 연산자를 사용한 원자적 업데이트
        Job->>INV: 2. UpdateItem (PK=InvId)<br>SET quantity = quantity - :qty,<br>    reserved = reserved - :qty
        
        alt Update Success
            INV-->>Job: OK (New Balance)
            Note right of INV: 이미 차감된 건이었다면 '이중 차감' 발생 (Under-stock).<br>이는 추후 WMS Sync가 보정함.
        else DB Error
            Job->>Job: Skip & Retry Next Time
        end
        
        %% 3. 상태 종결
        Note over Job, ALLOC: [Finalize] 상태 종결 처리
        Job->>ALLOC: 3. UpdateItem (PK=AllocId)<br>SET status = 'SHIPPED'
        ALLOC-->>Job: OK
    end
```

### 1-4. External: SLS Sync Integration

Mode B(Zombie Sweeper)의 "강제 차감"으로 인해 발생할 수 있는 **Under-stock(재고 과소)** 현상을 물류 시스템 이벤트를 통해 해소합니다.

- **실행 조건:** SLS(물류 시스템)로부터 입/출고 및 재고 변동 이벤트 수신 시 (Event-Driven).
- **데이터 소스:** SLS 이벤트 페이로드 내 포함된 `Snapshot Quantity` (물리적 실재고 총량).

#### **Step-by-Step Flow**

1. **Event Consumption (이벤트 수신):**

   - WMS로부터 특정 SKU/Inventory에 대한 변동 이벤트를 수신합니다.
2. **Delta Calculation (델타 보정):**

   - `SLS Snapshot Qty` **vs** `Current Inventory Qty` 비교.
   - `Diff = WMS Snapshot - Current Local`
3. **Synchronization (동기화):**

   - 차이값(`Diff`)만큼 `Inventory.quantity`를 가감(`$inc`)하여 실물 재고와 데이터를 일치시킵니다.
   - 이 과정을 통해 Mode B에서 발생했던 이중 차감분이 자연스럽게 채워집니다.

---

# 대안 옵션

## 1. Stock(물리 재고)에 대한 구조 분리 관점 비교 (분리 vs 통합)


| 항목 | Stock 분리 설계 | Stock 통합 설계 |

| --- | --- | --- |

| 물리 재고 | Stock(inventoryId, fcId, quantity) | Inventory.fcStocks[{ fcId, quantity }] |

| 선점 써머리 | Inventory.allocationsSummary[{ fcId, slotId, reservedQuantity }] | 동일 |

| Slot/정책 | Inventory.slots[...] | 동일 |

| Tx 범위 | 선점/해제는 주로 Inventory만, 출고는 Stock+Inventory **멀티 Tx** | Inventory 한 도큐 안에서 원자 업데이트 |

| Throughput | 선점/해제는 좋고, 출고는 멀티 Tx 경합 가능 | 선점/해제/출고 모두 단일 도큐 기준 → 단순/직관 |

| 도메인 경계 | 물류(Stock)와 주문/선점(Inventory) 경계가 물리적으로 분리 | 한 도큐에 섞임 → 경계는 “규칙/코드”로 관리 |

| 핫 스팟 | Stock/Inventory 각각 나눠 가짐 | 인기 SKU의 Inventory가 더 큰 핫스팟이 됨 |

## 2. Inventory 및 Allocation Tx 분리에 대한 trade-off

<https://wiki.team.musinsa.com/wiki/x/fAKhDg> 문서로 대체합니다.

## 3. DB에 대한 trade-off

<https://wiki.team.musinsa.com/wiki/x/1gv_DQ> 문서로 대체합니다.

- Poc 진행 문서: <https://wiki.team.musinsa.com/wiki/x/G4O9Dg>