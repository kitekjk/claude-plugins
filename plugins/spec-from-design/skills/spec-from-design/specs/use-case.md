# Use Case Spec 정의

Use Case Spec은 LLD의 Functional Requirements + 클래스 설계에서 도출됩니다.

## 필수 섹션

| 섹션 | 소스 | 설명 |
|------|------|------|
| 기본 정보 | 자동 생성 | type, domain, id, source |
| 의존성 | LLD FR 간 참조 분석 | dependsOn 메타데이터 (cross-domain) |
| 관련 정책 | policy-extractor 결과 | 관련 정책 Spec ID |
| 관련 Spec | 자동 링크 | 관련 API Spec ID |
| 관련 모델 | design-analyzer 결과 | 주 모델, 참조 모델 |
| 개요 | LLD Problem Statement | 사용자 관점으로 재작성 |
| 기본 흐름 | LLD 클래스 설계 메서드 순서 | 번호 목록 |
| 대안 흐름 | LLD 설계 판단 단점 + 리스크 | AF-N 형식 |
| 검증 조건 | LLD FR 검증 기준 | 테스트 가능한 문장 |
| 비기능 요구사항 | LLD NFR (관련 항목) | 수치 포함 |
| 테스트 시나리오 | test-scenario-writer | Given-When-Then + TC-ID |

## ID 규칙

- `{PREFIX}-{DOMAIN}-{번호}`
- PREFIX: service-definition에서 결정
- 번호: 001부터 순차

## source 필드

반드시 LLD 문서명과 FR-ID를 명시합니다.
예: `source: po-cancel-flow LLD FR-01`

## dependsOn 필드

다른 도메인 Spec에 대한 의존성을 명시합니다. `code-from-spec`의 스케줄링에서 실행 순서를 결정하는 데 사용됩니다.

### 의존성 유형

| 유형 | 의미 | 판별 방법 |
|------|------|----------|
| `data` | 다른 도메인의 모델을 참조 | LLD 클래스 설계에서 외부 도메인 엔티티 import |
| `api` | 다른 도메인의 API를 호출 | LLD 시퀀스에서 외부 도메인 서비스 호출 |
| `event` | 다른 도메인의 이벤트에 반응 | LLD 이벤트 흐름에서 외부 도메인 이벤트 구독 |

### 규칙

- **cross-domain만 기록**: 같은 도메인 내부의 Use Case 간 참조는 의존성으로 기록하지 않습니다.
- 의존 대상은 반드시 존재하는 Spec ID여야 합니다.
- 순환 의존이 감지되면 spec-reviewer가 설계 리뷰를 권고합니다.
