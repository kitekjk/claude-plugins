---
name: spec-harness
description: Spec 기반 코드 생성과 결정성 검증을 수행합니다. Spec으로 코드를 생성하거나, Spec 품질을 검증하려면 사용하세요.
allowed-tools: Read, Write, Edit, Grep, Glob, Task, Bash
---

# spec-harness

## 목적

`spec-harness`는 Spec 문서를 기반으로 코드를 생성하고, 동일 Spec으로 독립 생성된 2개의 구현체를 비교하여 **Spec의 결정성 점수**를 산출하는 스킬입니다.

차이나는 부분 = Spec이 모호해서 AI가 임의 판단한 부분 → Spec 보강 대상.

## 단일 기준

모든 규칙의 기준은 `contract.json`입니다.

## 서브에이전트 구조

```text
harness-orchestrator
├── code-generator          # Spec → 코드 생성 (Agent Teams)
├── determinism-evaluator   # 5 Level 결정성 비교
└── spec-improver           # 비교 결과 → Spec 보강
```

## 워크플로우

### 전자동 결정성 검증 (/verify-determinism)

```
Spec
 ├─→ code-generator (regen1) ── 독립 세션
 ├─→ code-generator (regen2) ── 독립 세션
 │
 ▼
서버 기동 (regen1:8080, regen2:8081)
 │
 ▼
determinism-evaluator (5 Level 비교)
 │
 ▼
점수 산출 + 리포트
 │
 ▼
spec-improver (보강 항목 추출 → Spec 반영)
 │
 ▼
서버 종료
```

### 개별 워크플로우

| 커맨드 | 설명 |
|--------|------|
| `/regen [target_dir]` | Spec 기반 프로젝트 재생성 |
| `/compare` | 기존 regen1/regen2 비교 + 점수 |
| `/improve-spec` | 비교 리포트에서 Spec 보강 반영 |

## 5 Level 비교 체계

| Level | 배점 | 측정 대상 | Spec 모호 시 영향 |
|-------|------|-----------|-------------------|
| L1: 테스트 상호 실행 | 30점 | 동작의 호환성 | 네이밍/규칙 모호 |
| L2: API 계약 | 25점 | 인터페이스 일치 | API Spec 미명시 |
| L3: 비즈니스 시나리오 | 25점 | 비즈니스 판정 | 정책 규칙 모호 |
| L4: 코드 구조 | 10점 | 아키텍처 패턴 | 아키텍처 규칙 부족 |
| L5: 네이밍 | 10점 | 명명 규칙 | 네이밍 가이드 부족 |

## 등급 체계

| 점수 | 등급 | 의미 |
|------|------|------|
| 95~100 | A | Spec 결정성 우수 |
| 85~94 | B | 양호. 소규모 보강 후 사용 가능 |
| 70~84 | C | 보통. Spec 보강 필요 |
| 70 미만 | D | 부족. 대폭 보강 필요 |

## 사용 예시

```
"이 프로젝트의 Spec 결정성을 검증해줘"     # 전자동
"regen1을 생성해줘"                        # 재생성만
"regen1과 regen2를 비교해줘"               # 비교만
"비교 리포트를 보고 Spec을 보강해줘"        # 보강만
```

## 고정 정책

- regen1과 regen2는 반드시 독립적으로 생성 (별도 세션, 코드 미참조)
- 빌드 실패 시 최대 3회 재시도
- 비교 시 동적 값(id, createdAt, updatedAt, token)은 제외
- Spec 보강은 사용자 승인 후 반영
- 리포트는 `reports/determinism-{date}.md`에 저장
