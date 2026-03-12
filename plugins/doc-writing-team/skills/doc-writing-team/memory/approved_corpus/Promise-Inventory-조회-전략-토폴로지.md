# Promise Inventory 데이터 조회 전략 및 연결 토폴로지 선정

> **Page ID**: 256348236

---

# 1. Context (배경 및 문제 정의)

- **시스템 성능 목표:** Core Promise System은 단일 상품 조회 시 **P99 50ms**, **최대 140,000 TPS**라는 초고성능을 보장해야 하는 환경에 놓여 있습니다.
- **데이터의 특성 (초고변동성):** 재고(Inventory)는 주문과 취소에 의해 초 단위로 변하는 'High Volatility' 데이터입니다. 단 1개의 수량 차이가 판매 가능 여부를 결정하는 임계값이 되므로 정합성이 매우 중요합니다.
- **핵심 쟁점:**

  - **실시간성 보장:** 오판매(Overselling) 방지를 위해 데이터 정합성을 최우선으로 확보해야 합니다.
  - **통신 효율성:** 상품 목록(PLP) 진입 시 발생하는 대규모 Fan-out 트래픽 환경에서 네트워크 오버헤드를 최소화해야 합니다.
- **성능 예산(Latency Budget):** 전체 배송 약속 계산 SLO가 50ms로 매우 타이트하며, 재고 조회가 전체 성능의 병목이 될 가능성이 큽니다.
- **강한 의존성 및 가용성 전략:** 재고 정보는 배송 약속 계산의 Critical Path입니다. 정보 없이는 계산 자체가 불가능하므로, 실패 시 즉시 '품절' 처리하는 **Fail-fast 전략**을 취해야 합니다.

---

## 2. Agenda (논의 및 결정 사항)

### 2.1. 재고 데이터의 실시간성 및 서비스 수준(SLO) 정의

- **질문 1:** 실시간성(Strong Consistency) 확보가 필수인가? 캐싱이나 복제본(Stale Data)을 사용하는 방식이 오판매 리스크를 감수할 만큼의 성능 이득을 주는가?
- **질문 2:** 140,000 TPS 상황에서 '최신 재고'로 간주할 수 있는 시간적 오차 범위(Staleness)는 얼마인가? 재고 시스템이 보장해야 할 단일 및 대량 조회(Fan-out)의 P99 응답 시간 목표는 무엇인가?
- **질문 3:** 모든 레이어에서 동일한 전략을 유지할 것인가, 아니면 상위 노출(PLP/PDP)과 실제 결제(Checkout) 레이어의 전략을 분리할 것인가?

### 2.2. 통신 매개체 및 라우팅 전략 선정

- **선택지:** Service Mesh (Envoy), Messaging Channel (Redis Pub/Sub), Client-side Load Balancing (Direct gRPC) 중 최적의 방안은 무엇인가?
- **평가 기준:** 140,000 TPS 환경에서의 네트워크 홉(Hop) 수, 지연 시간(Latency), 운영 복잡도 및 애플리케이션 코드 수정 여부.

### 2.3. 인프라 기술 스택 확정 및 운영 안정성 검증

- **검토 사항:** Envoy 및 Istio 제어 평면(Control Plane)의 도입 타당성, 리소스 사용량, 장애 발생 시의 복구 전략(SPOF 방지).
- **조직 역량:** 운영 조직(SRE/DevOps)의 성숙도와 학습 비용(Learning Tax)을 고려할 때 ALB 등 익숙한 기술로 요구사항을 커버할 수 있는가?

---

## 3. Technical Analysis (기술 조사 및 분석)

### 3.1. 지연 시간의 두 차원 분석: Read Time vs Staleness

- **시스템 지연 시간 (Read Time):** 요청부터 응답까지의 시간(RTT + Processing). API SLO 달성에 영향을 주며 길어지면 시스템 마비를 초래합니다.
- **데이터 지연 시간 (Staleness):** 실제 물리 재고와 조회 데이터 간의 시차. 길어지면 실제론 품절임에도 '재고 있음'으로 판단하여 오판매를 발생시킵니다.

### 3.2. 시나리오별 실시간성 요구 수준


| 시나리오 | 결과 | 비즈니스 손실 유형 | 시스템 전략 |

| --- | --- | --- | --- |

| **주문서 작성/장바구니** | 오판매(Overselling), 결제 실패 | 강제 취소 비용, CS 폭주, 브랜드 가치 하락 | **Strong Consistency** |

| **상품 상세 (PDP)** | 약속 시간 오안내 | 구매 전환율 급감, 신뢰도 저하 | **Real-time** |

| **상품 목록 (PLP)** | 정보 불일치 (낚시성) | 사용자 경험 및 클릭 효율 하락 | **Near Real-time** |

### 3.3. 인기 상품(Hot SKU) 변동 주기 추정 (Business Calculation)

초당 800건의 주문(Write)이 발생하는 환경에서 파레토 법칙을 적용한 계산 결과입니다.

- **집중도 10% (초인기 상품):** 초당 80회 변동 → **12.5ms마다 재고 1개 감소**.
- **집중도 5%:** 초당 40회 변동 → **25ms마다 재고 1개 감소**.
- **분석 결과:** Staleness가 100ms인 경우, 그사이 이미 4~8개의 재고가 판매되었음에도 시스템은 이전 수량을 보여주게 되어 임계 상황(Critical Stock)에서 즉각적인 오판매로 연결됩니다.

### 3.4. 통신 방식별 네트워크 처리 비용 (Inter-AZ Worst Case)

AWS 인프라 지표(같은 AZ 0.1~0.3ms, 다른 AZ 0.5~2ms, Loopback 0.01ms) 기반 분석입니다.

지연 시간은 musinsa AWS 계정에서 network analyzer 를 사용해 지난 2주간의 데이터로 측정했습니다.

![image-20251226-044505.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/256348236/image-20251226-044505.png?version=1&modificationDate=1766724307111&cacheVersion=1&api=v2&width=746&height=337)![image-20251226-044519.png](https://wiki.team.musinsa.com/wiki/download/thumbnails/256348236/image-20251226-044519.png?version=1&modificationDate=1766724320488&cacheVersion=1&api=v2&width=800&height=402)

- **Direct gRPC (~2.2ms):** Cross AZ RTT 1회(2.0ms) + 직렬화 0.2ms. 물리 지연은 최저이나 앱이 부하 분산/재시도를 직접 수행해야 하여 CPU 점유율 상승 리스크가 있음.
- **Envoy Sidecar (~3.02ms):** Loopback 0.02ms + Cross AZ RTT 2.0ms + 사이드카 연산 1.0ms. 선형적 확장성을 제공하며 대기열 포화 리스크가 가장 낮음.
- **Nginx Ingress (~6.0ms+):** Cross AZ RTT 2회(4.0ms) + L7 처리 2.0ms+. 중앙 집중형 구조로 큐잉 발생 시 P99가 수십~수백 ms로 급격히 악화될 수 있음.
- **Redis Pub/Sub (~18ms+):** Cross AZ RTT 4회(8.0ms) + 엔진 처리 10ms+. 140k TPS 시 초당 56만 건 메시지 발생으로 싱글 스레드 엔진 포화 및 컨텍스트 스위칭 비용 폭발 리스크가 매우 큼.

### 3.5. 상세 기술 및 운영 리스크 비교

- **Envoy (Sidecar):**

  - **리소스:** 1,000 TPS당 약 0.5 vCPU, 50MB 메모리 소모.
  - **강점:** L7 레벨 멀티플렉싱으로 모든 Pod에 부하를 균등 분산(Least Request)하여 Sticky Connection 문제를 원천 차단함.
  - **안정성:** Istiod가 중단되어도 캐싱된 규칙으로 동작 지속. 장애 파드 발생 시 0.1초 이내 전파 및 30초간 트래픽 배제(Outlier Detection) 수행.
- **Nginx/ALB:**

  - **한계:** gRPC 커넥션 유지 특성상 부하 분산이 완벽하지 않아 Hotspot 발생 확률이 높음.
  - **리스크:** 배포 시 커넥션을 재맺는 과정에서 **"Thundering Herd"** 현상 발생 시 Latency가 100ms 이상 튀며 구식 데이터(Stale) 노출 위험이 있음. 이를 방어하기 위해 3~5배의 Over-provisioning 필요.
- **종합 ROI 분석:**

  - **Nginx/ALB:** 단기 런칭 및 운영 편의성은 높으나, 피크 시 신선도 보장이 도전적임.
  - **Envoy/Istio:** 초기 학습 곡선 및 전담 프로젝트 수준의 공수가 필요하나, 장기적으로 대규모 확장성 및 운영 자동화 확보 가능.
  - **운영 참고:** Service Platform 팀에서 UnifiedMeshDX 도입 목표 및 운영 지식을 보유하고 있어 도입 타당성이 높음.

---

## 4. Decision

### 4.1. 재고 데이터의 실시간성 및 서비스 수준(SLO) 정의

- **신선도 기준:** 2,600만 개의 상품 중 주문이 집중되는 **상위 5% 상품의 변동 주기(25ms)를 고려하여 시스템 Staleness를 25ms 이내로 보장**하는 것을 목표로 합니다.
- **응답 시간 SLO:** 단일 및 Fan-out 조회를 포함한 재고 조회 **P99 Latency를 10ms 이내**로 확정합니다.
- **차등 적용:** 주문 및 결제 관련 레이어는 엄격한 Strong Consistency를 유지하며, 조회성 상위 레이어는 시스템 부하에 따라 Near Real-time 전략을 수용하되 최신성을 최대한 유지합니다.

### 4.2. 통신 매개체 및 라우팅 전략 선정

- **진행 상황:** Service Platform 팀 조사 결과, Envoy 기반 시스템 도입 계획이 있거나 이미 일부 도입되어 있는 것으로 확인되었습니다.
- **결정:** **Service Platform 팀과 세부 도입 현황 및 계획을 논의한 후 최종 확정합니다.**
- **차선책:** 만약 Envoy 도입이 불가능할 것으로 판단될 경우, 익숙한 운영 노하우를 가진 **Nginx를 대안으로 검토**하여 차선책을 마련합니다.

  - 불가능 할 것으로 판단되는 기준

    - Service Platform 팀의 운영 안정성 우려나 극복 불가능한 기술적 한계점이 존재하는 경우
    - Envoy proxy 를 도입하는 것의 공수가 매우 크며 충분히 ALB 로 대체 가능하다고 판단되는 경우

### 4.3. 인프라 기술 스택 확정 및 운영 안정성 검증

- **Service Platform 팀에서는 Istio 및 Envoy Proxy**를 도입한 상태 ([관련 문서](https://wiki.team.musinsa.com/wiki/spaces/PRODUCTS/pages/256348236/Promise+Inventory#4.3.-%EC%9D%B8%ED%94%84%EB%9D%BC-%EA%B8%B0%EC%88%A0-%EC%8A%A4%ED%83%9D-%ED%99%95%EC%A0%95-%EB%B0%8F-%EC%9A%B4%EC%98%81-%EC%95%88%EC%A0%95%EC%84%B1-%EA%B2%80%EC%A6%9D))
- **운영 대응:** Service Platform 팀의 전문 지식과 기존 레퍼런스를 적극 활용하여 학습 곡선(Learning Tax) 문제를 해결합니다.
- **가용성 보장:** Envoy의 Circuit Breaking 및 Outlier Detection 기능을 활용하여 특정 파드 장애가 전체 시스템의 Staleness로 전파되는 것을 차단하고, Fail-fast 전략을 인프라 레벨에서 구현합니다.

  - **action plan: Service platform 팀과 논의를 위해 Promise 에서 사용할 istio envoy sidecar 의 기능과 요구사항 정리 후 미팅 잡기**