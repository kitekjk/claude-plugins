# HLD → Spec 매핑 규칙 (hld-to-spec)

> **참조 에이전트**: design-analyzer(①), policy-extractor(④), usecase-writer(⑤)
> **목적**: HLD의 각 요소가 어느 Spec 산출물로 매핑되는지 정의

---

## 기본 원칙

HLD는 시스템 전체의 설계 결정을 담습니다. HLD 요소는 개별 UC Spec이 아닌 **Policy 또는 Foundation 문서**로 매핑됩니다.
UC Spec의 세부 흐름은 LLD에서 도출합니다. `lld-to-spec.md`를 참조하세요.

---

## 매핑 테이블

| HLD 요소 | Spec 매핑 대상 | 담당 에이전트 | 비고 |
|---------|--------------|------------|------|
| KDD (핵심 설계 판단) | Policy 규칙 (`POLICY-{DOMAIN}-{N}`) | policy-extractor | KDD 1개 = Policy 규칙 1개 이상 |
| NFR (비기능 요구사항) | NFR Policy (`POLICY-NFR-001`) | policy-extractor | 성능, 가용성, 보안 등을 하나의 NFR Policy로 통합 |
| 상태 전이 모델 | 상태 Policy 규칙 | policy-extractor | 상태 전이 조건이 Policy 규칙으로 추출됨 |
| System Context | `infra-config.md` (Foundation) | design-analyzer | 외부 시스템 연동 목록, 서비스 경계 |
| 서비스 개요 / 스코프 | `service-definition.md` (Foundation) | design-analyzer | 서비스 책임과 경계 정의 |
| 용어 정의 | `naming-guide.md` (Foundation) | design-analyzer | 도메인 용어를 네이밍 가이드에 반영 |
| 아키텍처 결정 | `architecture-rules.md` (Foundation) | design-analyzer | 레이어 규칙, 의존성 방향 |
| 이해관계자 / 제약조건 | `service-definition.md` (Foundation) | design-analyzer | 팀, 기한, 기술 제약 기록 |

---

## 상세 매핑 규칙

### 1. KDD → Policy 규칙

**HLD KDD 예시:**
```
KDD-001: 외부 SAP API 호출 실패 시 최대 3회 재시도 후 DLQ에 적재
```

**매핑 결과 (`POLICY-SCM-001.md`):**
```markdown
## 규칙
- 외부 SAP API 호출 실패 시 최대 3회 재시도 (지수 백오프)
- 3회 재시도 이후에도 실패 시 DLQ(Dead Letter Queue)에 적재
- DLQ 적재 후 알림 발송 (Slack 채널 #ops-alert)

## 제약조건
- 재시도 간격: 1초, 2초, 4초 (지수 백오프)
- DLQ 보존 기간: 7일

## 출처
- HLD KDD-001
```

**매핑 기준:**
- KDD 1개 → Policy 파일 1개 (복잡한 KDD는 여러 규칙으로 분리 가능)
- KDD의 "왜" (근거)는 Policy의 `제약조건`에 반영
- 기존 Policy와 중복되면 `적용 도메인`에 추가하고 새 파일 생성 안 함

---

### 2. NFR → POLICY-NFR-001

**HLD NFR 예시:**
```
- 응답시간: P99 < 500ms
- 가용성: 99.9% (월 43.8분 이하 장애)
- 처리량: 1,000 TPS
```

**매핑 결과 (`POLICY-NFR-001.md`):**
```markdown
## 규칙
- API 응답시간: P99 < 500ms (정상 운영 시)
- 서비스 가용성: 99.9% 이상 (월 기준)
- 최대 처리량: 1,000 TPS

## 측정 방법
- 응답시간: APM 도구 P99 지표 모니터링
- 가용성: 헬스체크 실패율 기반 계산

## 출처
- HLD NFR 섹션 (전체)
```

---

### 3. 상태 전이 모델 → 상태 Policy 규칙

**HLD 상태 전이 예시:**
```
주문 상태: PENDING → CONFIRMED → SHIPPED → DELIVERED
전이 조건: CONFIRMED → SHIPPED: 결제 완료 + 재고 확인 완료
```

**매핑 결과 (Policy 규칙 또는 UC Spec 대안 흐름):**
- 상태 전이 조건 → Policy 규칙
- 각 상태 전이가 포함된 UC의 `대안 흐름`에서 Policy 참조

---

### 4. System Context → infra-config.md

**HLD System Context 예시:**
```
외부 시스템: SAP (ERP), Slack (알림), AWS S3 (파일)
```

**매핑 결과 (`infra-config.md`):**
```markdown
## 외부 시스템 연동
| 시스템 | 용도 | 연동 방식 | 타임아웃 |
|--------|------|----------|---------|
| SAP ERP | PO 데이터 동기화 | REST API | 30초 |
| Slack | 운영 알림 | Webhook | 5초 |
| AWS S3 | 첨부파일 저장 | SDK | 10초 |
```

---

## HLD 요소가 없는 경우 처리

| 상황 | 처리 방법 |
|------|---------|
| HLD 전체 없음 | LLD만으로 진행. Foundation 문서는 기존 것 재사용 또는 코드에서 추출 |
| KDD 없음 | Policy 없이 진행. output-quality Q6에서 감점 가능 |
| NFR 없음 | POLICY-NFR-001 미생성. 경고 로그 남기고 진행 |
| System Context 없음 | infra-config.md 최소 버전 생성 (빈 섹션) |

---

## 추적성 확인

매핑 완료 후 traceability.md의 TR-H-01~TR-H-05 항목을 확인합니다.
