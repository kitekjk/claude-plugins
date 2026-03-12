# Policy Spec 정의

Policy Spec은 HLD KDD + LLD 설계 판단 근거에서 도출됩니다.

## 필수 섹션

| 섹션 | 소스 | 설명 |
|------|------|------|
| 기본 정보 | 자동 생성 | type, domain, id |
| 규칙 섹션 | HLD KDD / LLD 설계 판단 | 규칙 + 근거 + 제약 + 적용 범위 |
| 에러 코드 | LLD 에러 응답 | 에러 코드 테이블 |
| 적용 도메인 | 자동 링크 | 관련 도메인 목록 |

## 규칙 형식

각 규칙에 다음을 포함:
- 규칙: 정책 규칙 문장
- 근거: HLD KDD 또는 LLD 설계 판단 근거 요약
- 제약: "감수하는 단점"을 알려진 제약으로 명시
- 적용 범위: 관련 Use Case ID

## source 필드

반드시 HLD KDD 번호 또는 LLD 설계 판단 섹션을 명시합니다.
예: `source: po-cancel-flow HLD KDD-5`
