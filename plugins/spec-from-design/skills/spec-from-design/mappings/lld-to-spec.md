# LLD → Spec 변환 매핑 가이드

## 섹션별 매핑

| LLD 섹션 | 생성되는 Spec | 담당 | 변환 방식 |
|----------|-------------|------|----------|
| Problem Statement | Use Case 개요 | usecase-api-writer | 기술 배경 → 비즈니스 배경 |
| FR | Use Case 흐름 + 검증 조건 | usecase-api-writer | FR 1개 → Use Case 1개 또는 흐름 |
| FR 검증 기준 | 테스트 Given-When-Then | test-scenario-writer | 검증 기준 → Then 절 |
| NFR | NFR 정책 수치 보강 | policy-extractor | 목표 + 측정방법 → 정책 상세 |
| Goal | Use Case 기본 흐름 | usecase-api-writer | 목표 → 시스템 동작 단계 |
| Non-Goal | Spec 범위 제한 메모 | usecase-api-writer | 불포함 명시 |
| API 설계 | API Spec | usecase-api-writer | 1:1 매핑 |
| 클래스 설계 | Use Case 기본 흐름 상세 | usecase-api-writer | 메서드 순서 → 흐름 단계 |
| DB 스키마 | 모델 필드 + 검증 조건 | usecase-api-writer | 컬럼 타입/제약 → 검증 조건 |
| 설계 판단 근거 | 정책 규칙, 대안 흐름 | policy-extractor | 채택→정책, 탈락→"하지 않는다" |
| 트레이드오프 | 정책 제약 조건 | policy-extractor | 단점 → 알려진 제약 |
| 미해결 리스크 | 엣지 케이스 테스트 | test-scenario-writer | 리스크 → 네거티브 테스트 |
| Appendix 시뮬레이션 | Integration 테스트 | test-scenario-writer | 시뮬레이션 → Given-When-Then |

## FR → Use Case 변환 상세

```text
LLD FR:
  FR-01: {요구사항}
  우선순위: P0
  검증 기준: {검증 기준}

→ Use Case:
  기본 흐름 Step N: {요구사항을 시스템 동작으로}
  검증 조건: {검증 기준을 테스트 가능 문장으로}

→ 테스트 시나리오:
  Given: {검증 기준의 전제 조건}
  When: {검증 기준의 트리거}
  Then: {검증 기준의 기대 결과}
```

## 미해결 리스크 → 테스트 변환

```text
LLD 리스크:
  리스크: {리스크 설명}
  영향도: 높음
  완화 방안: {완화 방안}

→ 테스트 시나리오:
  Given: {리스크가 발생하는 조건}
  When: {시스템이 동작할 때}
  Then: {완화 방안이 정상 작동하는지 검증}
```

## 설계 판단 → 정책/제약 변환

```text
LLD 설계 판단:
  결정: {결정}
  채택: {옵션 A}
  탈락: {옵션 B}
  근거: {근거}
  감수하는 단점: {단점}

→ 정책 규칙:
  규칙: {채택 옵션을 규칙으로}
  근거: {근거}
  제약: {감수하는 단점을 알려진 제약으로}

→ 제약 확인 테스트:
  Given: {단점이 발생하는 조건}
  When: {시스템 동작}
  Then: {단점이 실제로 발생하고 허용 범위 이내인지 확인}
```
