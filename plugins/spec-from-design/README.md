# spec-from-design

HLD/LLD 설계 문서 및 개발요청서에서 **코드 생성 가능한 Spec**을 추출하는 멀티 에이전트 플러그인.

## 에이전트 구조

```
spec-orchestrator (조율자)
├── design-analyzer            HLD/LLD/Dev Request 파싱 + Foundation 문서 생성
├── usecase-identifier         진입점 기반 구현 클래스 식별 → UC 목록
├── identification-verifier    UC 식별 완전성 1:1 매핑 검증 (게이트)
├── policy-extractor           HLD KDD + LLD 설계 판단 → 정책 추출
├── usecase-writer             Spec 작성 (1 UC = 1 파일)
├── scope-evaluator            각 Spec 규모 판단
├── usecase-splitter           split-needed Spec 분해 (조건부)
├── test-scenario-writer       Given-When-Then 테스트 시나리오 작성
├── spec-traceability-verifier HLD/LLD ↔ Spec 양방향 전수 대조 (게이트)
└── spec-reviewer              100점 만점 품질 평가 (게이트)
```

## 파이프라인

```
  HLD + LLD (+ Dev Request)
      │
      ▼
 ┌──────────────────────────────────────────────────┐
 │  ① design-analyzer                               │
 │     설계 문서 파싱 → Foundation 문서 생성          │
 │     (service-definition, architecture-rules,      │
 │      naming-guide, infra-config)                  │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ② usecase-identifier                            │
 │     진입점 열거 (REST API, Temporal, Kafka 등)    │
 │     각 구현 클래스 = 1 UC로 식별                  │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ③ identification-verifier (게이트 1)             │
 │     LLD 구현 클래스와 UC 목록 1:1 매핑 검증       │
 │     FAIL → ② 재실행 (최대 2회)                    │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ④ policy-extractor                              │
 │     HLD KDD + LLD 설계 판단 → 정책 파일 생성      │
 │     → docs/policies/POLICY-{DOMAIN}-{NNN}.md     │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑤ usecase-writer                                │
 │     검증된 UC 목록 + 정책 → Spec 작성             │
 │     1 UC = 1 파일 (docs/specs/)                   │
 │     검증 조건에 책임 위치 + 에러 코드 명시         │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑥ scope-evaluator                               │
 │     수정 대상 파일 수 + FR 수로 규모 판단          │
 │     → ok / split-needed                           │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑦ usecase-splitter (조건부)                      │
 │     split-needed Spec만 분해                      │
 │     → model Spec + service Spec 산출              │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑧ test-scenario-writer                          │
 │     각 Spec에 Given-When-Then 테스트 시나리오 추가 │
 │     TC-ID 부여, 테스트 레벨 분류                   │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑨ spec-traceability-verifier (게이트 2)          │
 │     HLD KDD → Policy 매핑 완전성                  │
 │     LLD FR → Spec 기본 흐름 매핑 완전성            │
 │     FAIL → ⑤ 재실행 (최대 2회)                    │
 └────────────────────┬─────────────────────────────┘
                      │
                      ▼
 ┌──────────────────────────────────────────────────┐
 │  ⑩ spec-reviewer (게이트 3)                       │
 │     8개 카테고리 100점 만점 품질 평가              │
 │     90점 미만 FAIL → ⑤ 재실행 (최대 2회)          │
 │     PASS 시 개선 제안도 함께 출력                  │
 └─────────────────────────────────────────────────┘
```

## Spec 유형

| 유형 | 설명 | 테스트 시나리오 |
|------|------|----------------|
| `usecase` | 외부 요청을 수신하여 처리하는 기능 단위 | 필수 |
| `model` | 엔티티/스키마 변경 (분해 산출물) | 선택 |
| `service` | 도메인 서비스 (분해 산출물) | 선택 |
| `refactoring` | 외부 동작 불변 리팩터링 | 필수 |
| `performance` | 성능 최적화 | 필수 |
| `simplification` | 구조 단순화 (외부 동작 변경 수반 가능) | 필수 |

## 입력

| 입력 | 필수 | 설명 |
|------|------|------|
| HLD | 선택 | 고수준 설계 (KDD, NFR, 상태 모델) |
| LLD | 필수 | 저수준 설계 (FR, 클래스 설계, API 설계) |
| Dev Request | 선택 | 개발요청서 (요구사항, 배경, 제약조건) |

## 출력

```
docs/
├── service-definition.md      # 서비스 정의
├── architecture-rules.md      # 아키텍처 규칙
├── naming-guide.md            # 네이밍 가이드
├── infra-config.md            # 인프라 설정
├── policies/                  # 비즈니스 정책
│   └── POLICY-{DOMAIN}-{NNN}.md
└── specs/                     # Spec 파일 (1 UC = 1 파일)
    └── SPEC-{PREFIX}-{DOMAIN}-{NNN}-{name}.md
```

## 사용 예시

```
# HLD + LLD로 Spec 생성
"이 HLD와 LLD에서 Spec을 생성해줘"

# LLD만으로 Spec 생성
"LLD에서 Spec을 추출해줘"

# 개발요청서로 Spec 생성
"이 개발요청서에서 Spec을 생성해줘"

# 신규 프로젝트 모드
"신규 프로젝트로 Spec을 생성해줘 (모드: new-project)"
```

## 품질 게이트

3단계 게이트를 통과해야 Spec이 최종 산출됩니다:

| 게이트 | 에이전트 | 기준 | 실패 시 |
|--------|---------|------|---------|
| 게이트 1 | identification-verifier | UC ↔ LLD 클래스 1:1 | identifier 재실행 |
| 게이트 2 | spec-traceability-verifier | FR/KDD 전수 대조 | writer 재실행 |
| 게이트 3 | spec-reviewer | 100점 중 90점 이상 | writer 재실행 |
