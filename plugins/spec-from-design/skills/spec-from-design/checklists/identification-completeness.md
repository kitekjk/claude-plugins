# 식별 완전성 체크리스트 (identification-completeness)

> **사용 시점**: identification-verifier(③)가 usecase-identifier 결과 검증 시 적용
> **목적**: LLD의 모든 진입점 구현 클래스가 UC 식별 목록에 빠짐없이 포함되었는지 확인

---

## 진입점 정의

아래 유형이 진입점입니다. contract.json의 `identificationRules.entryPoints`와 동기화되어야 합니다.

| 진입점 유형 | 클래스 패턴 | 식별 기준 |
|-----------|-----------|---------|
| REST API | `*Controller` | `@RestController`, `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` / `@PatchMapping` |
| Temporal Activity | `*ActivityImpl` | `implements *Activity` |
| Temporal Workflow | `*WorkflowImpl` | `implements *Workflow` |
| Kafka Consumer | `*Consumer` / `*EventListener` | `@KafkaListener` |
| Scheduler | `@Scheduled` 메서드를 포함하는 클래스 | `@Scheduled` 어노테이션 |

> customEntryPoints가 있는 경우 contract.json을 확인하여 이 표에 추가합니다.

---

## 1. 전수 식별 확인

### 절차

1. LLD의 클래스/컴포넌트 설계 섹션에서 모든 구현 클래스를 열거합니다.
2. 각 클래스에 대해 진입점 유형 해당 여부를 판별합니다.
3. 진입점 해당 클래스가 UC 식별 목록에 포함되어 있는지 확인합니다.

### 체크 항목

- [ ] **IC-01** LLD의 모든 구현 클래스가 열거되었는가? (클래스 개수 확인)
- [ ] **IC-02** 각 클래스에 대해 진입점 유형 해당 여부가 판별되었는가?
- [ ] **IC-03** 진입점으로 분류된 모든 클래스가 UC 식별 목록에 포함되었는가?
- [ ] **IC-04** 진입점으로 분류되지 않은 클래스의 제외 사유가 명시되었는가?

---

## 2. 클래스 분류 매핑 테이블

> identification-verifier가 이 테이블을 채워 검증합니다.

| 클래스명 | LLD 위치 | 진입점 해당 | 진입점 유형 | UC 식별 목록 포함 | 제외 사유 |
|--------|---------|-----------|-----------|----------------|--------|
| | | Y / N | | Y / N / 해당없음 | |

---

## 3. 제외 대상 분류 기준

진입점이 아닌 클래스는 UC 식별 목록에서 제외합니다. 제외 시 반드시 사유를 기록합니다.

| 제외 유형 | 설명 | 예시 |
|---------|------|------|
| 내부 서비스 | 외부 요청을 직접 수신하지 않는 도메인 서비스 | `OrderDomainService`, `PricingCalculator` |
| 도메인 모델 | 엔티티, 값 객체, 애그리거트 | `Order`, `OrderItem`, `Money` |
| 포트/어댑터 | Repository 구현체, 외부 API 클라이언트 | `OrderPersistenceAdapter`, `SapApiClient` |
| 설정 클래스 | Spring Configuration, 인프라 설정 | `DataSourceConfig`, `SecurityConfig` |
| 유틸리티 | 공통 유틸, 헬퍼 클래스 | `DateUtils`, `JsonMapper` |

### 제외 항목 체크

- [ ] **IC-05** 제외된 모든 클래스에 제외 유형과 사유가 기록되었는가?
- [ ] **IC-06** "판단 불가" 상태인 클래스가 없는가? (모호한 클래스는 사용자 확인 요청)
- [ ] **IC-07** 내부 서비스로 분류된 클래스가 실제 외부 진입점 역할을 하지 않는가?

---

## 4. 누락 검출

### 누락 판정 조건

- LLD 클래스/컴포넌트 설계에 명시된 클래스가 UC 식별 목록에도 없고 제외 목록에도 없는 경우

### 체크 항목

- [ ] **IC-08** LLD 전체 클래스 수와 (UC 목록 + 제외 목록) 합계가 일치하는가?
- [ ] **IC-09** 분류 미완료(미처리) 클래스가 없는가?

### 누락 보고 형식

```
[식별 완전성 검증 실패]
누락된 클래스:
  - OrderEventConsumer (LLD 3.2절): UC 목록에 없고 제외 목록에도 없음
    → Kafka Consumer 진입점으로 판단됨. usecase-identifier 재실행 필요.

  - SapPoSendActivityImpl (LLD 3.4절): UC 목록에 없음
    → 제외 사유가 불명확. 재분류 필요.

조치: usecase-identifier에 위 클래스 포함 여부 피드백 전달.
```

---

## 5. 최종 판정

| 판정 | 조건 |
|------|------|
| **pass** | IC-01~IC-09 모든 항목 통과 |
| **fail** | IC-03, IC-08, IC-09 중 하나라도 미통과 |
| **warn** | IC-05, IC-06, IC-07 일부 미통과 (pifdback 전달 후 진행 가능) |

---

## 6. 통계 요약

```
전체 LLD 구현 클래스 수: ___
  ├── 진입점 분류 (UC 식별 목록): ___
  └── 비진입점 분류 (제외):       ___
      ├── 내부 서비스: ___
      ├── 도메인 모델: ___
      ├── 포트/어댑터: ___
      ├── 설정 클래스: ___
      └── 유틸리티:   ___

미분류 (오류): ___  ← 0이어야 pass
```
