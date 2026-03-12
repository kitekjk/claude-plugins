# LLD 문서 스펙

`LLD`는 HLD에서 정의된 구조를 구현 수준으로 상세화하고, 데이터/인터페이스/알고리즘/운영 전략을 설명하는 문서입니다.

## 계약 기준

- 구조와 저장 규칙의 단일 기준은 `skills/doc-writing-team/contract.json`
- 저장 경로는 `documents/lld/{slug}/DOCUMENT.md`
- `Appendix`는 선택 허용
- Appendix는 보조 계산, 확장 표, 운영 부록 용도로만 사용

## 필수 섹션

### 1. Glossary

- 핵심 용어 5-15개

### 2. Problem Statement

- 시스템 목표
- 데이터 특성 (Volatility, Cardinality, R/W Ratio, Volume 중 2개+)
- 기술적 난제
- 미해결 리스크 (리스크 + 영향도 + 완화 방안)
- 문제 미해결 시 리스크

### 3. Functional Requirements

- 검증 가능한 요구사항
- 우선순위 포함
- 각 FR에 검증 기준 필수

### 4. Non-Functional Requirements

- 최소 5개 이상의 수치 목표
- 성능, 처리량, 가용성, RTO/RPO, 데이터 볼륨 또는 확장성 포함

### 5. Goal / Non-Goal

- 이 문서가 해결하는 것
- 이 문서가 다루지 않는 것

### 6. Proposed Design

아키텍처 개요와 함께 다음 하위 섹션을 포함합니다.

#### 6.1 API 설계

- 엔드포인트 목록 (Method, Path, 설명, 인증)
- 각 엔드포인트별 Request/Response 스키마
- 에러 응답 테이블 (HTTP 상태, 에러 코드, 조건, 메시지)
- 요청 필드별 타입, 필수 여부, 검증 규칙

#### 6.2 클래스/컴포넌트 설계

- 주요 클래스/컴포넌트 목록과 역할
- 핵심 메서드 시그니처
- 컴포넌트 간 관계 (필요 시 클래스 다이어그램)

#### 6.3 DB 스키마

- 테이블 정의 (컬럼, 타입, 제약, 설명)
- 인덱스 정의 (인덱스명, 컬럼, 용도)
- DDL 예시

#### 6.4 설계 판단 근거

- 주요 결정별 채택/탈락 옵션 비교
- 채택 근거
- 감수하는 단점 명시
- 트레이드오프 분석

## 선택 섹션

### 7. Appendix

- 보조 계산
- 상세 표
- 운영 파라미터
- 본문 판단을 보조하는 추가 자료

## 작성 규칙

- 데이터 특성은 `Volatility`, `Cardinality`, `Read/Write Ratio`, `Volume` 중 최소 2개 이상을 포함합니다.
- 모호한 표현 대신 수치를 사용합니다.
- Mermaid는 복잡한 흐름이나 상태 전이가 있을 때만 사용합니다.
- HLD와 용어 및 범위가 일치해야 합니다.
- API 설계의 에러 코드는 프로젝트 전체에서 일관된 체계를 사용합니다.
- FR 검증 기준은 테스트 시나리오로 직접 변환 가능한 수준으로 작성합니다.
- 미해결 리스크는 완화 방안과 함께 영향도를 기재합니다.

## Spec 도출 가능성 기준

이 LLD에서 하류 Spec을 생성할 때 다음이 가능해야 합니다.

| 도출 대상 | LLD 소스 섹션 | 필요 정보 |
|-----------|-------------|----------|
| Use Case Spec | FR + 클래스 설계 | FR-ID, 검증 기준, 메서드 호출 순서 |
| API Spec | API 설계 | 엔드포인트, 요청/응답, 에러 코드 |
| 정책 Spec | 설계 판단 근거 | 채택 근거, 감수하는 단점 |
| 테스트 시나리오 | FR 검증 기준 + 미해결 리스크 | Given-When-Then 변환 가능한 검증 조건 |

## 권장 길이

| 섹션 | 권장 길이 |
|------|----------|
| Glossary | 5-15개 용어 |
| Problem Statement | 200-500자 |
| Functional Requirements | 5-20개 항목 |
| Non-Functional Requirements | 수치 목표 5개 이상 |
| Goal / Non-Goal | 각 3-7개 |
| Proposed Design | 제한 없음 |
| - API 설계 | 엔드포인트당 Request/Response + 에러 테이블 |
| - 클래스 설계 | 주요 클래스 3-10개 |
| - DB 스키마 | 관련 테이블 전체 |
| - 설계 판단 근거 | 결정 3-7개 |
