# HLD → Spec 변환 매핑 가이드

## 섹션별 매핑

| HLD 섹션 | 생성되는 Spec | 담당 | 변환 방식 |
|----------|-------------|------|----------|
| Glossary | service-definition.md 용어 정의 | design-analyzer | 직접 복사 + 코드 맥락 보강 |
| Overview (배경/목적) | Use Case 개요 | usecase-api-writer | 목적을 사용자 관점으로 재작성 |
| System Context | infra-config.md, API Spec 연동 | policy-extractor | 외부 시스템별 연동 방식 정리 |
| 상태 전이 모델 | 정책 Spec (상태 전이 규칙) | policy-extractor | 전이 조건 → 정책 규칙 |
| 핵심 컴포넌트 책임 | architecture-rules.md | design-analyzer | 컴포넌트별 레이어 규칙 |
| KDD | 정책 Spec (비즈니스 규칙) | policy-extractor | 결정+근거 → 정책, 단점 → 제약 |
| NFR | POLICY-NFR Spec | policy-extractor | 지표별 정책 규칙 + 검증 기준 |
| Deployment | infra-config.md | policy-extractor | 배포 순서, 롤백 전략 |

## KDD → 정책 변환 상세

```text
HLD KDD 원문:
  결정: {결정 내용}
  선택: {채택 옵션}
  대안: {탈락 옵션}
  근거: {채택 근거}

→ 정책 Spec:
  규칙: {결정을 규칙 문장으로}
  근거: {근거 요약}
  제약: {탈락 옵션의 장점이 누락되는 것을 알려진 제약으로}
  적용 범위: {관련 Use Case ID}
```

## NFR → NFR 정책 변환

```text
HLD NFR:
  항목: P99 Latency
  Target: 500ms
  측정 방법: Prometheus histogram

→ NFR 정책:
  규칙: {엔드포인트} 응답 시간은 P99 500ms 이내여야 한다
  검증 기준: Prometheus histogram으로 측정
  위반 시: 경고 알림 발생
```
