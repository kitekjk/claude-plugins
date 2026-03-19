# spec-from-design 플러그인 생성 명세서

## 1. 배경

HLD/LLD 설계 문서 및 개발요청서(Dev request)에서 코드 생성 가능한 Spec을 추출하는 멀티 에이전트 플러그인을 만든다.
가장 중요한 설계 과제는 **Use Case 식별 및 분류의 정확성**이다.
또한, 엣지 케이스를 포함한 다양한 **테스트 시나리오**를 제공한다.

### 1.1 해결해야 할 핵심 난제

LLM 기반 Spec 생성 시 반복적으로 발생하는 문제들이다. 이 플러그인은 아래 문제를 구조적으로 해결해야 한다.

| 문제 | 원인 | 해결 방향 |
|------|------|----------|
| LLM이 LLD 내용("모델 변경", "도메인 로직") 보고 usecase → service로 오분류 | 키워드 기반 판단 | 진입점 유형 기반 분류로 전환 |
| 여러 구현 클래스를 하나의 Spec으로 묶음 | 타입 단위(Temporal Activity 등)로 묶으려는 경향 | 각 구현 클래스 = 하나의 Spec 원칙 강제 |
| soft rule(비유, 가이드라인)을 LLM이 무시 | 프롬프트 기반 가드레일의 한계 | 구조적 제약(에이전트 분리, 검증 게이트)으로 대체 |

### 1.2 설계 원칙

1. **식별 단위는 구현 클래스**: "Temporal Activity"라는 타입이 아니라, 각 ActivityImpl 클래스가 개별 Spec의 단위
2. **유형 판단은 진입점으로**: LLD 내용(모델 변경, 상태 전이 등)이 아니라, 진입점 유형으로 분류
3. **프롬프트가 아니라 구조로 강제**: 식별과 작성을 에이전트 수준에서 분리하여 오류 전파 차단

---

## 2. 설계 목표

### 2.1 핵심 목표
- **Use Case를 정확하게 식별하고 분리**하는 것
- 각 구현 클래스(ActivityImpl, Controller, KafkaConsumer 등)가 **독립된 하나의 Spec**으로 생성되어야 함

### 2.2 필수 요구사항
- [ ] 멀티 에이전트 구조 (orchestrator → analyzer → identifier → **identification-verifier** → policy-extractor → writer → **scope-evaluator** → **usecase-splitter**(조건부) → test-scenario-writer → reviewer)
- [ ] contract.json 단일 기준 원칙
- [ ] Spec 유형 체계 (usecase, model, service, refactoring, performance)
- [ ] Policy 추출 (policy-extractor)
- [ ] 테스트 시나리오 생성 (test-scenario-writer)
- [ ] 품질 평가 체크리스트 (output-quality, traceability)
- [ ] No-code 원칙 (Spec에 코드 금지, Pseudocode는 허용)
- [ ] 단일 파일 원칙 (1 Spec = 1 파일)
- [ ] Foundation 문서 생성 (service-definition, architecture-rules, naming-guide)
- [ ] 기존/신규 프로젝트 모드 지원
- [ ] preset 시스템

### 2.3 설계 핵심 사항

- [ ] **Use Case 식별 알고리즘**: 진입점 유형 기반의 구체적인 식별 절차 수립
- [ ] **식별과 작성의 에이전트 분리**: 식별 전담 에이전트와 작성 전담 에이전트를 분리하여 역할 혼동 방지
- [ ] **구조적 가드레일**: 프롬프트 규칙이 아닌, 에이전트 간 데이터 흐름으로 제약을 강제
- [ ] **매핑 규칙 정밀화**: LLD → Spec 변환 규칙을 진입점 유형별로 구체화

---

## 3. Use Case 식별 규칙 (핵심 설계 영역)

### 3.1 식별 단위

**원칙: 각 구현 클래스 = 하나의 API = 하나의 Spec**

| 진입점 유형 | 식별 단위 | 예시 |
|------------|----------|------|
| REST API | Controller의 각 엔드포인트 메서드 | `POST /api/orders` → Spec 1개 |
| Temporal Activity | 각 ActivityImpl 클래스 | `SapPoSendActivityImpl` → Spec 1개 |
| Temporal Workflow | 각 WorkflowImpl 클래스 | `PoProcessingWorkflowImpl` → Spec 1개 |
| Kafka Consumer | 각 Consumer 클래스 | `OrderEventConsumer` → Spec 1개 |
| Scheduler | 각 Scheduler 메서드 | `@Scheduled dailySync()` → Spec 1개 |

### 3.2 식별 절차

1. LLD의 클래스/컴포넌트 설계에서 **모든 구현 클래스**를 열거
2. 각 클래스가 위 진입점 유형에 해당하는지 판별
3. 해당하면 **각각 독립된 usecase Spec**으로 생성
4. 해당하지 않으면 (내부 서비스, 도메인 모델 등) → Spec 대상에서 제외 (다른 Spec의 "수정 대상 파일"에만 등장)

### 3.3 분류 규칙

- **기본 유형은 항상 usecase**: LLD 내용에 "모델 변경", "도메인 로직", "상태 전이" 등이 포함되더라도 유형을 변경하지 않음
- **model/service는 분해 전용**: 단일 usecase Spec이 너무 클 때만 분해 산출물로 생성
- **refactoring**: LLD에서 명시적으로 "리팩토링"으로 분류한 항목만
- **performance**: LLD에서 명시적으로 "성능 개선"으로 분류한 항목만

---

## 4. 에이전트 아키텍처

### 4.1 에이전트 구조

**식별 에이전트를 분리하여 식별과 작성의 역할을 명확히 나눈다.**

```
spec-orchestrator (조율)
  → design-analyzer (HLD/LLD 파싱 + Foundation 문서 생성)
  → usecase-identifier (Use Case 식별 전담 — 식별 목록만 산출)
  → identification-verifier (식별 결과 검증 — 완전성·1:1 매핑 확인)
  → policy-extractor (정책 추출)
  → usecase-writer (Spec 작성 — 검증된 UC 목록 기반, 무조건 1 UC = 1 파일)
  → scope-evaluator (규모 판단 — 각 Spec의 분해 필요 여부 판정)
  → usecase-splitter (조건부 — 대규모 UC를 model/service Spec으로 분해)
  → test-scenario-writer (테스트 시나리오)
  → spec-reviewer (품질 검증)
```

### 4.2 에이전트 역할 정의

| 에이전트 | 역할 | 입력 | 출력 |
|---------|------|------|------|
| spec-orchestrator | 전체 파이프라인 조율 | 사용자 요청 + HLD/LLD | 최종 Spec 세트 |
| design-analyzer | HLD/LLD 파싱, Foundation 문서 생성 | HLD/LLD 파일 | 파싱된 설계 정보 + Foundation 문서 |
| usecase-identifier | 구현 클래스 열거 → Use Case 식별 | 파싱된 설계 정보 | UC 식별 목록 (클래스명, 진입점 유형, 도메인) |
| identification-verifier | 식별 결과 검증 | UC 식별 목록 + 파싱된 설계 정보 | 검증 결과 (pass/fail + 누락·중복 리포트) |
| policy-extractor | 정책/규칙 추출 | HLD/LLD | Policy 파일 |
| usecase-writer | 검증된 UC 목록 기반 Spec 작성 (무조건 1 UC = 1 파일) | 검증된 UC 식별 목록 + 파싱된 설계 정보 | Spec 파일 |
| scope-evaluator | 각 Spec의 규모 판단, 분해 필요 여부 판정 | Spec 파일 | 판정 결과 (pass / split-needed + 분해 근거) |
| usecase-splitter | 대규모 UC를 model/service Spec으로 분해 (조건부 실행) | split-needed Spec + 파싱된 설계 정보 | 원본 Spec 축소 + 분해된 model/service Spec |
| test-scenario-writer | 테스트 시나리오 생성 | Spec 파일 | Spec 파일 내 테스트 시나리오 섹션 |
| spec-reviewer | 품질 검증 | 전체 Spec 세트 | 검증 리포트 |

---

## 5. 품질 게이트

### 5.1 체크리스트

- [ ] input-quality.md — 입력(HLD/LLD) 품질 검증
- [ ] output-quality.md — 8개 카테고리, 100점 만점
- [ ] traceability.md — HLD/LLD → Spec 추적성
- [ ] **identification-completeness.md** — LLD에 있는 구현 클래스가 모두 Spec으로 식별되었는지
- [ ] **one-to-one-mapping.md** — 하나의 구현 클래스가 정확히 하나의 Spec에 매핑되었는지

---

## 6. 산출물 구조

### 6.1 Spec 파일

```markdown
# SPEC-{PREFIX}-{DOMAIN}-{number}-{name}

## 기본 정보
- 유형: usecase | model | service | refactoring | performance
- 도메인: {도메인}
- 출처: {LLD 참조}

## 개요
...

## 수정 대상 파일
...

## 의존성 (dependsOn)
...

## 기본 흐름
1. ...
2. ...

## 대안 흐름
...

## 검증 조건
...

## 테스트 시나리오
...

## 관련 정책
...
```

### 6.2 디렉토리 구조

```
docs/
├── specs/          # Spec 파일
├── policies/       # Policy 파일
├── service-definition.md
├── architecture-rules.md
└── naming-guide.md
```

---

## 7. 제약 사항

### 7.1 절대 규칙
- Spec에 코드 포함 금지 (자연어만)
- 1 Spec = 1 파일
- contract.json이 단일 기준

### 7.2 프로젝트 컨텍스트
- 대상 아키텍처: DDD + Clean Architecture + Kotlin/Spring Boot (preset으로 관리)
- 주요 진입점: REST API, Temporal Workflow/Activity, Kafka Consumer
- 도메인 특성: SCM(공급망 관리) — PO, 입고, RFID, SAP 연동 등

---

## 8. 실행 요청

위 명세를 기반으로 `spec-from-design` 플러그인을 **처음부터 생성**해 주세요.
기존 코드를 참조하지 말고, 이 문서만으로 완성하세요.

### 8.1 작업 범위
1. contract.json 설계
2. 에이전트 정의 (agents/*.md)
3. Spec 유형 정의 (specs/*.md)
4. 매핑 규칙 (mappings/*.md)
5. 템플릿 (templates/*.md)
6. 체크리스트 (checklists/*.md)
7. SKILL.md 작성
8. plugin.json 작성 (v2.0.0)

### 8.2 우선순위
1. **Use Case 식별 정확성** — 가장 중요
2. **에이전트 간 역할 분리** — 식별과 작성의 명확한 분리
3. **품질 검증** — 식별 완전성 + 1:1 매핑 검증
4. 나머지 기능

### 8.3 검증 기준
- [ ] LLD를 입력했을 때, 각 ActivityImpl이 개별 Spec으로 분리되는가?
- [ ] "모델 변경"을 다루는 Activity가 usecase로 정확히 분류되는가?
- [ ] model/service 유형이 분해 없이 단독 생성되지 않는가?
