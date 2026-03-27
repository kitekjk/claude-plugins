---
name: code-from-spec
description: Spec 기반 코드 구현, 코드 리뷰(체크리스트 기반 리뷰→수정 루프), Spec 준수도 검증, PR 리뷰 피드백 반영(코드 수정 + Spec 동기화)을 수행합니다. Spec으로 코드를 생성하거나, 코드 리뷰를 돌리거나, 구현이 Spec을 잘 따르는지 검증하거나, PR 리뷰를 코드와 Spec에 반영하려면 사용하세요.
---

# code-from-spec

## 목적

`code-from-spec`은 Spec 문서를 기반으로 코드를 구현하고, 구현된 코드가 **Spec을 얼마나 충실히 따르는지 준수도 점수**를 산출하는 스킬입니다.

## 단일 기준

모든 규칙의 기준은 `contract.json`입니다.

## 서브에이전트 구조

```text
impl-orchestrator
├── work-scheduler     # Spec 의존성 분석 + Jira 티켓 + Git 브랜치 + 실행 계획
├── code-generator     # Spec → 코드 구현 (Agent Teams) + 모호점 로그
├── spec-verifier      # 구현 → Spec 준수도 검증 + Spec 갭 플래그
└── spec-feedback      # 모호점 + 갭 → Spec 수정 제안
```

## 워크플로우

### 전체 흐름 (스케줄링 + 구현 + 검증 + 피드백)

```
Spec
 │
 ▼
work-scheduler (의존성 분석 + Jira 티켓 + 브랜치 생성)
 │
 ▼
code-generator (Agent Teams 4명 + 모호점 로그) ← isolation: "worktree"로 병렬/순차
 │
 ▼
빌드 + 테스트 통과
 │
 ▼
코드 리뷰 루프 (체크리스트 기반 리뷰 → 수정, 최대 3회)
 │
 ▼
spec-verifier (4영역 준수도 검증 + Spec 갭 플래그)
 │
 ▼
spec-feedback (모호점 + 갭 → Spec 수정 제안)
 │
 ▼
사용자 승인 → Spec 반영 + 구현 추적 업데이트
 │
 ▼
integrate (통합 브랜치 생성 → Level 순서 머지 → 전체 테스트 → push 확인)
```

### 개별 워크플로우

| 커맨드 | 설명 |
|--------|------|
| 스케줄, schedule | Spec 의존성 분석 + Jira 티켓 + 브랜치 생성 |
| 구현, implement | Spec 기반 프로젝트 구현 (모호점 로그 포함) |
| 검증, verify | 기존 구현의 Spec 준수도 검증 |
| 코드 리뷰, code-review, 리뷰해줘 | 체크리스트 기반 코드 리뷰 → 수정 루프 (코드가 이미 있는 경우) |
| 피드백, feedback | 모호점 + 미준수 + PR 리뷰에서 Spec 수정 제안 |
| 리뷰 반영, review-apply, PR 피드백 반영 | PR 리뷰 → 코드 수정 → 재검증 → Spec 동기화 |
| 통합, integrate, integration, 통합 테스트 | Spec 브랜치 통합 → 전체 테스트 → push 확인 |

## 4영역 검증 체계

| 영역 | 배점 | 검증 대상 | 미준수 시 의미 |
|------|------|-----------|---------------|
| V1: 기능 구현 완결성 | 40점 | 기본 흐름 + 수정 대상 파일 구현 여부 | 기능 누락 |
| V2: 비즈니스 규칙 준수 | 30점 | policies/ 규칙 반영 여부 | 비즈니스 로직 불일치 |
| V3: 아키텍처 준수 | 15점 | 레이어/의존성 규칙 | 아키텍처 위반 |
| V4: 테스트 커버리지 | 15점 | TC-ID 커버리지 + 통과 | 검증 부족 |

## 등급 체계

| 점수 | 등급 | 의미 |
|------|------|------|
| 95~100 | A | Spec 충실 구현 |
| 85~94 | B | 양호. 소규모 보완 필요 |
| 70~84 | C | 보통. 주요 미준수 항목 존재 |
| 70 미만 | D | 부족. 상당 부분 미구현 |

## 실행 모드

| 모드 | 설명 | 사용 시점 |
|------|------|---------|
| `auto` | Level 0~N 연속 구현, 개발자 리뷰 없이 AI가 전부 처리 | 검증 완료된 Spec, 신뢰도 높은 환경 |
| `review-gate` | Level 완료마다 개발자 리뷰 후 다음 Level 진행. 1-Level lookahead(shared_files 겹침 없을 때)로 대기 시간 최소화 | Spec 검증 초기, 중요 도메인 |

모드를 명시하지 않으면 `contract.json`의 `execution.default` (기본값: `auto`)를 따릅니다.

## 사용 예시

```
"이 Spec들의 작업 계획을 세워줘"                   # 스케줄
"이 Spec으로 프로젝트를 구현해줘"                  # 구현 (auto)
"리뷰 포함해서 구현해줘"                           # 구현 (review-gate)
"review-gate 모드로 구현해줘"                      # 구현 (review-gate 명시)
"구현이 Spec을 잘 따르는지 검증해줘"               # 검증
"모호한 부분을 피드백해서 Spec을 보강해줘"          # 피드백
"PR 리뷰 반영해서 Spec 업데이트해줘"                # 피드백 (Spec만 수정)
"이 PR 리뷰 내용을 Spec에 반영해줘 {PR_URL}"       # 피드백 (PR URL → Spec만 수정)
"이 PR 리뷰 반영해줘 {PR_URL}"                     # review-apply (코드 수정 + Spec 동기화)
"리뷰 적용하고 Spec도 맞춰줘"                       # review-apply
"이 코드 리뷰해줘"                                   # code-review (기존 코드 리뷰)
"코드 리뷰 돌려줘"                                   # code-review
"구현한 것들 통합해줘"                                # integrate
"develop 브랜치로 통합 테스트 해줘"                   # integrate (base branch 지정)
"Spec 기반으로 구현하고 준수도도 확인해줘"          # 전체 (auto)
"리뷰 포함해서 전체 파이프라인 실행해줘"            # 전체 (review-gate)
```

## 고정 정책

- Spec에 없는 것은 구현하지 않음
- 구현 중 모호점 발견 시 ambiguity-log에 기록
- 빌드 실패 시 최대 3회 재시도
- Spec 수정은 사용자 승인 후 반영
- 리포트는 `reports/` 디렉토리에 저장
- Spec은 SSOT — 구현 상태(Jira, PR, commit)를 Spec 파일에 기록
- 기존 Jira 티켓이 있는 Spec은 중복 생성하지 않음
