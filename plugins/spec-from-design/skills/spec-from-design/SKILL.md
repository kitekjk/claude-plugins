---
name: spec-from-design
description: HLD/LLD 설계 문서에서 코드 생성 가능한 Spec을 생성합니다. 기존 프로젝트와 신규 프로젝트 모두 지원합니다.
allowed-tools: Read, Write, Edit, Grep, Glob, Task, Bash
---

# spec-from-design

## 목적

HLD/LLD 설계 문서 + 코드베이스(또는 프리셋)를 분석하여 **코드 생성 가능한 수준의 Spec 문서**를 생성합니다.

설계 문서 → Spec → 코드 순서의 **정방향 개발 흐름**을 지원합니다.

## 단일 기준

모든 규칙의 기준은 `contract.json`입니다.

- `contract.json`
- `specs/{type}.md`
- `templates/{type}.md`
- `checklists/*.md`
- `mappings/*.md`
- `presets/*.md`

## 두 가지 모드

### existing-project (기존 프로젝트)

기존 코드가 있는 경우. 아키텍처, 네이밍, 기술 스택을 **코드에서 추출**합니다.

| 추출 대상 | 코드 소스 | 용도 |
|----------|----------|------|
| 빌드 시스템 | build.gradle, pom.xml, package.json | 언어/프레임워크 결정 |
| 패키지 구조 | src/ 디렉토리 구조 | architecture-rules.md |
| 네이밍 컨벤션 | 기존 클래스/변수/API 경로 | naming-guide.md |
| 기존 모델 | domain/model/** | 모델 관계 확인 |
| 기존 API | interfaces/web/** 또는 controller/** | 하위호환 확인 |
| 기존 Spec | docs/specs/** | 정책 충돌 확인 |
| 기존 테스트 | src/test/** | TC-ID 패턴, 테스트 스타일 |

### new-project (신규 프로젝트)

코드가 없는 경우. **프리셋**으로 아키텍처/네이밍/기술 스택을 결정합니다.

- 기본 프리셋: `ddd-clean-kotlin`
- 프리셋은 `presets/` 디렉토리에서 관리
- 사용자가 프리셋을 지정하지 않으면 기본 프리셋 사용
- 사용자가 다른 스택을 원하면 새 프리셋 파일 추가 가능

## 서브에이전트 구조

```text
spec-orchestrator
├── design-analyzer         # HLD/LLD 파싱, 기초 Spec
├── usecase-api-writer      # Use Case + API Spec
├── policy-extractor        # 정책/규칙 추출
├── test-scenario-writer    # 테스트 시나리오
└── spec-reviewer           # 품질 평가
```

## 워크플로우

### 0단계: 모드 결정 + 입력 검증
1. 프로젝트에 코드가 있는지 확인 → `existing-project` 또는 `new-project`
2. `new-project`이면 프리셋 확인 (기본: `ddd-clean-kotlin`)
3. HLD/LLD 품질 사전 검증 (`checklists/input-quality.md`)
4. 누락 항목 리포트 → 사용자 확인

### 1단계: 설계 문서 + 맥락 분석
- `design-analyzer`가 HLD/LLD 정독
- `existing-project`: 코드에서 아키텍처/네이밍 추출
- `new-project`: 프리셋에서 아키텍처/네이밍 로드
- service-definition.md, architecture-rules.md, naming-guide.md 초안

### 2단계: Spec 생성 (병렬)
- `usecase-api-writer`: Use Case + API Spec
- `policy-extractor`: 정책 + NFR 정책 + infra-config

### 3단계: 테스트 시나리오 (순차)
- `test-scenario-writer`: 2단계 결과 + LLD FR 검증 기준 → 테스트 시나리오

### 4단계: 품질 게이트
- `spec-reviewer`: 구조 검증 + 결정성 평가 + 추적성 검증
- 80점 미만이면 수정 지시 후 재생성

## 고정 정책

- 출력 구조는 `docs/specs/` 하위
- Spec ID 접두사는 `service-definition.md`에서 결정
- HLD KDD → 정책 규칙 매핑은 `mappings/hld-to-spec.md`
- LLD FR → Use Case 매핑은 `mappings/lld-to-spec.md`
- 프리셋은 구조적 기본값만 제공하며 HLD/LLD 내용을 덮어쓰지 않음

## 사용법

```text
# 기존 프로젝트
"HLD/LLD를 기반으로 Spec을 생성해줘"
"/generate-spec-from-design"
"/generate-spec-from-design [도메인]"

# 신규 프로젝트
"새 프로젝트인데 이 HLD/LLD로 Spec 만들어줘"
"/generate-spec-from-design --preset ddd-clean-kotlin"
```
