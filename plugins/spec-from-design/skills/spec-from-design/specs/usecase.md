# Use Case Spec 정의

**DDD/Hexagonal 아키텍처의 application layer use case 단위**입니다.
외부에서 시스템으로 요청이 들어올 때, 이를 처리하는 application layer의 use case 각각이 하나의 Spec이 됩니다.
**하나의 Spec은 하나의 파일**로 출력하며, **구현 코드를 포함하지 않습니다**.

## Use Case 식별 기준

Hexagonal 아키텍처에서 외부와 통신하는 레이어(adapter)는 반드시 application layer를 경유합니다.
application layer에는 use case가 들어 있으며, **외부 요청에 대응하는 use case 각각이 하나의 Spec**입니다.

### 외부 요청 경로 (Port/Adapter)

다음은 외부에서 시스템으로 요청이 들어오는 경로입니다. 각 경로에 대응하는 use case를 식별해야 합니다:

| 외부 요청 경로 | 설명 | 예시 |
|--------------|------|------|
| API Controller | REST/GraphQL 엔드포인트로 인입 | PlmPoCancelController |
| Kafka Consumer | Kafka 토픽 메시지 수신 처리 | PoStatusChangeConsumer |
| Temporal Workflow | Temporal 런타임이 워크플로우 실행 | PoCancelWorkflowImpl |
| Temporal Activity | Temporal 런타임이 액티비티 실행 | PoCancelActivityImpl |
| RFC/Socket | 외부 시스템 통신 모듈 진입 | SapRfcReceiver |
| Scheduler/Cron | 스케줄러 트리거 진입 | DailyBatchJob |

### 식별 단위: 구현 클래스

외부 진입점은 **유형이 아니라 구현 클래스 단위**로 식별합니다.

- Temporal Activity가 3개(SapPoSendActivityImpl, RfidProductTagOrderActivityImpl, RfidProductAssortInfoActivityImpl)이면 → use case 3개
- "Temporal Activity"라는 유형으로 묶어서 1개로 만들지 않습니다
- API Controller가 2개(PoCancelController, PoConfirmController)이면 → use case 2개

### 분리 원칙

- 하나의 LLD에 여러 use case가 포함되면 **use case별로 개별 Spec을 생성**합니다
- 서로 다른 외부 경로(예: API + Kafka)가 **동일한 use case를 호출하면 Spec은 하나만** 생성합니다
- 서로 다른 use case는 별도 Spec으로 분리합니다

### 2단계 분류

1. **1단계**: 식별된 모든 use case는 `usecase` 유형입니다. model이나 service 유형을 직접 선택하지 않습니다.
2. **2단계**: 개별 use case가 대규모(파일 10개 초과 또는 FR 5개 초과)이면 model + service + usecase로 분해합니다. model과 service는 이 분해의 산출물로만 존재합니다.

### 예시

PO 취소 처리 LLD에 API Controller, Temporal Workflow, Temporal Activity가 있으면:
- UC-001: PoCancelReceiveUsecase — 취소 요청 수신 및 워크플로우 시작 (API Controller가 호출)
- UC-002: PoCancelWorkflow — 취소 프로세스 오케스트레이션 (Temporal 런타임이 실행)
- UC-003: PoCancelActivity — 취소 처리 개별 액티비티 구현 (Temporal 런타임이 실행)

만약 API와 Kafka Consumer가 모두 PoCancelReceiveUsecase를 호출한다면 UC-001 하나로 통합합니다.

## 출력 규칙

- **단일 파일**: 관련 정책, 모델, 검증 조건, 테스트 시나리오를 모두 하나의 파일에 포함
- **코드 금지**: Java/Kotlin/TypeScript 등 구현 코드, import 문, 어노테이션 포함 금지
- **자연어 기술**: 흐름, 조건, 시나리오는 자연어 문장으로만 기술

## 공통 섹션

모든 Spec 유형에 포함되는 섹션입니다.

| 섹션 | 설명 |
|------|------|
| 기본 정보 | type, domain, id, source |
| 수정 대상 파일 | 구현 시 수정/생성할 파일 목록. dependsOn 판별에 사용 |
| dependsOn | 같은 LLD 내 다른 Spec과 파일 겹침 또는 레이어 선행 관계 |
| 관련 정책 | 정책 Spec ID와 조항 참조 |
| 관련 Spec | 관련 다른 Spec ID |
| 관련 모델 | 주 모델, 참조 모델 (필드 목록 포함) |
| 검증 조건 | 테스트 가능한 자연어 문장 |
| 테스트 시나리오 | Given-When-Then + TC-ID |

## usecase 고유 섹션

| 섹션 | 소스 | 설명 |
|------|------|------|
| 개요 | LLD Problem Statement | 사용자 관점으로 재작성 |
| 기본 흐름 | LLD 클래스 설계 메서드 순서 | 번호 목록 (자연어) |
| 대안 흐름 | LLD 설계 판단 단점 + 리스크 | AF-N 형식 |
| 비기능 요구사항 | LLD NFR | 수치 포함 |

## ID 규칙

- `{PREFIX}-{DOMAIN}-{번호}`
- PREFIX: service-definition에서 결정
- 번호: 001부터 순차

## source 필드

반드시 LLD 문서명과 FR-ID를 명시합니다.
예: `source: po-cancel-request-send LLD FR-01~FR-08`

## 수정 대상 파일 섹션

LLD의 클래스/컴포넌트 설계 섹션에서 도출합니다.
- `code-from-spec`이 구현 범위를 파악하는 데 사용
- 같은 LLD 내 다른 Spec과의 파일 겹침을 `dependsOn`으로 기록

## dependsOn 필드

같은 LLD에서 분해된 다른 Spec과 **수정 대상 파일이 겹치거나** **레이어 선행 관계**가 있을 때 기록합니다.

### 규칙

- **같은 LLD 내 Spec 간에만 적용**
- **수정 파일 겹침**: 동일 파일을 수정하면 병렬 개발 불가
- **레이어 선행 관계**: model → service → usecase 순서
- **단일 Spec이면 반드시 `dependsOn: []`**
