# spec-from-design v2.0.0 설계 문서

## 1. 배경

HLD/LLD 설계 문서 및 개발요청서(Dev Request)에서 코드 생성 가능한 Spec을 추출하는 멀티 에이전트 플러그인 v2.0.0 재설계.
기존 v1.7.0을 삭제하고 처음부터 생성한다.
또한, 엣지 케이스를 포함한 다양한 테스트 시나리오를 제공한다.

### 1.1 핵심 문제

| 문제 | 원인 | 해결 방향 |
|------|------|----------|
| LLM이 LLD 내용 보고 usecase → service로 오분류 | 키워드 기반 판단 | 진입점 유형 기반 분류로 전환 |
| 여러 구현 클래스를 하나의 Spec으로 묶음 | 타입 단위로 묶으려는 경향 | 각 구현 클래스 = 하나의 Spec 원칙 강제 |
| soft rule을 LLM이 무시 | 프롬프트 기반 가드레일의 한계 | 구조적 제약(에이전트 분리, 검증 게이트)으로 대체 |

### 1.2 설계 원칙

1. **식별 단위는 구현 클래스**: 각 ActivityImpl 클래스가 개별 Spec의 단위
2. **유형 판단은 진입점으로**: LLD 내용이 아니라 진입점 유형으로 분류
3. **프롬프트가 아니라 구조로 강제**: 식별과 작성을 에이전트 수준에서 분리

---

## 2. 에이전트 파이프라인

### 2.1 10개 에이전트

```
orchestrator ─┬─① design-analyzer        (opus)
              ├─② usecase-identifier      (opus)
              ├─③ identification-verifier  (sonnet) ← 게이트
              ├─④ policy-extractor        (opus)
              ├─⑤ usecase-writer          (opus)
              ├─⑥ scope-evaluator         (sonnet)
              ├─⑦ usecase-splitter        (opus, 조건부)
              ├─⑧ test-scenario-writer    (sonnet)
              └─⑨ spec-reviewer           (opus) ← 게이트
```

### 2.2 에이전트 상세

| 에이전트 | model | tools | 역할 |
|---------|-------|-------|------|
| spec-orchestrator | - | Read,Write,Edit,Glob,Grep,Task,Bash | 파이프라인 조율, 모드 판별, 게이트 관리 |
| design-analyzer | opus | Read,Write,Edit,Glob,Grep | HLD/LLD/Dev Request 파싱, Foundation 문서 생성 |
| usecase-identifier | opus | Read,Write,Glob,Grep | 구현 클래스 열거, 진입점 유형 판별, UC 목록 산출 |
| identification-verifier | sonnet | Read,Grep | UC 목록 완전성·1:1 매핑 검증 |
| policy-extractor | opus | Read,Write,Edit,Glob,Grep | HLD KDD + LLD 설계 판단에서 정책 추출 |
| usecase-writer | opus | Read,Write,Edit,Glob,Grep | 검증된 UC 목록 기반 Spec 작성 (1 UC = 1 파일) |
| scope-evaluator | sonnet | Read,Grep | 각 Spec의 규모 판단 (수치 비교) |
| usecase-splitter | opus | Read,Write,Edit,Glob,Grep | 대규모 UC를 model/service Spec으로 분해 |
| test-scenario-writer | sonnet | Read,Write,Edit,Glob,Grep | Given-When-Then 테스트 시나리오 생성 |
| spec-reviewer | opus | Read,Grep,Glob,Bash | 100점 만점 품질 평가, auto-FAIL 검증 |

**model 선택 기준**: opus = 설계 판단·분석·창작 필요, sonnet = 구조화된 검증·비교 작업

### 2.3 데이터 흐름

| 단계 | 에이전트 | 입력 | 출력 |
|------|---------|------|------|
| ① | design-analyzer | HLD/LLD/Dev Request 파일 | 파싱된 설계 정보 + Foundation 문서 3종 |
| ② | usecase-identifier | 파싱된 설계 정보 | UC 식별 목록 (클래스명, 진입점 유형, 도메인) |
| ③ | identification-verifier | UC 식별 목록 + 파싱된 설계 정보 | pass / fail + 누락·중복 리포트 |
| ④ | policy-extractor | HLD KDD + LLD 설계 판단 | Policy 파일들 |
| ⑤ | usecase-writer | 검증된 UC 목록 + 설계 정보 + Policy | Spec 파일들 (1 UC = 1 파일) |
| ⑥ | scope-evaluator | Spec 파일들 | 각 Spec별 pass / split-needed |
| ⑦ | usecase-splitter | split-needed Spec + 설계 정보 | 축소된 usecase + model/service Spec |
| ⑧ | test-scenario-writer | 최종 Spec 파일들 | 각 Spec에 테스트 시나리오 섹션 추가 |
| ⑨ | spec-reviewer | 전체 Spec 세트 | 검증 리포트 (90점+ pass) |

### 2.4 게이트 정책

- **③ identification-verifier**: fail 시 ②를 피드백과 함께 재실행 (최대 2회 재시도 = 총 3회 시도, 초과 시 사용자 판단)
  - 피드백 형식: 누락된 클래스 목록, 중복 매핑 목록, 제외 사유 불명확 항목
- **⑨ spec-reviewer**: fail 시 ⑤를 피드백과 함께 재실행 (최대 2회 재시도 = 총 3회 시도, 초과 시 사용자 판단)
  - 피드백 형식: 감점 카테고리별 상세 사유, auto-FAIL 위반 항목

---

## 3. 식별 규칙

### 3.1 식별 단위

**원칙: 각 구현 클래스 = 하나의 Spec**

### 3.2 진입점 유형

```json
{
  "entryPointPrinciple": "외부 요청을 직접 수신하는 클래스/메서드",
  "entryPoints": [
    "REST API (Controller 엔드포인트 메서드)",
    "Temporal Activity (ActivityImpl 클래스)",
    "Temporal Workflow (WorkflowImpl 클래스)",
    "Kafka Consumer (Consumer 클래스)",
    "Scheduler (@Scheduled 메서드)"
  ],
  "customEntryPoints": []
}
```

- 기본 5개 + `customEntryPoints`로 프로젝트별 확장 가능
- preset이나 사용자가 직접 추가 (Socket, gRPC, Batch Job 등)

### 3.3 분류 규칙

- **기본 유형은 항상 usecase**: LLD 내용과 무관
- **model/service는 분해 전용**: scope-evaluator가 split-needed 판정 시에만 생성
- **refactoring/performance**: LLD에서 명시적으로 분류한 항목만

---

## 4. 분해 규칙

### 4.1 scope-evaluator 기준

| 조건 | 판정 |
|------|------|
| 수정 대상 파일 ≤ 10개 AND FR ≤ 5개 | pass (분해 불필요) |
| 수정 대상 파일 > 10개 OR FR > 5개 | split-needed |

### 4.2 usecase-splitter 동작

- split-needed Spec을 model + service + usecase(축소)로 분해
- 조건부 실행 — split-needed가 없으면 스킵

---

## 5. contract.json 구조

```json
{
  "version": "2.0.0",
  "modes": {
    "existing-project": "코드에서 아키텍처 추출 (build files, package structure, naming conventions)",
    "new-project": "preset 사용 (기본: ddd-clean-kotlin)"
  },
  "pipeline": [
    "design-analyzer",
    "usecase-identifier",
    "identification-verifier",
    "policy-extractor",
    "usecase-writer",
    "scope-evaluator",
    "usecase-splitter",
    "test-scenario-writer",
    "spec-reviewer"
  ],
  "classificationFlow": {
    "phase1": "모든 진입점 → usecase 유형",
    "phase2": "scope-evaluator 판정 → split-needed만 분해"
  },
  "identificationRules": {
    "unit": "각 구현 클래스 = 하나의 Spec",
    "entryPointPrinciple": "외부 요청을 직접 수신하는 클래스/메서드",
    "entryPoints": [
      "REST API (Controller 엔드포인트 메서드)",
      "Temporal Activity (ActivityImpl 클래스)",
      "Temporal Workflow (WorkflowImpl 클래스)",
      "Kafka Consumer (Consumer 클래스)",
      "Scheduler (@Scheduled 메서드)"
    ],
    "customEntryPoints": []
  },
  "decompositionThreshold": {
    "files": 10,
    "functionalRequirements": 5
  },
  "retryLimits": {
    "identification-verifier": 2,
    "spec-reviewer": 2
  },
  "outputRules": {
    "singleFilePerSpec": true,
    "noImplementationCode": true,
    "pseudocodeAllowed": true,
    "specPrefix": "SPEC-{PREFIX}-{DOMAIN}-{number}-{name}"
  },
  "storagePaths": {
    "specs": "docs/specs/",
    "policies": "docs/policies/",
    "foundation": "docs/",
    "pathFlexibility": true
  },
  "hardGuardrails": [
    "model/service는 분해 산출물로만 생성",
    "orchestrator가 지정 유형을 writer에 전달",
    "writer는 지정 유형 변경 불가",
    "유형 불일치 시 reviewer auto-FAIL"
  ],
  "qualityGates": {
    "passThreshold": 90,
    "categories": 8,
    "maxScore": 100
  }
}
```

---

## 6. 체크리스트

| 파일 | 용도 | 사용 시점 |
|------|------|----------|
| input-quality.md | HLD/LLD 필수 항목 존재 여부 | ① analyzer 진입 전 |
| identification-completeness.md | LLD 구현 클래스 전수 식별 여부 | ③ verifier |
| one-to-one-mapping.md | 1클래스 = 1Spec 매핑 검증 | ③ verifier |
| output-quality.md | 8카테고리 100점 만점, 90점+ pass | ⑨ reviewer |
| traceability.md | HLD/LLD → Spec 추적성 | ⑨ reviewer |

### 6.1 output-quality.md 배점

| ID | 카테고리 | 배점 | 평가 내용 |
|----|---------|------|----------|
| Q1 | 구조 완결성 | 10 | 필수 섹션 존재, 메타데이터 완전성 |
| Q2 | 모호성 | 15 | 모호한 표현 없음, 수치 기반, 테스트 가능 |
| Q3 | 분기 커버리지 | 20 | 기본흐름 + 대안흐름, 모든 분기 커버 |
| Q4 | 참조 완결성 | 10 | Policy/Spec/모델 링크 유효 |
| Q5 | 테스트 도출 가능성 | 15 | Given-When-Then, TC-ID, 레벨 분류 |
| Q6 | HLD/LLD 추적성 | 10 | 출처 명시, 커버리지 매핑 |
| Q7 | YAGNI | 10 | HLD/LLD에 없는 추가 기능 없음 |
| Q8 | 스코프 적정성 | 10 | 단일 관심사, 배포 가능 단위 |

**auto-FAIL 조건** (점수 무관):
- Spec에 구현 코드 블록 포함 (yaml dependsOn 및 pseudocode는 허용)
- 1 Spec ≠ 1 파일
- 유형이 orchestrator 지정과 불일치
- model/service가 분해 없이 단독 생성

---

## 7. Spec 템플릿

```markdown
# SPEC-{PREFIX}-{DOMAIN}-{number}-{name}

## 기본 정보
- 유형: usecase | model | service | refactoring | performance
- 도메인: {도메인}
- 출처: {LLD 참조}
- 진입점 유형: {REST API | Temporal Activity | ...}
- 구현 클래스: {클래스명}
- 구현 상태: not-started

## 개요
...

## 수정 대상 파일
...

## 의존성 (dependsOn)
...

## 기본 흐름
1. ...
2. ...

## 대안 흐름
...

## 검증 조건
...

## 테스트 시나리오
...

## 관련 정책
...
```

**구현 상태 값:**

| 값 | 의미 | 설정 주체 |
|----|------|----------|
| not-started | 초기값 | spec-from-design (writer) |
| in-progress | 구현 중 | code-from-spec |
| completed | 구현 완료 | code-from-spec |
| verified | 검증 통과 | code-from-spec (spec-verifier) |

---

## 8. 디렉토리 구조

```
plugins/spec-from-design/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── spec-orchestrator.md
│   ├── design-analyzer.md
│   ├── usecase-identifier.md
│   ├── identification-verifier.md
│   ├── policy-extractor.md
│   ├── usecase-writer.md
│   ├── scope-evaluator.md
│   ├── usecase-splitter.md
│   ├── test-scenario-writer.md
│   └── spec-reviewer.md
└── skills/spec-from-design/
    ├── SKILL.md
    ├── CLAUDE.md
    ├── contract.json
    ├── checklists/
    │   ├── input-quality.md
    │   ├── output-quality.md
    │   ├── traceability.md
    │   ├── identification-completeness.md
    │   └── one-to-one-mapping.md
    ├── specs/
    │   ├── usecase.md
    │   ├── model.md
    │   ├── service.md
    │   ├── refactoring.md
    │   ├── performance.md
    │   └── policy.md
    ├── templates/
    │   ├── usecase.md
    │   ├── model.md
    │   ├── service.md
    │   ├── refactoring.md
    │   ├── performance.md
    │   ├── policy.md
    │   ├── service-definition.md
    │   ├── architecture-rules.md
    │   └── naming-guide.md
    ├── mappings/
    │   ├── hld-to-spec.md
    │   └── lld-to-spec.md
    └── presets/
        └── ddd-clean-kotlin.md
```

---

## 9. 버전 동기화

v2.0.0 반영 대상 4곳:
1. `plugins/spec-from-design/.claude-plugin/plugin.json` → `"version": "2.0.0"`
2. `plugins/spec-from-design/skills/spec-from-design/contract.json` → `"version": "2.0.0"`
3. `.claude-plugin/marketplace.json` → spec-from-design 항목
4. `README.md` → 플러그인 목록 테이블

---

## 10. 입력 소스

### 10.1 지원 입력

| 입력 | 필수 | 설명 |
|------|------|------|
| HLD | 선택 | 고수준 설계 (KDD, NFR, 상태 모델) |
| LLD | 필수 | 저수준 설계 (FR, 클래스 설계, API 설계) |
| Dev Request | 선택 | 개발요청서 (요구사항, 배경, 제약조건) |

### 10.2 입력 규모별 모드

| 규모 | 입력 조합 | design-analyzer 동작 |
|------|----------|---------------------|
| full | HLD + LLD (+ Dev Request) | HLD + LLD 파싱, Foundation 문서 생성 |
| lld-only | LLD만 (+ Dev Request) | LLD만 파싱, Foundation 문서 기존 것 재사용 또는 코드에서 추출 |
| request-only | Dev Request만 | Dev Request에서 요구사항 추출, 아키텍처는 코드에서 추출 |

---

## 11. plugin.json 명세

```json
{
  "name": "spec-from-design",
  "version": "2.0.0",
  "description": "HLD/LLD 설계 문서 및 개발요청서에서 코드 생성 가능한 Spec을 추출하는 멀티 에이전트 플러그인",
  "agents": [
    { "name": "spec-orchestrator", "path": "./agents/spec-orchestrator.md" },
    { "name": "design-analyzer", "path": "./agents/design-analyzer.md" },
    { "name": "usecase-identifier", "path": "./agents/usecase-identifier.md" },
    { "name": "identification-verifier", "path": "./agents/identification-verifier.md" },
    { "name": "policy-extractor", "path": "./agents/policy-extractor.md" },
    { "name": "usecase-writer", "path": "./agents/usecase-writer.md" },
    { "name": "scope-evaluator", "path": "./agents/scope-evaluator.md" },
    { "name": "usecase-splitter", "path": "./agents/usecase-splitter.md" },
    { "name": "test-scenario-writer", "path": "./agents/test-scenario-writer.md" },
    { "name": "spec-reviewer", "path": "./agents/spec-reviewer.md" }
  ],
  "skills": [
    { "name": "spec-from-design", "path": "./skills/spec-from-design" }
  ]
}
```

---

## 12. SKILL.md 명세

```markdown
---
name: spec-from-design
description: HLD/LLD 설계 문서에서 코드 생성 가능한 Spec을 생성합니다. 기존 프로젝트와 신규 프로젝트 모두 지원합니다.
allowed-tools: Read, Write, Edit, Glob, Grep, Task, Bash
---

{스킬 본문 — orchestrator 호출 흐름, 입력 안내, 모드 선택 로직}
```

트리거 키워드: "Spec 생성", "HLD에서 Spec", "LLD에서 Spec", "설계 문서에서 Spec", "Spec 추출"

---

## 13. CLAUDE.md (플러그인 내부 규칙)

플러그인 스코프의 내부 규칙 파일. 내용:

- contract.json이 단일 기준 — 다른 파일과 충돌 시 contract.json을 따름
- No-code 원칙: 구현 코드 금지, pseudocode는 허용
- 에이전트 역할 분리: orchestrator는 조율만, writer는 작성만, reviewer는 평가만
- 직접 작성 금지: orchestrator/reviewer가 Spec 본문을 직접 쓰거나 고치지 않음
- 식별과 작성 분리: identifier가 식별, writer가 작성 — 역할 교차 금지

---

## 14. specs/ vs templates/ 구분

| 디렉토리 | 용도 | 내용 |
|----------|------|------|
| `specs/` | Spec 유형 정의 | 각 유형의 목적, 생성 조건, 필수/선택 섹션, 제약 사항 |
| `templates/` | 출력 템플릿 | 실제 Markdown 골격 (작성자가 채울 빈 구조) |

예시 — `specs/usecase.md`:
```markdown
# usecase 유형 정의

## 목적
외부 진입점을 통해 시작되는 하나의 기능 단위를 기술

## 생성 조건
- 진입점 유형에 해당하는 구현 클래스가 식별되었을 때
- 기본 유형 — 별도 분류 판정 없이 자동 할당

## 필수 섹션
기본 정보, 개요, 수정 대상 파일, 의존성, 기본 흐름, 검증 조건, 테스트 시나리오

## 선택 섹션
대안 흐름, 관련 정책

## 제약 사항
- 구현 코드 금지 (pseudocode 허용)
- 1 Spec = 1 파일
- 구현 상태 초기값: not-started
```

예시 — `specs/model.md`:
```markdown
# model 유형 정의

## 목적
엔티티/스키마 레이어 변경을 기술

## 생성 조건
- scope-evaluator가 split-needed 판정한 usecase Spec의 분해 산출물로만 생성
- 단독 생성 금지 (hardGuardrail)

## 필수 섹션
기본 정보, 개요, 모델 변경사항, 필드 정의, 관계, 마이그레이션

## 제약 사항
- 반드시 부모 usecase Spec을 참조해야 함
```

---

## 15. 매핑 규칙 구조

### 15.1 hld-to-spec.md

| HLD 요소 | Spec 매핑 대상 |
|----------|---------------|
| KDD (핵심 설계 판단) | Policy 규칙 |
| NFR (비기능 요구사항) | NFR Policy (POLICY-NFR-001) |
| 상태 전이 모델 | 상태 Policy 규칙 |
| System Context | infra-config.md |

### 15.2 lld-to-spec.md

| LLD 요소 | Spec 매핑 대상 | 비고 |
|----------|---------------|------|
| 구현 클래스 (진입점) | UC 식별 목록 | identifier가 처리 |
| FR (기능 요구사항) | 기본 흐름 (번호 리스트) | writer가 변환 |
| FR 검증 기준 | 테스트 시나리오 (Given-When-Then) | test-scenario-writer |
| 클래스/컴포넌트 설계 | 수정 대상 파일 + dependsOn | writer |
| 설계 판단 | 대안 흐름 + Policy | writer + policy-extractor |
| 미해결 리스크 | 엣지 케이스 테스트 | test-scenario-writer |
| DB 스키마 | model Spec 필드 정의 | splitter (분해 시) |

**진입점 유형별 매핑 규칙:**

| 진입점 유형 | 클래스 → Spec 제목 | 주요 매핑 |
|------------|-------------------|----------|
| REST API | `POST /api/orders` → `SPEC-...-create-order` | request/response → 수정 대상 파일 |
| Temporal Activity | `SapPoSendActivityImpl` → `SPEC-...-sap-po-send` | Activity 파라미터 → 기본 흐름 입력 |
| Temporal Workflow | `PoProcessingWorkflowImpl` → `SPEC-...-po-processing` | Workflow 시퀀스 → 기본 흐름 단계 |
| Kafka Consumer | `OrderEventConsumer` → `SPEC-...-order-event` | 이벤트 페이로드 → 기본 흐름 입력 |
| Scheduler | `@Scheduled dailySync()` → `SPEC-...-daily-sync` | 스케줄 설정 → 기본 정보 |

---

## 16. Preset 시스템

### 16.1 preset 파일 형식

```markdown
# {preset-name}

## 기술 스택
- 언어: ...
- 프레임워크: ...
- 빌드: ...
- DB: ...
- 테스팅: ...

## 레이어 구조
...

## 네이밍 규칙
...

## 추가 진입점 (customEntryPoints)
(프로젝트별 진입점이 있으면 여기에 추가)
```

### 16.2 모드 선택 로직

1. 사용자가 명시적으로 지정 → 해당 모드 사용
2. 미지정 시 orchestrator가 자동 판별:
   - 프로젝트 루트에 소스 코드 존재 → `existing-project`
   - 소스 코드 없음 → `new-project` + preset 선택 요청

### 16.3 기본 제공 preset

- `ddd-clean-kotlin.md`: Kotlin 2.x + Spring Boot 3.x + JDK 21 + MySQL 8.x + Clean Architecture

---

## 17. 설계 결정 기록

| 결정 | 근거 |
|------|------|
| Spec 템플릿에 진입점 유형/구현 클래스 필드 추가 | identifier 식별 결과의 추적성 확보 |
| 구현 상태 필드 추가 (초기값 not-started) | code-from-spec과의 라이프사이클 연동 |
| pseudocode 허용 | 자연어만으로 표현하기 어려운 알고리즘 흐름 기술 지원 |
| Dev Request를 입력 소스로 추가 | HLD/LLD 없이 개발요청서만으로도 Spec 생성 가능하도록 |
| customEntryPoints 확장 구조 | Socket, gRPC, Batch Job 등 프로젝트별 진입점 대응 |

---

## 18. 구현 접근

1. 기존 `plugins/spec-from-design/` 전체 삭제
2. 위 디렉토리 구조대로 완전 신규 생성
3. v1.7.0 코드 참조 없이 이 문서 + `spec-from-design-rebuild-prompt.md`만으로 작성
