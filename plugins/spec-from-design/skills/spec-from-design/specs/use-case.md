# Use Case Spec 정의

Use Case Spec은 LLD의 Functional Requirements + 클래스 설계에서 도출됩니다.

## 필수 섹션

| 섹션 | 소스 | 설명 |
|------|------|------|
| 기본 정보 | 자동 생성 | type, domain, id, source |
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
