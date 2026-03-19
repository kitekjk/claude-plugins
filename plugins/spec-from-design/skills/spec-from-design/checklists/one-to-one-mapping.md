# 1:1 매핑 체크리스트 (one-to-one-mapping)

> **사용 시점**: identification-verifier(③)가 usecase-identifier 결과 검증 시 적용
> **목적**: 각 구현 클래스가 정확히 하나의 Spec에만 매핑되었는지 검증

---

## 핵심 원칙

```
각 구현 클래스 = 하나의 Spec (1:1 매핑)
```

- 하나의 클래스 → 여러 Spec = **중복 매핑** (금지)
- 여러 클래스 → 하나의 Spec = **병합 매핑** (금지)

---

## 1. 중복 매핑 검출 (1 클래스 → N Spec)

> 동일한 구현 클래스가 여러 UC에 등록된 경우를 탐지합니다.

### 체크 항목

- [ ] **OM-01** UC 식별 목록에서 동일한 구현 클래스명이 2회 이상 등장하지 않는가?
- [ ] **OM-02** 같은 클래스를 참조하는 Spec 파일이 2개 이상 생성되지 않았는가?
- [ ] **OM-03** Controller의 경우, 각 엔드포인트 메서드가 별도의 UC로 분리되었는가? (메서드 단위 분리 허용)

### 중복 매핑 탐지 방법

```
UC 식별 목록의 `구현 클래스` 컬럼에서 중복 값 탐색:
  - 동일 클래스명이 2개 이상 → 중복 매핑 오류
  - Controller의 메서드 단위 분리는 예외 허용
    예: OrderController.createOrder → UC-001
        OrderController.cancelOrder → UC-002 (허용)
```

### 중복 매핑 보고 형식

```
[1:1 매핑 위반: 중복 매핑]
위반 클래스: SapPoSendActivityImpl
매핑된 UC:
  - UC-003: sap-po-send (진입점: Temporal Activity)
  - UC-007: sap-po-retry (진입점: Temporal Activity)

동일 클래스가 두 UC에 매핑되었습니다.
조치: 하나의 UC로 통합하거나, 실제로 두 개의 서로 다른 클래스인지 LLD를 재확인하세요.
```

---

## 2. 병합 매핑 검출 (N 클래스 → 1 Spec)

> 여러 구현 클래스가 하나의 UC에 묶인 경우를 탐지합니다.

### 체크 항목

- [ ] **OM-04** 각 UC 항목의 `구현 클래스` 필드에 클래스가 하나만 기재되어 있는가?
- [ ] **OM-05** "ActivityImpl들 모두", "관련 Consumer 전체" 같은 집합 표현이 없는가?
- [ ] **OM-06** 하나의 UC Spec이 여러 클래스의 기능을 모두 기술하지 않는가?

### 병합 매핑 탐지 방법

```
UC 식별 목록의 `구현 클래스` 컬럼에서 복수 클래스가 기재된 항목 탐색:
  - "SapPoSendActivityImpl, SapPoRetryActivityImpl" → 병합 매핑 오류
  - 별도 행으로 분리되어야 함:
    UC-003: SapPoSendActivityImpl
    UC-004: SapPoRetryActivityImpl
```

### 병합 매핑 보고 형식

```
[1:1 매핑 위반: 병합 매핑]
위반 UC: UC-005 po-processing
구현 클래스 (복수):
  - PoProcessingWorkflowImpl
  - PoStatusUpdateActivityImpl

여러 클래스가 하나의 UC로 묶였습니다.
조치: 각 클래스당 별도의 UC를 생성하세요.
```

---

## 3. UC 식별 목록 매핑 테이블

> identification-verifier가 이 테이블을 검증합니다.

| UC ID | 구현 클래스 | 진입점 유형 | 중복 매핑 여부 | 병합 매핑 여부 | 상태 |
|-------|-----------|-----------|-------------|-------------|------|
| UC-001 | | | N | N | pass |
| UC-002 | | | N | N | pass |

---

## 4. Temporal 분리 검증

WorkflowImpl과 ActivityImpl은 서로 다른 진입점 유형이므로, 동일한 기능을 구성하더라도 반드시 별도 UC로 식별되어야 합니다.

### 체크 항목

- [ ] **OM-09** 동일 UC에 WorkflowImpl과 ActivityImpl이 공존하지 않는가?
  - 탐지: UC 식별 목록 또는 Spec 본문에서 `*WorkflowImpl`과 `*ActivityImpl`이 동일 UC에 등장하면 병합 매핑 오류
  - 예: `PoCancelWorkflowImpl` + `PoCancelActivityImpl` → 반드시 별도 UC
- [ ] **OM-10** 동일 UC에 서로 다른 ActivityImpl 클래스가 2개 이상 포함되지 않는가?
  - 탐지: UC 식별 목록 또는 Spec 본문에서 서로 다른 `*ActivityImpl`이 동일 UC에 등장하면 병합 매핑 오류
  - 예: `SapPoSendActivityImpl` + `RfidProductTagOrderActivityImpl` → 반드시 별도 UC

### Temporal 병합 매핑 보고 형식

```
[1:1 매핑 위반: Temporal 병합 매핑]
위반 UC: UC-003 activity-state-transition
병합된 클래스:
  - SapPoSendActivityImpl (진입점: Temporal Activity)
  - RfidProductTagOrderActivityImpl (진입점: Temporal Activity)
  - RfidProductAssortInfoActivityImpl (진입점: Temporal Activity)

서로 다른 ActivityImpl이 하나의 UC로 묶였습니다.
조치: 각 ActivityImpl을 별도의 UC로 분리하세요.
```

---

## 5. Controller 엔드포인트 분리 규칙

Controller는 클래스 단위가 아니라 **엔드포인트 메서드 단위**로 UC를 식별합니다.

| 처리 방법 | 예시 |
|---------|------|
| 올바름 | `POST /api/orders` → UC-001, `DELETE /api/orders/{id}` → UC-002 |
| 잘못됨 | `OrderController 전체` → UC-001 (메서드 혼합) |

### 체크 항목

- [ ] **OM-07** Controller가 있는 경우, 각 HTTP 메서드(엔드포인트)가 별도 UC로 분리되었는가?
- [ ] **OM-08** 하나의 엔드포인트가 여러 UC로 분리되지 않았는가?

---

## 6. 최종 판정

| 판정 | 조건 |
|------|------|
| **pass** | OM-01~OM-10 모든 항목 통과 |
| **fail** | OM-01, OM-04, OM-07, OM-09, OM-10 중 하나라도 미통과 |
| **warn** | OM-03, OM-05, OM-08 일부 미통과 (피드백 후 진행 가능) |

---

## 7. 통계 요약

```
UC 식별 목록 전체 항목 수:         ___
  중복 매핑 위반 (1클래스→N UC):   ___  ← 0이어야 pass
  병합 매핑 위반 (N클래스→1 UC):   ___  ← 0이어야 pass
  Temporal 병합 위반:              ___  ← 0이어야 pass
  Controller 엔드포인트 분리 준수:  ___ / ___ (준수/전체)
```

---

## 8. 재시도 안내

identification-verifier가 fail을 반환하면 orchestrator는 usecase-identifier를 피드백과 함께 재실행합니다.

- 최대 재시도: 2회 (총 3회 시도)
- 재시도 초과 시: 사용자에게 보고, 수동 수정 요청
- 재시도 피드백 형식: 중복/병합 위반 목록 + 조치 안내
