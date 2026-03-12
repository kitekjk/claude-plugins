# HLD 문서 스펙

`HLD`는 시스템의 전체 구조, 주요 컴포넌트 관계, 핵심 설계 결정, 비기능 목표를 설명하는 문서입니다.

## 계약 기준

- 구조와 저장 규칙의 단일 기준은 `skills/doc-writing-team/contract.json`
- 저장 경로는 `documents/hld/{slug}/DOCUMENT.md`
- `Appendix`는 선택 허용
- Appendix는 본문을 보조하는 참고 자료이며, 필수 섹션을 대체하지 않음

## 필수 섹션

### 1. Glossary

- 핵심 용어 5-20개

### 2. Overview

- 시스템 목적
- 범위
- 대상 독자

### 3. System Context

- 외부 시스템 관계
- 인터페이스 방향/프로토콜
- Mermaid 다이어그램 필수

### 4. High-Level Architecture

- 컴포넌트 다이어그램
- 컴포넌트 역할 + 기술 스택 명시
- 데이터 흐름

### 5. State Transition Model (해당 시)

- 상태 그룹별 enum 정의
- 허용 전이 조건
- 전이 규칙
- Mermaid stateDiagram 포함
- **상태가 중요한 도메인에서만 작성** (해당하지 않으면 생략)

### 6. Key Design Decisions

- 핵심 결정 3개 이상
- 각 결정의 근거와 관련 ADR
- 대안 비교 필수

### 7. Non-Functional Requirements

- 수치 목표 3개 이상
- 측정 방법 또는 관측 수단
- 가용성/복구 목표

## 선택 섹션

### 8. Deployment Overview

- 배포 환경 요약
- 필요한 경우 배포 다이어그램

### 9. Appendix

- 참고 표
- 상세 매핑
- 본문 판단을 보조하는 추가 자료

## 작성 규칙

- `System Context`와 `High-Level Architecture`에 최소 2개의 Mermaid 다이어그램을 포함합니다.
- 상태가 중요한 도메인이면 `State Transition Model`을 포함하고, Mermaid stateDiagram을 추가합니다.
- 구현 세부(클래스/함수/DB 세부 스키마)는 LLD로 넘깁니다.
- Appendix가 있어도 핵심 구조와 NFR은 본문에 남깁니다.
- ADR 링크가 있으면 연결합니다.
- 컴포넌트 테이블에는 역할과 기술 스택을 함께 명시합니다.

## Spec 도출 가능성 기준

이 HLD에서 하류 Spec을 생성할 때 다음이 가능해야 합니다.

| 도출 대상 | HLD 소스 섹션 | 필요 정보 |
|-----------|-------------|----------|
| 서비스 정의 | Glossary + Overview | 도메인 용어, 시스템 목적 |
| 아키텍처 규칙 | Architecture + 컴포넌트 역할 | 레이어 구조, 컴포넌트 책임 |
| 정책 Spec | KDD | 결정 + 근거 + 대안 비교 |
| NFR 정책 | NFR | 수치 목표 + 측정 방법 |
| 상태 전이 정책 | State Transition Model | 상태 enum, 전이 규칙 |
| infra-config | System Context + Deployment | 외부 시스템 연동 방식 |

## 권장 길이

| 섹션 | 권장 길이 |
|------|----------|
| Glossary | 5-20개 용어 |
| Overview | 100-300자 |
| System Context | 다이어그램 + 200자 이상 |
| High-Level Architecture | 다이어그램 + 300-500자 |
| State Transition Model | 상태 그룹 + 전이 규칙 |
| Key Design Decisions | 3-7개 결정 |
| Non-Functional Requirements | 수치 목표 3개 이상 |
| 전체 | 1000-2000자 |
