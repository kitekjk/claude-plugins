# Use Case Spec 정의

동작이 바뀌는 모든 변경에 사용합니다. Actor가 있는 기능 추가/변경, 외부 연동 추가 등.
소규모 변경이면 이 유형 하나로 충분합니다.
**하나의 Spec은 하나의 파일**로 출력하며, **구현 코드를 포함하지 않습니다**.

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
