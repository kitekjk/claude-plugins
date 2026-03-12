# API Spec 정의

API Spec은 LLD의 API 설계 섹션에서 1:1 매핑으로 도출됩니다.

## 필수 섹션

| 섹션 | 소스 | 설명 |
|------|------|------|
| 기본 정보 | 자동 생성 | type, domain, id, source |
| 관련 정책 | policy-extractor 결과 | 관련 정책 Spec ID |
| 관련 Spec | 자동 링크 | 관련 Use Case ID |
| API 개요 | LLD API 설계 | 엔드포인트 목록 |
| 공통 사항 | LLD/HLD 인증, 기존 코드 | 인증, 공통 에러 |
| 엔드포인트 | LLD API 설계 | Method + Path + 요청/응답/에러 |

## 엔드포인트 세부 구조

각 엔드포인트에 다음을 포함:
- Method + Path
- 역할 제한
- 출처 (LLD Section 번호)
- Request 필드 테이블 (필드, 타입, 필수, 검증, 설명)
- Response 스키마
- 에러 응답 테이블 (HTTP 상태, 에러 코드, 조건, 메시지)

## dependsOn 필드

API Spec은 연결된 Use Case Spec의 의존성을 상속합니다. 추가로 API 간 직접 의존이 있으면 명시합니다.

### 판별 기준

- 엔드포인트가 다른 도메인의 API를 내부 호출하면 `api` 타입 의존성
- 요청/응답에 다른 도메인의 모델을 포함하면 `data` 타입 의존성

## existing-project 규칙

- 기존 에러 코드 체계 준수
- 기존 API 경로 패턴 준수
- 하위호환 위반 시 명시
