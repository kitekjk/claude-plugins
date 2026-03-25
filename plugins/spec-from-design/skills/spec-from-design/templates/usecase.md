# SPEC-{PREFIX}-{DOMAIN}-{number}-{name}

## 기본 정보

- 유형: usecase
- 도메인: {도메인}
- 출처: {LLD 참조 — 예: LLD Section 3.2 FR-001}
- 진입점 유형: {REST API | Temporal Activity | Temporal Workflow | Kafka Consumer | Scheduler}
- 구현 클래스: {클래스명 — 예: CreateOrderActivityImpl}

## 개요

{이 Use Case가 수행하는 기능을 2~3문장으로 요약한다.
어떤 외부 요청을 받아 무엇을 처리하고 어떤 결과를 반환하는지 기술한다.}

## 수정 대상 파일

{구현 시 변경되는 파일 목록. 각 파일의 역할을 간략히 명시한다.}

- `{패키지.경로.ClassName}` — {역할 설명}
- `{패키지.경로.ClassName}` — {역할 설명}

## 의존성 (dependsOn)

```yaml
dependsOn:
  - specId: {SPEC-PREFIX-DOMAIN-NNN-name}
    reason: {의존 이유}
  - policyId: {POLICY-DOMAIN-NNN}
    reason: {적용 정책 이유}
```

## 기본 흐름

1. {시스템이 {진입점}을 통해 요청을 수신한다.}
2. {입력 유효성을 검증한다.}
3. {핵심 비즈니스 로직을 처리한다.}
4. {결과를 저장하거나 외부 시스템에 전달한다.}
5. {응답을 반환한다.}

## 대안 흐름

### 대안 흐름 A: {조건명}

- 조건: {대안 흐름이 발생하는 조건}
- 처리: {대안 처리 방법}
- 결과: {대안 흐름의 결과}

## 검증 조건

검증의 1차 책임은 도메인 모듈(엔티티, VO, Enum, 도메인 서비스)에 있다.
API 레이어(@Valid 등)는 fast-fail 용도의 2차 검증이며, 도메인 검증을 대체하지 않는다.

| 검증 규칙 | 책임 위치 | 위반 시 에러 |
|-----------|----------|------------|
| {검증 조건 1} | {엔티티/VO/도메인 서비스} | {에러 클래스 또는 에러 코드} |
| {검증 조건 2} | {엔티티/VO/도메인 서비스} | {에러 클래스 또는 에러 코드} |
| {검증 조건 3} | {엔티티/VO/도메인 서비스} | {에러 클래스 또는 에러 코드} |

## 테스트 시나리오

### TC-{DOMAIN}-{number}-01: {시나리오명} [Unit | Integration | E2E]

- **Given**: {사전 조건}
- **When**: {실행 조건}
- **Then**: {기대 결과}

### TC-{DOMAIN}-{number}-02: {시나리오명} [Unit | Integration | E2E]

- **Given**: {사전 조건}
- **When**: {실행 조건}
- **Then**: {기대 결과}

## 관련 정책

- {POLICY-DOMAIN-NNN}: {정책명 및 적용 내용 요약}
