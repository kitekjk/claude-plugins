# {PREFIX}-{DOMAIN}-{번호} {UseCase명}

## 기본 정보
- type: use_case
- domain: {도메인}
- id: {PREFIX}-{DOMAIN}-{번호}
- source: {LLD 문서명} FR-{번호}

## 의존성

```yaml
dependsOn:
  - spec_id: {PREFIX}-{OTHER_DOMAIN}-{번호}
    type: data | api | event
    reason: "{의존 사유}"
```

> 의존성이 없으면 이 섹션을 비워둡니다 (`dependsOn: []`).

## 관련 정책
- POLICY-{DOMAIN}-001 ({정책명})
- POLICY-NFR-001 (비기능 요구사항)

## 관련 Spec
- {PREFIX}-API-{DOMAIN}-{번호}

## 관련 모델
- 주 모델: {design-analyzer 결과}
- 참조 모델: {design-analyzer 결과}

## 개요
{LLD Problem Statement 목표를 사용자 관점으로 재작성}

## 기본 흐름
1. {단계 1 — LLD 클래스 설계 Step 1 대응}
2. {단계 2 — LLD 클래스 설계 Step 2 대응}

## 대안 흐름
- **AF-1: {대안 시나리오}** - {처리 방식. LLD 근거}
- **AF-2: {에러 시나리오}** - {에러코드 + HTTP 상태}

## 검증 조건
- {조건 1 — FR-{번호} 검증 기준에서 도출}
- {조건 2}

## 비기능 요구사항
- {NFR-01: 응답시간 P99 < {목표}ms}

## 테스트 시나리오

### TC-{DOMAIN}-{번호}-01: {정상 시나리오} ({레벨})
- **Given**: {전제 조건}
- **When**: {트리거}
- **Then**: {기대 결과}

### TC-{DOMAIN}-{번호}-02: {에러 시나리오} ({레벨})
- **Given**: {에러 조건}
- **When**: {트리거}
- **Then**: {에러 처리 결과}
