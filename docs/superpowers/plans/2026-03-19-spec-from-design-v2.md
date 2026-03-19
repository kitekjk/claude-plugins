# spec-from-design v2.0.0 Plugin Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 spec-from-design v1.7.0 플러그인을 삭제하고, 10개 에이전트 파이프라인 기반의 v2.0.0을 처음부터 생성한다.

**Architecture:** HLD/LLD/Dev Request 입력 → design-analyzer → usecase-identifier → identification-verifier(게이트) → policy-extractor → usecase-writer → scope-evaluator → usecase-splitter(조건부) → test-scenario-writer → spec-reviewer(게이트) 순서의 멀티 에이전트 파이프라인. contract.json이 단일 기준이며 모든 에이전트와 체크리스트가 이를 참조한다.

**Tech Stack:** Claude Code Plugin (Markdown agents, JSON manifest, Markdown skills/specs/templates/checklists/mappings)

**Spec:** `docs/superpowers/specs/2026-03-19-spec-from-design-v2-design.md`
**Rebuild Prompt:** `spec-from-design-rebuild-prompt.md`

---

## File Structure

### 삭제 대상
- `plugins/spec-from-design/` (전체 v1.7.0 디렉토리)

### 생성 대상

```
plugins/spec-from-design/
├── .claude-plugin/
│   └── plugin.json                          # 매니페스트 (v2.0.0)
├── agents/                                  # 10개 에이전트
│   ├── spec-orchestrator.md                 # 파이프라인 조율
│   ├── design-analyzer.md                   # HLD/LLD/DevReq 파싱 + Foundation
│   ├── usecase-identifier.md                # UC 식별 전담
│   ├── identification-verifier.md           # 식별 검증 게이트
│   ├── policy-extractor.md                  # 정책 추출
│   ├── usecase-writer.md                    # Spec 작성 (1UC=1파일)
│   ├── scope-evaluator.md                   # 규모 판단
│   ├── usecase-splitter.md                  # 조건부 분해
│   ├── test-scenario-writer.md              # 테스트 시나리오
│   └── spec-reviewer.md                     # 품질 검증
└── skills/spec-from-design/
    ├── SKILL.md                             # 스킬 진입점
    ├── CLAUDE.md                            # 내부 규칙
    ├── contract.json                        # 단일 기준 (v2.0.0)
    ├── checklists/
    │   ├── input-quality.md                 # HLD/LLD 입력 검증
    │   ├── output-quality.md                # 100점 만점 품질 평가
    │   ├── traceability.md                  # 추적성 검증
    │   ├── identification-completeness.md   # 구현 클래스 전수 식별
    │   └── one-to-one-mapping.md            # 1클래스:1Spec 매핑
    ├── specs/
    │   ├── usecase.md                       # usecase 유형 정의
    │   ├── model.md                         # model 유형 정의
    │   ├── service.md                       # service 유형 정의
    │   ├── refactoring.md                   # refactoring 유형 정의
    │   ├── performance.md                   # performance 유형 정의
    │   └── policy.md                        # policy 유형 정의
    ├── templates/
    │   ├── usecase.md                       # usecase 출력 템플릿
    │   ├── model.md                         # model 출력 템플릿
    │   ├── service.md                       # service 출력 템플릿
    │   ├── refactoring.md                   # refactoring 출력 템플릿
    │   ├── performance.md                   # performance 출력 템플릿
    │   ├── policy.md                        # policy 출력 템플릿
    │   ├── service-definition.md            # Foundation 문서 템플릿
    │   ├── architecture-rules.md            # Foundation 문서 템플릿
    │   └── naming-guide.md                  # Foundation 문서 템플릿
    ├── mappings/
    │   ├── hld-to-spec.md                   # HLD → Spec 매핑 규칙
    │   └── lld-to-spec.md                   # LLD → Spec 매핑 규칙
    └── presets/
        └── ddd-clean-kotlin.md              # DDD + Clean Architecture preset
```

### 수정 대상
- `.claude-plugin/marketplace.json` — spec-from-design 버전 → 2.0.0
- `README.md` — 플러그인 목록 테이블 버전 → 2.0.0

---

## Task 1: 기존 v1.7.0 삭제 및 디렉토리 구조 생성

**Files:**
- Delete: `plugins/spec-from-design/` (전체)
- Create: 새 디렉토리 구조 (빈 디렉토리들)

- [ ] **Step 1: 기존 플러그인 삭제**

```bash
rm -rf plugins/spec-from-design/
```

- [ ] **Step 2: 새 디렉토리 구조 생성**

```bash
mkdir -p plugins/spec-from-design/.claude-plugin
mkdir -p plugins/spec-from-design/agents
mkdir -p plugins/spec-from-design/skills/spec-from-design/checklists
mkdir -p plugins/spec-from-design/skills/spec-from-design/specs
mkdir -p plugins/spec-from-design/skills/spec-from-design/templates
mkdir -p plugins/spec-from-design/skills/spec-from-design/mappings
mkdir -p plugins/spec-from-design/skills/spec-from-design/presets
```

- [ ] **Step 3: 커밋**

```bash
git add -A plugins/spec-from-design/
git commit -m "refactor(spec-from-design): delete v1.7.0 and create v2.0.0 directory structure"
```

---

## Task 2: contract.json + plugin.json + SKILL.md + CLAUDE.md (기반 파일)

**Files:**
- Create: `plugins/spec-from-design/skills/spec-from-design/contract.json`
- Create: `plugins/spec-from-design/.claude-plugin/plugin.json`
- Create: `plugins/spec-from-design/skills/spec-from-design/SKILL.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/CLAUDE.md`

- [ ] **Step 1: contract.json 작성**

설계 문서 Section 5의 contract.json 구조를 그대로 사용한다. 핵심 필드:
- `version`: "2.0.0"
- `modes`: existing-project / new-project
- `pipeline`: 9개 에이전트 순서
- `identificationRules`: 진입점 원칙 + 기본 5개 + customEntryPoints
- `decompositionThreshold`: files=10, FR=5
- `retryLimits`: verifier=2, reviewer=2
- `outputRules`: singleFilePerSpec, noImplementationCode, pseudocodeAllowed, specPrefix
- `storagePaths`: specs, policies, foundation, pathFlexibility
- `hardGuardrails`: 4개 규칙
- `qualityGates`: passThreshold=90, categories=8, maxScore=100

참조: 설계 문서 Section 5

- [ ] **Step 2: plugin.json 작성**

설계 문서 Section 11의 구조를 사용한다:
- `name`: "spec-from-design"
- `version`: "2.0.0"
- `description`: 한 줄 설명
- `agents`: 10개 에이전트 경로
- `skills`: 1개 스킬 경로

참조: 설계 문서 Section 11

- [ ] **Step 3: SKILL.md 작성**

Frontmatter:
```yaml
---
name: spec-from-design
description: HLD/LLD 설계 문서에서 코드 생성 가능한 Spec을 생성합니다. 기존 프로젝트와 신규 프로젝트 모두 지원합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash
---
```

본문: orchestrator 호출 흐름, 입력 안내 (HLD/LLD/Dev Request), 모드 선택 로직, 사용 예시

참조: 설계 문서 Section 12

- [ ] **Step 4: CLAUDE.md 작성**

내용:
- contract.json 단일 기준 원칙
- No-code 원칙 (pseudocode 허용)
- 에이전트 역할 분리 규칙
- 직접 작성 금지 규칙
- 식별/작성 분리 규칙

참조: 설계 문서 Section 13

- [ ] **Step 5: 커밋**

```bash
git add plugins/spec-from-design/skills/spec-from-design/contract.json \
       plugins/spec-from-design/.claude-plugin/plugin.json \
       plugins/spec-from-design/skills/spec-from-design/SKILL.md \
       plugins/spec-from-design/skills/spec-from-design/CLAUDE.md
git commit -m "feat(spec-from-design): v2.0.0 foundation files (contract, plugin, skill, rules)"
```

---

## Task 3: Spec 유형 정의 (specs/*.md)

**Files:**
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/usecase.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/model.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/service.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/refactoring.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/performance.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/specs/policy.md`

- [ ] **Step 1: usecase.md 작성**

각 유형 정의 파일은 동일한 구조를 따른다:
```
# {type} 유형 정의
## 목적
## 생성 조건
## 필수 섹션
## 선택 섹션
## 제약 사항
```

usecase: 기본 유형, 진입점 클래스 식별 시 자동 할당.
필수 섹션: 기본 정보, 개요, 수정 대상 파일, 의존성, 기본 흐름, 검증 조건, 테스트 시나리오.
선택 섹션: 대안 흐름, 관련 정책.

참조: 설계 문서 Section 14

- [ ] **Step 2: model.md 작성**

model: 분해 전용, scope-evaluator가 split-needed 판정 시에만 생성.
필수 섹션: 기본 정보, 개요, 모델 변경사항, 필드 정의, 관계, 마이그레이션.
제약: 단독 생성 금지, 부모 usecase 참조 필수.

- [ ] **Step 3: service.md 작성**

service: 분해 전용, model과 동일 조건.
필수 섹션: 기본 정보, 개요, 서비스 책임, 메서드, 입출력, 에러 처리.
제약: 단독 생성 금지, 부모 usecase 참조 필수.

- [ ] **Step 4: refactoring.md 작성**

refactoring: LLD에서 명시적으로 분류한 항목만.
필수 섹션: 기본 정보, 개요, Before/After 구조, 변경 사유, 영향 범위.

- [ ] **Step 5: performance.md 작성**

performance: LLD에서 명시적으로 분류한 항목만.
필수 섹션: 기본 정보, 개요, 현재 문제, 해결 방안, 목표 지표, 측정 방법.

- [ ] **Step 6: policy.md 작성**

policy: policy-extractor가 생성.
필수 섹션: 기본 정보, 규칙, 제약조건, 적용 도메인.

- [ ] **Step 7: 커밋**

```bash
git add plugins/spec-from-design/skills/spec-from-design/specs/
git commit -m "feat(spec-from-design): add spec type definitions (6 types)"
```

---

## Task 4: 출력 템플릿 (templates/*.md)

**Files:**
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/usecase.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/model.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/service.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/refactoring.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/performance.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/policy.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/service-definition.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/architecture-rules.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/templates/naming-guide.md`

- [ ] **Step 1: usecase.md 템플릿 작성**

설계 문서 Section 7의 Spec 템플릿 구조 사용:
```markdown
# SPEC-{PREFIX}-{DOMAIN}-{number}-{name}

## 기본 정보
- 유형: usecase
- 도메인: {도메인}
- 출처: {LLD 참조}
- 진입점 유형: {진입점 유형}
- 구현 클래스: {클래스명}
- 구현 상태: not-started

## 개요
## 수정 대상 파일
## 의존성 (dependsOn)
## 기본 흐름
## 대안 흐름
## 검증 조건
## 테스트 시나리오
## 관련 정책
```

- [ ] **Step 2: model.md 템플릿 작성**

usecase 템플릿 기반에서 model 고유 섹션 추가:
모델 변경사항, 필드 정의, 관계, 마이그레이션.
부모 usecase 참조 필드 포함.

- [ ] **Step 3: service.md 템플릿 작성**

서비스 책임, 메서드, 입출력, 에러 처리 섹션.
부모 usecase 참조 필드 포함.

- [ ] **Step 4: refactoring.md 템플릿 작성**

Before/After 구조, 변경 사유, 영향 범위 섹션.

- [ ] **Step 5: performance.md 템플릿 작성**

현재 문제, 해결 방안, 목표 지표, 측정 방법 섹션.

- [ ] **Step 6: policy.md 템플릿 작성**

```markdown
# POLICY-{DOMAIN}-{number}

## 기본 정보
## 규칙
## 제약조건
## 적용 도메인
```

- [ ] **Step 7: Foundation 문서 템플릿 3종 작성**

- `service-definition.md`: 서비스 정의 (스코프, 경계, 외부 의존성)
- `architecture-rules.md`: 아키텍처 규칙 (레이어 규칙, 의존성 방향)
- `naming-guide.md`: 네이밍 가이드 (클래스, 패키지, API 경로 규칙)

- [ ] **Step 8: 커밋**

```bash
git add plugins/spec-from-design/skills/spec-from-design/templates/
git commit -m "feat(spec-from-design): add output templates (6 spec + 3 foundation)"
```

---

## Task 5: 체크리스트 (checklists/*.md)

**Files:**
- Create: `plugins/spec-from-design/skills/spec-from-design/checklists/input-quality.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/checklists/output-quality.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/checklists/traceability.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/checklists/identification-completeness.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/checklists/one-to-one-mapping.md`

- [ ] **Step 1: input-quality.md 작성**

HLD 필수 항목 (H-01~H-07) + LLD 필수 항목 (L-01~L-09).
조건부 항목 표시. blockOnMissing 사용자 오버라이드 허용.

참조: 설계 문서 Section 6

- [ ] **Step 2: output-quality.md 작성**

8카테고리, 100점 만점, 90점+ pass:
- Q1 구조 완결성 (10점)
- Q2 모호성 (15점)
- Q3 분기 커버리지 (20점)
- Q4 참조 완결성 (10점)
- Q5 테스트 도출 가능성 (15점)
- Q6 HLD/LLD 추적성 (10점)
- Q7 YAGNI (10점)
- Q8 스코프 적정성 (10점)

auto-FAIL 4개 조건 포함.

참조: 설계 문서 Section 6.1

- [ ] **Step 3: traceability.md 작성**

매핑 추적:
- HLD KDD → Policy
- LLD FR → Use Case 기본 흐름
- FR 검증 기준 → 테스트 시나리오
- 미해결 리스크 → 엣지 케이스 테스트

- [ ] **Step 4: identification-completeness.md 작성**

검증 항목:
- LLD의 모든 진입점 구현 클래스가 UC 목록에 포함되었는지
- 누락된 클래스가 있으면 사유와 함께 리포트
- 제외 대상 (내부 서비스, 도메인 모델)이 적절히 분류되었는지

- [ ] **Step 5: one-to-one-mapping.md 작성**

검증 항목:
- 하나의 구현 클래스가 정확히 하나의 Spec에 매핑되었는지
- 중복 매핑 (하나의 클래스 → 여러 Spec) 탐지
- 병합 매핑 (여러 클래스 → 하나의 Spec) 탐지

- [ ] **Step 6: 커밋**

```bash
git add plugins/spec-from-design/skills/spec-from-design/checklists/
git commit -m "feat(spec-from-design): add quality checklists (5 files)"
```

---

## Task 6: 매핑 규칙 + Preset (mappings/, presets/)

**Files:**
- Create: `plugins/spec-from-design/skills/spec-from-design/mappings/hld-to-spec.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/mappings/lld-to-spec.md`
- Create: `plugins/spec-from-design/skills/spec-from-design/presets/ddd-clean-kotlin.md`

- [ ] **Step 1: hld-to-spec.md 작성**

매핑 테이블:
| HLD 요소 | Spec 매핑 대상 |
|----------|---------------|
| KDD | Policy 규칙 |
| NFR | NFR Policy (POLICY-NFR-001) |
| 상태 전이 모델 | 상태 Policy 규칙 |
| System Context | infra-config.md |

참조: 설계 문서 Section 15.1

- [ ] **Step 2: lld-to-spec.md 작성**

LLD 요소 → Spec 매핑 + 진입점 유형별 매핑 규칙 포함.
핵심: UC 식별이 FR 매핑보다 먼저 수행되어야 함을 명시.

참조: 설계 문서 Section 15.2

- [ ] **Step 3: ddd-clean-kotlin.md 작성**

기술 스택:
- Kotlin 2.x, Spring Boot 3.x, JDK 21, MySQL 8.x, Gradle (Kotlin DSL)
- JUnit 5 + MockK + Testcontainers

레이어 구조 (Clean Architecture):
- domain/ (Entity, Value Object, Domain Service)
- application/ (Use Case interface & impl, Port, DTO)
- infrastructure/ (Repository adapter, External adapter, Config)
- interfaces/ (REST Controller, Event Listener)

네이밍 규칙:
- Use Case: `{Name}UseCase` / `{Name}Service`
- Repository: `{Name}Port` / `{Name}PersistenceAdapter`
- Controller: `{Name}Controller`
- DTO: `{Name}Request` / `{Name}Response`

customEntryPoints 확장 가이드 포함.

- [ ] **Step 4: 커밋**

```bash
git add plugins/spec-from-design/skills/spec-from-design/mappings/ \
       plugins/spec-from-design/skills/spec-from-design/presets/
git commit -m "feat(spec-from-design): add mapping rules and ddd-clean-kotlin preset"
```

---

## Task 7: 에이전트 정의 — spec-orchestrator + design-analyzer

**Files:**
- Create: `plugins/spec-from-design/agents/spec-orchestrator.md`
- Create: `plugins/spec-from-design/agents/design-analyzer.md`

- [ ] **Step 1: spec-orchestrator.md 작성**

```yaml
---
name: spec-orchestrator
description: spec-from-design 전체 파이프라인을 조율합니다. 입력 규모 판별, 모드 감지, 에이전트 순차 호출, 게이트 관리를 담당합니다.
tools: Read, Write, Edit, Glob, Grep, Task, Bash
---
```

본문에 포함할 내용:
- 입력 규모 판별 (full / lld-only / request-only)
- 프로젝트 모드 감지 (existing-project / new-project)
- 파이프라인 순서: ① analyzer → ② identifier → ③ verifier → ④ policy-extractor → ⑤ writer → ⑥ scope-evaluator → ⑦ splitter → ⑧ test-scenario-writer → ⑨ reviewer
- 게이트 관리: verifier fail → identifier 재실행 (최대 2회 재시도), reviewer fail → writer 재실행 (최대 2회 재시도)
- 출력 경로 감지 (pathFlexibility)
- hardGuardrails 강제: writer에 지정 유형 전달, model/service 분해 전용
- contract.json 참조 지시

- [ ] **Step 2: design-analyzer.md 작성**

```yaml
---
name: design-analyzer
description: HLD/LLD/Dev Request를 파싱하고 Foundation 문서(service-definition, architecture-rules, naming-guide)를 생성합니다.
tools: Read, Write, Edit, Glob, Grep
model: opus
---
```

본문에 포함할 내용:
- 입력 파싱: HLD (개요, 용어, KDD, NFR, 상태 모델), LLD (문제 정의, 목표, 클래스 설계), Dev Request (요구사항, 배경, 제약)
- Foundation 문서 3종 생성 (templates/ 참조)
- 모드별 동작: existing-project (코드에서 아키텍처 추출), new-project (preset 사용)
- 읽기 범위: domain/model/**, README.md, 기존 Foundation 문서
- 읽기 제외: infrastructure/**, test code

- [ ] **Step 3: 커밋**

```bash
git add plugins/spec-from-design/agents/spec-orchestrator.md \
       plugins/spec-from-design/agents/design-analyzer.md
git commit -m "feat(spec-from-design): add orchestrator and analyzer agents"
```

---

## Task 8: 에이전트 정의 — usecase-identifier + identification-verifier

**Files:**
- Create: `plugins/spec-from-design/agents/usecase-identifier.md`
- Create: `plugins/spec-from-design/agents/identification-verifier.md`

- [ ] **Step 1: usecase-identifier.md 작성**

```yaml
---
name: usecase-identifier
description: LLD의 구현 클래스를 열거하고 진입점 유형을 판별하여 Use Case 식별 목록을 산출합니다.
tools: Read, Write, Glob, Grep
model: opus
---
```

본문에 포함할 내용:
- 식별 절차:
  1. LLD 클래스/컴포넌트 설계에서 모든 구현 클래스 열거
  2. contract.json의 entryPoints + customEntryPoints와 대조
  3. entryPointPrinciple ("외부 요청을 직접 수신하는 클래스/메서드")에 따라 판별
  4. 해당 → UC 식별 목록에 추가 (클래스명, 진입점 유형, 도메인)
  5. 비해당 → 제외 (내부 서비스, 도메인 모델 등)
- 출력 형식: UC 식별 목록 (테이블 또는 구조화 문서)
- 기본 유형 규칙: 모든 식별된 UC는 usecase 유형
- 주의: LLD 내용(모델 변경, 도메인 로직)에 의한 유형 변경 금지

- [ ] **Step 2: identification-verifier.md 작성**

```yaml
---
name: identification-verifier
description: Use Case 식별 목록의 완전성과 1:1 매핑을 검증합니다. 누락이나 중복 발견 시 fail을 반환합니다.
tools: Read, Grep
model: sonnet
---
```

본문에 포함할 내용:
- 검증 항목:
  1. identification-completeness 체크리스트 적용
  2. one-to-one-mapping 체크리스트 적용
- 판정: pass / fail
- fail 시 피드백 형식: 누락된 클래스 목록, 중복 매핑 목록, 제외 사유 불명확 항목
- 최대 재시도: 2회 (총 3회 시도, contract.json retryLimits 참조)

- [ ] **Step 3: 커밋**

```bash
git add plugins/spec-from-design/agents/usecase-identifier.md \
       plugins/spec-from-design/agents/identification-verifier.md
git commit -m "feat(spec-from-design): add identifier and verifier agents"
```

---

## Task 9: 에이전트 정의 — policy-extractor + usecase-writer

**Files:**
- Create: `plugins/spec-from-design/agents/policy-extractor.md`
- Create: `plugins/spec-from-design/agents/usecase-writer.md`

- [ ] **Step 1: policy-extractor.md 작성**

```yaml
---
name: policy-extractor
description: HLD KDD와 LLD 설계 판단에서 재사용 가능한 정책(Policy)을 추출합니다.
tools: Read, Write, Edit, Glob, Grep
model: opus
---
```

본문에 포함할 내용:
- 추출 대상: HLD KDD, HLD NFR, LLD 설계 판단/트레이드오프/재시도·타임아웃 설정
- 출력: POLICY-{DOMAIN}-{N} 파일, POLICY-NFR-001, infra-config.md, init-data.md
- 핵심 원칙: 정책은 도메인 레벨 재사용 규칙 (UC 특화 아님)
- 기존 정책 확인 후 중복 시 확장 (적용 도메인 추가)
- 읽기 범위: HLD KDD + NFR, LLD 설계 정당화, infrastructure/config/**, infrastructure/security/**
- 읽기 제외: application/**, interfaces/**
- templates/policy.md 참조

- [ ] **Step 2: usecase-writer.md 작성**

```yaml
---
name: usecase-writer
description: 검증된 UC 식별 목록을 기반으로 Spec을 작성합니다. 무조건 1 UC = 1 파일로 작성합니다.
tools: Read, Write, Edit, Glob, Grep
model: opus
---
```

본문에 포함할 내용:
- 입력: 검증된 UC 식별 목록 (verifier 통과), 파싱된 설계 정보, Policy 파일
- 핵심 규칙:
  - orchestrator가 전달한 지정 유형을 반드시 사용 (변경 불가)
  - 1 UC = 1 파일 (규모 무관)
  - 구현 코드 금지, pseudocode는 허용
  - 구현 상태: not-started로 초기화
- 변환 규칙:
  - LLD FR → 기본 흐름 (번호 리스트, 자연어)
  - 설계 판단 → 대안 흐름
  - 클래스/컴포넌트 → 수정 대상 파일 + dependsOn
- 읽기 범위: LLD FR + API 설계 + 클래스 설계 + 시퀀스 다이어그램
- 읽기 제외: domain/model/**, infrastructure/**
- templates/ 참조 (유형별 템플릿 사용)

- [ ] **Step 3: 커밋**

```bash
git add plugins/spec-from-design/agents/policy-extractor.md \
       plugins/spec-from-design/agents/usecase-writer.md
git commit -m "feat(spec-from-design): add policy-extractor and writer agents"
```

---

## Task 10: 에이전트 정의 — scope-evaluator + usecase-splitter

**Files:**
- Create: `plugins/spec-from-design/agents/scope-evaluator.md`
- Create: `plugins/spec-from-design/agents/usecase-splitter.md`

- [ ] **Step 1: scope-evaluator.md 작성**

```yaml
---
name: scope-evaluator
description: 각 Spec의 규모를 판단하여 분해 필요 여부를 판정합니다.
tools: Read, Grep
model: sonnet
---
```

본문에 포함할 내용:
- 판정 기준 (contract.json decompositionThreshold):
  - 수정 대상 파일 ≤ 10 AND FR ≤ 5 → pass
  - 수정 대상 파일 > 10 OR FR > 5 → split-needed
- 출력: 각 Spec별 판정 결과 (pass / split-needed + 분해 근거)

- [ ] **Step 2: usecase-splitter.md 작성**

```yaml
---
name: usecase-splitter
description: 대규모 Use Case Spec을 model/service Spec으로 분해합니다. scope-evaluator가 split-needed로 판정한 Spec에 대해서만 실행됩니다.
tools: Read, Write, Edit, Glob, Grep
model: opus
---
```

본문에 포함할 내용:
- 조건부 실행: split-needed 없으면 스킵
- 분해 방식: usecase Spec → 축소된 usecase + model Spec + service Spec
- model/service Spec은 부모 usecase를 참조해야 함
- 분해 후에도 1 Spec = 1 파일 유지
- templates/model.md, templates/service.md 참조

- [ ] **Step 3: 커밋**

```bash
git add plugins/spec-from-design/agents/scope-evaluator.md \
       plugins/spec-from-design/agents/usecase-splitter.md
git commit -m "feat(spec-from-design): add scope-evaluator and splitter agents"
```

---

## Task 11: 에이전트 정의 — test-scenario-writer + spec-reviewer

**Files:**
- Create: `plugins/spec-from-design/agents/test-scenario-writer.md`
- Create: `plugins/spec-from-design/agents/spec-reviewer.md`

- [ ] **Step 1: test-scenario-writer.md 작성**

```yaml
---
name: test-scenario-writer
description: 각 Spec에 Given-When-Then 형식의 테스트 시나리오를 생성합니다. 엣지 케이스를 포함합니다.
tools: Read, Write, Edit, Glob, Grep
model: sonnet
---
```

본문에 포함할 내용:
- Spec의 "테스트 시나리오" 섹션에 직접 추가 (별도 파일 아님)
- Given-When-Then 형식
- TC-ID: TC-{DOMAIN}-{번호}-{순번}
- 레벨 분류: Unit / Integration / E2E
- 커버리지 목표: FR당 1+, 대안흐름당 1+, 미해결 리스크 → 엣지 케이스
- 자연어만 (JUnit/Mockito 코드 금지)
- LLD FR 검증 기준 → positive/negative/edge-case 시나리오 변환

- [ ] **Step 2: spec-reviewer.md 작성**

```yaml
---
name: spec-reviewer
description: 전체 Spec 세트를 100점 만점으로 평가하고 auto-FAIL 조건을 검증합니다. Spec을 직접 수정하지 않습니다.
tools: Read, Grep, Glob, Bash
model: opus
---
```

본문에 포함할 내용:
- 평가 전용 (수정 금지)
- output-quality.md 체크리스트 적용 (8카테고리 100점, 90점+ pass)
- traceability.md 체크리스트 적용
- auto-FAIL 4개 조건 검증:
  1. 구현 코드 블록 포함 (yaml dependsOn, pseudocode 제외)
  2. 1 Spec ≠ 1 파일
  3. 유형이 orchestrator 지정과 불일치
  4. model/service 단독 생성
- fail 시 피드백: 감점 카테고리별 상세 사유, auto-FAIL 위반 항목
- 최대 재시도: 2회 (총 3회 시도)

- [ ] **Step 3: 커밋**

```bash
git add plugins/spec-from-design/agents/test-scenario-writer.md \
       plugins/spec-from-design/agents/spec-reviewer.md
git commit -m "feat(spec-from-design): add test-scenario-writer and reviewer agents"
```

---

## Task 12: 버전 동기화 + 최종 검증

**Files:**
- Modify: `.claude-plugin/marketplace.json` — spec-from-design 버전 → 2.0.0
- Modify: `README.md` — 플러그인 목록 테이블 버전 → 2.0.0

- [ ] **Step 1: marketplace.json 업데이트**

spec-from-design 항목의 `"version"` 필드를 `"2.0.0"`으로 변경.

- [ ] **Step 2: README.md 업데이트**

플러그인 목록 테이블에서 spec-from-design 행의 버전을 `v2.0.0`으로 변경.

- [ ] **Step 3: 최종 구조 검증**

```bash
find plugins/spec-from-design/ -type f | sort
```

예상 출력: 총 37개 파일
- plugin.json (1)
- agents/*.md (10)
- SKILL.md + CLAUDE.md + contract.json (3)
- checklists/*.md (5)
- specs/*.md (6)
- templates/*.md (9)
- mappings/*.md (2)
- presets/*.md (1)

총: 37개 파일

- [ ] **Step 4: 4곳 버전 일치 확인**

```bash
grep -r '"version"' plugins/spec-from-design/.claude-plugin/plugin.json \
                    plugins/spec-from-design/skills/spec-from-design/contract.json
grep 'spec-from-design' .claude-plugin/marketplace.json
grep 'spec-from-design' README.md
```

4곳 모두 2.0.0이어야 한다.

- [ ] **Step 5: 커밋**

```bash
git add .claude-plugin/marketplace.json README.md
git commit -m "feat(spec-from-design): v2.0.0 version sync (marketplace + README)"
```

- [ ] **Step 6: 푸시**

```bash
git push
```
