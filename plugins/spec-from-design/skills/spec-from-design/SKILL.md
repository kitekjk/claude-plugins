---
name: spec-from-design
description: HLD/LLD 설계 문서에서 코드 생성 가능한 Spec을 생성합니다. 기존 프로젝트와 신규 프로젝트 모두 지원합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash
---

# spec-from-design

HLD/LLD 설계 문서 및 개발요청서(Dev Request)에서 코드 생성 가능한 Spec을 추출합니다.

## 호출 흐름

이 스킬은 `spec-orchestrator` 에이전트를 Task로 호출하여 전체 파이프라인을 실행합니다.

```
사용자 요청 → SKILL.md → spec-orchestrator (Task 호출)
                              ↓
              ① design-analyzer      → 설계 파싱 + Foundation 문서
              ② usecase-identifier   → UC 식별 목록
              ③ identification-verifier → 검증 게이트 (fail → ② 재실행)
              ④ policy-extractor     → 정책 추출
              ⑤ usecase-writer       → Spec 작성 (1 UC = 1 파일)
              ⑥ scope-evaluator      → 규모 판단
              ⑦ usecase-splitter     → 조건부 분해
              ⑧ test-scenario-writer → 테스트 시나리오
              ⑨ spec-reviewer        → 품질 검증 (fail → ⑤ 재실행)
```

## 입력 안내

| 입력 | 필수 | 설명 |
|------|------|------|
| HLD | 선택 | 고수준 설계 (KDD, NFR, 상태 모델) |
| LLD | 필수 | 저수준 설계 (FR, 클래스 설계, API 설계) |
| Dev Request | 선택 | 개발요청서 (요구사항, 배경, 제약조건) |

### 입력 규모별 모드

| 규모 | 입력 조합 | design-analyzer 동작 |
|------|----------|---------------------|
| full | HLD + LLD (+ Dev Request) | HLD + LLD 파싱, Foundation 문서 생성 |
| lld-only | LLD만 (+ Dev Request) | LLD만 파싱, Foundation 문서 기존 것 재사용 또는 코드에서 추출 |
| request-only | Dev Request만 | Dev Request에서 요구사항 추출, 아키텍처는 코드에서 추출 |

## 모드 선택 로직

프로젝트 모드는 다음 기준으로 결정됩니다:

1. **사용자 명시 지정** → 해당 모드 사용
2. **자동 판별** (미지정 시):
   - 프로젝트 루트에 소스 코드 존재 → `existing-project`
   - 소스 코드 없음 → `new-project` + preset 선택 요청

### existing-project 모드
- 기존 코드에서 아키텍처 추출 (build files, package structure, naming conventions)

### new-project 모드
- preset 사용 (기본: `ddd-clean-kotlin`)
- 사용자가 다른 preset을 지정할 수 있음

## 실행 방법

spec-orchestrator를 Task로 호출합니다:

```
Task: spec-orchestrator

입력 파일:
- HLD: {HLD 파일 경로}
- LLD: {LLD 파일 경로}
- Dev Request: {Dev Request 파일 경로} (선택)

모드: {existing-project | new-project} (선택, 미지정 시 자동 판별)
```

## 사용 예시

### 예시 1: HLD + LLD로 Spec 생성
```
HLD와 LLD에서 Spec을 생성해 주세요.
- HLD: docs/design/hld.md
- LLD: docs/design/lld.md
```

### 예시 2: LLD만으로 Spec 생성
```
LLD에서 Spec을 추출해 주세요.
- LLD: docs/design/order-processing-lld.md
```

### 예시 3: 개발요청서로 Spec 생성
```
설계 문서에서 Spec을 생성해 주세요.
- Dev Request: docs/requests/order-api-request.md
```

### 예시 4: 신규 프로젝트 모드
```
신규 프로젝트로 Spec을 생성해 주세요.
- LLD: docs/design/new-service-lld.md
- 모드: new-project
```

## 트리거 키워드

다음 키워드로 이 스킬이 자동 매칭됩니다:
- "Spec 생성"
- "HLD에서 Spec"
- "LLD에서 Spec"
- "설계 문서에서 Spec"
- "Spec 추출"
- "spec-from-design"
