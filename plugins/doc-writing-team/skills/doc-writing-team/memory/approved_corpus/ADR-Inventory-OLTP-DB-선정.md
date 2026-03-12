# ADR: Inventory OLTP DB 선정

> **Page ID**: 261101296

---

# 0. Reference links

[CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates)

<https://wiki.team.musinsa.com/wiki/spaces/PRODUCTS/pages/258030137/CIAP+Inventory+DB?atl_f=PAGETREE>

# 1. 결정 요약 (TL;DR)


| **항목** | **결정** | **근거/비고** |

| --- | --- | --- |

| **도메인 처리 모델** | Model C(No-Tx/Saga + CAS/단일 항목 원자 연산 중심) 를 채택 | DynamoDB 시나리오 테스트에서 Model A/B는 고경합에서 성공률이 급락하고, Model C는 100% 성공 및 오버셀 0을 기록합니다. |

| **후보 DB 범위** | DynamoDB 또는 ScyllaDB 중 하나로 한정 | Model C에서 필요한 인터페이스/의미론이 “DynamoDB API 서브셋”으로 수렴하도록 설계하여, 선택지를 2개로 제한하고 도메인 개발에 집중합니다(“전환”이 목적이 아니라 “선택지 축소”가 목적입니다). |

| **테스트 수행 현황** | DynamoDB 시나리오 테스트는 수행 완료 | 본 문서의 실증 근거는 DynamoDB 기반 시나리오 결과입니다. |

| **추가 검증** | ScyllaDB에 대해 동일 시나리오 테스트를 추가 수행한 뒤 최종 선택 | Scylla는 LWT(CAS) 고경합 시 성능 급락 가능성이 있어 수치 검증이 필요합니다. |

| **MongoDB** | **후보에 포함하지 않으며, 시나리오 테스트도 수행하지 않음** | Scalability/Reliability/Recovery 및 운영 안정성 관점의 리스크(장애/확장 이벤트, failover 쓰기 불가, 샤딩 운영 공수, hot document 경합 등)가 CIAP 목표 대비 과도합니다. |

---

# 2. 배경 및 목표

재고 시스템은 이커머스의 핵심 시스템으로서 다음을 동시에 만족해야 합니다.

[CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates#0.-%EC%9A%94%EA%B5%AC%EC%82%AC%ED%95%AD-%EC%9A%94%EC%95%BD)

- 대규모 트래픽(프로모션/라이브커머스/핫딜)에서 **Scale-out/Scale-in이 무중단으로 수행**되어야 합니다.
- 노드 추가/제거, 리밸런싱(데이터 이동/compaction/streaming) 중에도 SLO(특히 tail latency)와 처리량 안정성(jitter 최소화)을 유지해야 합니다.
- 노드/AZ/리전 장애 시 자동 우회/복구 및 필요 시 멀티리전(Active-Active 또는 Active-Standby) 확장이 가능해야 합니다.
- 장애 전환(Failover/Failback) 과정이 자동화 가능하고, 전환 중 데이터 정합성과 중복처리 방지가 보장되어야 합니다.

---

# 3. 아키텍처 결정: Model C

## 3.1. 결정

<https://wiki.team.musinsa.com/wiki/spaces/PRODUCTS/pages/258030137/CIAP+Inventory+DB?atl_f=PAGETREE> 문서에서 검증한 3개 모델은 다음과 같습니다:

- Model A: 강한 결합 트랜잭션(Single Tx)
- Model B: Inventory-First(선점 후 할당, Lazy Compensation)
- Model C: No-Tx(App-level Saga, Single Item Atomic Loop)

주요 결론은 다음과 같습니다.

- **대량 주문 한계(Bulk-Limit)**: Model A는 DB 트랜잭션 제한으로 구조적으로 실패했으며, Model C는 단건 루프 처리로 제한을 우회했습니다.
- **핫 SKU 고경합(1,000명이 1개 상품 동시 구매 시도)**: 트랜잭션 기반(Model A/B)은 TransactionConflict로 치명적으로 실패했으며, Model C는 100% 성공했습니다.
- **성능/안정성(Performance Test)**: 저충돌/고부하 구간에서 Model C가 더 높은 TPS와 낮은 실패율을 기록했습니다.
- **보상 트랜잭션 신뢰성 및 시스템 안정성**: 롤백 테스트에서 수학적 무결성과 0% HTTP 실패율이 함께 제시됩니다.

요약하면, CIAP의 “핫 SKU + 고동시성” 본질적 워크로드에서 **멀티 엔티티 트랜잭션은 성능·안정성 리스크를 제거하지 못하며**, 오히려 충돌/제한/비용을 확대할 가능성이 큽니다. 따라서 **Model C를 기본 모델로 고정**하는 것이 합리적입니다.

## 3.2. Model C 채택 시 반드시 지켜야하는 설계 전제

Model C는 “DB 트랜잭션으로 강한 정합성을 확보하는 모델”이 아니므로, 다음을 전제합니다.

1. **원자성의 기준을 “단일 레코드(또는 단일 파티션 키 범위) 조건부 업데이트(CAS)”로 제한합니다.**  
   재고 선점/차감의 핵심은 “복잡한 다건 트랜잭션”이 아니라 “단일 레코드에 대한 원자적 연산”이라는 점을 전제로 합니다.
2. **Saga/보상(Compensation)은 필연적으로 “일시적 불일치(Consistency failure)”를 동반할 수 있음을 인정하고, 이를 운영 가능한 형태로 설계합니다.**  
   즉, 분산 환경에서 “완전한 즉시 일관성” 대신 “관측 가능하고 복구 가능한 일관성”을 목표로 합니다(멱등성/재처리/보상 경로 필수).
3. **일관성 실패가 발생하더라도 도메인 정책은 ‘Oversell 방지(Undersell 허용)’로 고정합니다.**  
   과판매(Oversell)는 파트너/고객 신뢰 및 보상/물류 임팩트가 크고, 판매기회 손실(Undersell)은 상대적으로 관리 가능하다는 비즈니스 합의를 전제로 합니다.
4. **OLTP 재고 DB는 “핵심 키 기반 조회/갱신”에 집중하고, 관리자 조회/복합 필터/통계성 질의는 별도 경로로 분리합니다.**  
   DynamoDB는 GSI 개수 제한과 Range Query/Multi-filter 한계가 명확하므로, 운영/통계성 조회를 OLTP에 강제로 얹지 않는 전제가 필요합니다.

---

# 4. 후보 단일화: DynamoDB vs. ScyllaDB

## 4.1. 단일화의 이유

본 문서에서 “DynamoDB Driver 단일화”를 언급하는 목적은 다음 한 가지입니다.

- **애플리케이션 구현 관점에서 인터페이스를 DynamoDB API 중심으로 고정해, DB 선택지를 ‘DynamoDB 또는 ScyllaDB’로 의도적으로 좁힙니다.**  
  즉, MongoDB를 포함한 다른 DB를 폭넓게 열어두는 대신, **두 개 후보 중 하나를 선택**하는 전략으로 도메인 로직 개발·운영 체계 구축·테스트 자동화에 집중합니다.

단, 이 전략은 “호환성 범위가 명확히 정의될 때”만 안전합니다. 따라서 다음을 명시합니다.

- 사용 API는 Model C 구현에 필요한 **핵심 연산(ConditionExpression 기반 UpdateItem/PutItem 등)** 중심으로 최소화합니다.
- 후보별 고유 기능(예: DynamoDB의 특정 매니지드 기능, Scylla의 특정 확장 기능)에 도메인 로직이 과도하게 결합되지 않도록 도메인 로직 구현에 제약을 둡니다.

## 4.2. MongoDB 후보 제외 사유

MongoDB는 벤치마크 관점에서 특정 조건에서 높은 성능이 관찰될 수 있으나, CIAP의 목표는 “특정 벤치마크 최고점”이 아니라 **무중단 확장·장애·일관성·운영 리스크를 포함한 종합 안정성**입니다. MongoDB를 후보에서 제외하는 근거는 다음과 같습니다.

### 4.2.1. 샤딩 환경에서 멀티 도큐먼트 트랜잭션 비용 및 운영 복잡도

- MongoDB는 샤딩 클러스터에서 멀티 도큐먼트 트랜잭션을 지원하지만, **여러 샤드를 건드리는 트랜잭션은 더 큰 성능 비용을 유발**한다고 공식 문서에 명시되어 있습니다.

  - <https://www.mongodb.com/docs/manual/core/transactions-sharded-clusters/>
- [CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates) 문서 역시 “샤딩 시에 멀티도큐먼트 트랜잭션 비용이 더 큼” 및 “샤딩 클러스터 운영 공수 필요”를 명시합니다.

CIAP는 이미 Model C로 방향을 잡았기 때문에 “트랜잭션으로 강한 정합성을 쉽게 얻는 이점”을 MongoDB에서 활용하지 않습니다. 따라서 `MongoDB는 멀티 tx를 제공해줄 수 있다` 라는 장점은 CIAP 재고 시스템에서는 취할 수 없는 장점입니다.

### 4.2.2. 샤딩 환경에서 Scale-out/in시에 발생하는 성능 지표 저하 현상

- MongoDB 샤딩 환경에서 Scale-out(샤드 추가)은 ‘노드를 늘리면 곧바로 부하가 분산된다’라기보다는, 데이터를 새 샤드로 옮겨 ‘실제로 분산되는 과정’이 뒤따릅니다.
- 이 과정이 바로 **balancer의 chunk migration(리밸런싱)** 이고, 경우에 따라 **reshardCollection(리샤딩/재분산)** 이 사용됩니다. MongoDB는 이 절차가 사용자에게 투명하다고 설명하지만, 동시에 **절차가 진행되는 동안 성능 영향이 있을 수 있다**고 공식 문서에 명시합니다.

  - <https://www.mongodb.com/ko-kr/docs/v8.0/core/sharding-balancer-administration/>
  - <https://www.mongodb.com/ko-kr/docs/manual/core/sharding-reshard-a-collection/>
- Scale-out으로 인해 발생할 수 있는 performance impact는 Online Critical Search Path인 재고시스템 입장에서는 장애로 인지해야합니다.

### 4.2.3. Failover 시 쓰기 불가 구간 및 P99.99+ 안정성 리스크

- [CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates) 문서는 MongoDB에 대해 Failover 시 수 초간 쓰기 불가(Downtime)가 존재함을 명시합니다.
- MongoDB 공식 문서에서도 replica set election(새 primary 선출)까지의 시간이 기본 설정에서 통상 두 자릿수 초(예: median 12초) 수준임을 설명합니다.

  - <https://www.mongodb.com/docs/manual/core/replica-set-elections/>

CIAP의 재고는 주문 경로의 핵심이므로, 짧은 write unavailability도 곧바로 사용자 체감 실패율 및 tail latency를 악화시킬 수 있습니다.

### 4.2.4. 데이터 롤백(ack 된 write의 유실 가능성)과 이를 피하기 위한 majority의 비용

- MongoDB는 write concern이 primary 단독 ack인 경우, primary가 stepdown/failover 되기 전에 복제되지 않은 데이터가 **rollback 될 수 있음**을 문서에서 경고합니다.
- acknowledged write의 rollback 방지를 위해서는 **{w:"majority"} 및 journaling** 등을 권고합니다.

즉, “데이터 유실 리스크를 낮추기 위해 majority를 강제”하면, 그 자체가 CIAP의 low latency/high throughput 목표에 부담으로 작용합니다(특히 tail latency에 직접적인 영향이 있습니다).

### 4.2.5. 결론

따라서 MongoDB는 “Model C로 트랜잭션을 피하더라도” CIAP이 요구하는 **가용성·일관성·운영 안정성·확장 중 성능 보장** 관점에서 리스크 대비 이점이 낮아 후보에서 제외합니다.

---

# 5. Hot SKU 대응 전략

“Hot SKU 전략을 어떻게 구현하는가”에 대해서는 더 자세한 설계가 필요합니다.

다만 `Hot SKU를 발생 기준에 근거하여 식별하고, Hot SKU가 식별되었을때 별도의 process로 처리한다` 수준으로 거시적인 설계는 유효하며, 시나리오 테스트 이후에 CIAP 시스템 설계시에 고려되어야 합니다.

핫키는 DynamoDB든 ScyllaDB(LWT)든 **성능 임팩트를 유발할 수 있는 공통 리스크**입니다. 특히 DynamoDB는 단일 파티션 키의 물리 한계(예: 1,000 WCU)를 초과할 수 없고, 트랜잭션 사용 시 비용이 2배로 증가해 단일 SKU 처리 한계가 더 낮아질 수 있습니다.

따라서 다음 전략을 기본 방침으로 둡니다.

- **핫키 감지(기준 정의)**: 고경합 테스트 결과를 기반으로 “Hot SKU 발생 기준(throughput, throttling, LWT conflict rate, P99+ 급등 등)”을 수치로 정의합니다.
- **핫키 구간 처리 방식 전환**: 기준을 초과한 SKU에 대해서는 해당 SKU에 한해 **latency를 일부 희생하더라도 queue 기반 동기식(직렬화) 처리로 throughput과 안정성을 보장**합니다.
- **영향 범위 격리**: 핫 SKU의 처리 지연이 전체 SKU/전체 주문 흐름의 tail latency를 끌어올리지 않도록, 큐·워커·레이트리밋·서킷브레이커를 SKU 단위로 격리합니다.

---

# 6. ScyllaDB 추가 검증이 필요한 이유와 테스트 방향

[CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates) 에서는 Cassandra(LWT)가 Hot SKU reserve에서 성공률이 70%대로 떨어지고(p95가 크게 증가) “LWT 병목”이 관찰되었다고 명시하고 있습니다.

따라서 ScyllaDB 채택 가능성을 판단하려면, 최소한 다음을 **동일 시나리오/동일 측정 기준**으로 재검증해야 합니다.

- Model C의 핵심 연산을 ScyllaDB에서 구현할 때, **LWT 사용 여부/범위/라우팅 전략**에 따라 P99.99+ latency와 성공률이 어떻게 변하는지 확인합니다.
- 핫 SKU에서의 **conflict/timeout/retry** 패턴이 서비스 레벨에서 운영 가능한지 확인합니다.
- Scale-out/Scale-in 및 리밸런싱 중에도 tail latency SLO를 유지할 수 있는지 확인합니다.
- 적정 수준의 Quorum/DC/RF 설정, Shard-aware routing driver를 사용하여 LWT 환경에서의 성능을 끌어올리는 튜닝이 필요합니다.

---

# 7. 비용 및 기타 고려사항

[CIAP: Inventory Database Candidates](/wiki/spaces/PRODUCTS/pages/234752982/CIAP+Inventory+Database+Candidates) 문서에는 특정 트래픽 가정(Read 2,000 RPS / Write 1,000 RPS) 하에서 DynamoDB(Provisioned)와 유사 수준이며, MongoDB Atlas는 고정 비용 구조로 더 높게 제시됩니다.

다만 본 의사결정의 1차 기준은 비용이 아니라 **SLO/안정성/운영 리스크**에 더 높은 우선순위로 결정하였습니다.

---

# 8. Next Action Items

1. **ScyllaDB 시나리오 테스트 수행**

   1. DynamoDB에서 수행한 Model C 중심 시나리오(특히 Hot SKU 고경합)를 ScyllaDB에서 재현합니다.
   2. LWT 사용 여부/핫키 분산·큐 전환 정책까지 포함해 “운영 가능한 수치”를 확보합니다.
2. **핫키 감지 기준 수치화 및 운영 정책 확정**

   1. “언제 큐로 전환하는가 / 언제 원복하는가 / 전환 중 정합성·멱등성은 어떻게 유지하는가”를 문서화합니다.