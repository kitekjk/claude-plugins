# 통합 Style Guide v7

> Source of truth: `skills/doc-writing-team/contract.json` v2.0.0
> 문서 구조, 저장 경로, 평가 계약은 항상 `contract.json`을 우선합니다.
> `memory/approved_corpus/`는 스타일과 예시를 학습하기 위한 참고 자료이며, 계약을 덮어쓰지 않습니다.

---

## Persona (작성자 관점)

모든 문서는 **Staff Engineer Persona**의 관점으로 작성합니다.
상세 정의는 `memory/personas/staff-engineer.md`를 참조합니다.

- 핵심: 시스템 사고, 기술 리더십 톤, 의사결정 프레이밍
- 대상 문서: ADR, HLD, LLD
- 목적: 구조적 사고와 검증 가능한 판단 근거를 일관되게 유지

---

## Contract Precedence

1. `skills/doc-writing-team/contract.json`
2. `specs/*.md`, `templates/*.md`, `checklists/*.md`
3. `memory/style_guide.md`, `memory/style_summary.md`
4. `memory/approved_corpus/*`

승인 코퍼스에서 Appendix가 보이거나 다른 저장 관례가 보여도, 생성 문서는 반드시 계약을 따릅니다.

---

## Voice & Tone

### Voice
- **전문적이면서 친근함**: 권위적이지 않지만 신뢰감 있는 톤
- **명확하고 간결함**: 불필요한 수식어 배제
- **실용적**: 독자가 바로 활용할 수 있는 정보 제공
- **데이터 중심**: 주장은 반드시 수치나 사례로 뒷받침

### Tone
- **객관적**: 감정적 표현보다 사실 기반
- **솔직함**: 트레이드오프와 한계를 숨기지 않음
- **성장 지향적**: 문제보다 해결책과 다음 행동에 집중

### 관점
- **기술 문서** (ADR, HLD, LLD): 3인칭 또는 중립적 서술
- **결정 서술**: "`~를 채택합니다`", "`~를 선정합니다`" 형식
- **ADR Decision**: 사용자 또는 팀 확인 전에는 반드시 `[TBD]`

### 언어
- **한국어** 기본
- **기술 용어**: 영문 병기 허용
- **약어**: 첫 등장 시 풀네임 명시
- **섹션 제목**: 계약의 정식 섹션명을 우선 사용

---

## Structure Guidelines

### 문단 구성
- 한 문단은 하나의 핵심 메시지만 다룹니다.
- 3-5문장을 기본 단위로 사용합니다.
- 긴 문단은 역할이나 논점 기준으로 분리합니다.

### 제목 레벨
- `#`: 문서 제목만 사용
- `##`: 계약상 섹션
- `###`: 하위 섹션
- `####`: 세부 항목

### 목록 사용
- 순서 없는 나열은 글머리 기호 사용
- 단계, 절차, 실행 계획은 번호 목록 사용
- 완료 추적이 필요할 때만 체크리스트 사용

### 생성 문서 저장 구조

- 본문 저장 경로: `documents/{type}/{slug}/DOCUMENT.md`
- 리뷰 저장 경로: `documents/{type}/{slug}/REVIEW.md`
- 자산 저장 경로: `documents/{type}/{slug}/assets/`
- `{type}`는 `adr`, `hld`, `lld` 중 하나를 사용
- 본문 파일명은 항상 `DOCUMENT.md`
- 루트에 직접 `.md` 파일을 생성하지 않음

예시:

```text
documents/hld/order-routing/
├── DOCUMENT.md
├── REVIEW.md
└── assets/
```

### 문서 타입별 구조 정책

| 타입 | 필수 섹션 | 선택 섹션 | Appendix | 추가 정책 |
|------|----------|----------|----------|----------|
| ADR | Context, Agenda, Decision, Next Step | 없음 | 금지 | Decision은 `[TBD]` 또는 사용자/팀 확인된 값만 허용 |
| HLD | Glossary, Overview, System Context, High-Level Architecture, Key Design Decisions, Non-Functional Requirements | Deployment Overview, Appendix | 허용 | Appendix는 본문을 보조하는 참고 자료로만 사용 |
| LLD | Glossary, Problem Statement, Functional Requirements, Non-Functional Requirements, Goal / Non-Goal, Proposed Design | Appendix | 허용 | Appendix는 상세 표, 보조 계산, 운영 부록에 사용 가능 |

---

## Phrase Bank

### 선호 표현

**동사**

| 한국어 | 영어 | 사용 맥락 |
|--------|------|----------|
| 구현하다 | implement | 기능 개발 |
| 설계하다 | design | 아키텍처 |
| 최적화하다 | optimize | 성능 개선 |
| 검증하다 | validate | 테스트 |
| 분석하다 | analyze | 조사 및 비교 |
| 확장하다 | scale | 용량 증가 |
| 도입하다 | introduce | 새 기술 적용 |
| 채택하다 | adopt | 최종 결정 |
| 선정하다 | select | 옵션 선택 |
| 수립하다 | establish | 전략 및 계획 |

**결정 표현**

| 용도 | 표현 |
|------|------|
| 채택 | "`~를 채택합니다`", "`~를 선정합니다`" |
| 탈락 | "`탈락. {근거}`", "`[Physical Limit]`", "`[Operational Risk]`" |
| 목표 | "`~를 목표로 합니다`", "`~를 보장해야 합니다`" |
| 판단 | "`~로 판단합니다`", "`~라고 판단됩니다`" |

**옵션 탈락 태그**

| 태그 | 의미 |
|------|------|
| `[Physical Limit]` | 물리적 한계 |
| `[Operational Risk]` | 운영 리스크 |
| `[Cost Prohibitive]` | 비용 과다 |
| `[Compatibility]` | 호환성 문제 |

**연결어**
- 결과: 따라서, 그러므로, 결과적으로
- 대조: 그러나, 한편, 반면
- 추가: 또한, 더불어, 아울러
- 예시: 예를 들어, 구체적으로, 가령
- 강조: 특히, 핵심적으로, 무엇보다

**수치 표현**
- Latency: `P99 {X}ms`
- Throughput: `{X} TPS`
- Availability: `{99.X}%`
- RTO/RPO: `RTO {X}분`, `RPO {X}분`
- Data Volume: `일 {X}만 건`, `{X}M rows`

---

## Do / Don’t

### Do

1. 모든 주장에 근거를 남깁니다.
2. 성능, 비용, 볼륨, 가용성은 숫자로 씁니다.
3. 트레이드오프를 명시합니다.
4. 옵션 비교 시 장단점을 균형 있게 기술합니다.
5. HLD는 구조와 관계를, LLD는 구현과 운영 세부를 명확히 분리합니다.
6. Appendix가 허용되는 문서에서도 핵심 결정과 요구사항은 본문에 둡니다.

### Don’t

1. 코퍼스 예시를 이유로 계약을 무시하지 않습니다.
2. ADR에서 작성자가 임의로 Decision을 확정하지 않습니다.
3. HLD/LLD의 Appendix를 필수 섹션 대체 수단으로 사용하지 않습니다.
4. 루트에 단일 `.md` 파일을 바로 생성하지 않습니다.
5. "빠른", "효율적", "적절한"처럼 모호한 표현을 단독 사용하지 않습니다.

---

## Forbidden / Avoid List

### 절대 금지
- "think outside the box"
- "on the same page"
- "game changer"
- "시너지"
- "혁신적인" (근거 없이)
- "획기적인" (근거 없이)
- "패러다임 전환" (근거 없이)
- "당연히"
- "자명하게"

### 주의해서 사용
- "기본적으로" → 삭제하거나 구체화
- "일반적으로" → 예외를 함께 명시
- "등" → 실제 열거 후 사용
- "최적의" → 비교 기준을 명시
- "충분히" → 수치로 대체
- "적절한" → 기준을 함께 제시

### 출처 없이 사용 금지
- 성능 수치
- 비용 데이터
- 벤치마크 결과
- 외부 시스템 SLA/SLO

---

## Formatting Rules

### 마크다운
- 코드 블록은 언어를 명시합니다.
- 함수명, 변수명, 명령어는 인라인 코드로 감쌉니다.
- 핵심 용어는 굵은 글씨를 사용합니다.
- 인용은 정의나 공식 문서 발췌에만 제한적으로 사용합니다.

### 표
- 3열 이상 비교는 표를 우선합니다.
- 헤더는 비교 축을 명확히 드러내야 합니다.

### 다이어그램
- HLD는 `System Context`, `High-Level Architecture` 다이어그램을 기본으로 포함합니다.
- LLD는 복잡한 흐름이나 상태 전이가 있을 때만 Mermaid를 사용합니다.
- Appendix의 보조 다이어그램은 본문 다이어그램을 대체하지 않습니다.

---

## 문서 타입별 참조

| 타입 | 스펙 | 템플릿 | 체크리스트 | Writer |
|------|------|--------|-----------|--------|
| ADR | `specs/adr.md` | `templates/adr.md` | `checklists/adr-checklist.md` | `adr-writer` |
| HLD | `specs/hld.md` | `templates/hld.md` | `checklists/hld-checklist.md` | `hld-writer` |
| LLD | `specs/lld.md` | `templates/lld.md` | `checklists/lld-checklist.md` | `lld-writer` |

공통 평가는 `checklists/common-checklist.md`를 사용합니다.

---

## 피드백 반영 규칙

1. 사용자 피드백은 `memory/feedback_log.jsonl`에 기록합니다.
2. 스키마와 필수 필드는 `skills/doc-writing-team/contract.json`과 `memory/FEEDBACK_SCHEMA.md`를 따릅니다.
3. 생성 문서가 아닌 승인 코퍼스 문서는 피드백의 기본 적용 대상이 아닙니다.
4. 구조나 정책 충돌이 발생하면 항상 계약을 우선합니다.

---

## 기술 문서 패턴

### 옵션 비교 패턴

```markdown
| 옵션 | 장점 | 단점 | 선정 여부 |
|------|------|------|----------|
| Option A | {장점} | {단점} | 탈락. [Operational Risk] |
| Option B | {장점} | {단점} | **채택** |
```

### 컴포넌트 설명 패턴

```markdown
### {컴포넌트명}

**Challenge:** {핵심 제약}
**Strategy:** {선택한 전략과 이유}
**Resilience:** {장애 대응과 복구 방식}
```

### Appendix 사용 패턴

```markdown
## Appendix

### A.1 보조 계산
{본문의 판단 근거를 보강하는 계산식}

### A.2 참고 표
{세부 파라미터, 매핑표, 추가 예시}
```

Appendix는 HLD와 LLD에서만 사용합니다.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v7 | 2026-03-09 | `contract.json` v2.0.0 기준으로 계약 우선순위, 저장 경로, HLD 1급 지원, Appendix 정책, ADR Decision 정책 정렬 |
| v6 | 2026-01-16 | 문서 저장 구조 가이드 추가 |
| v5 | 2026-01-09 | Persona 섹션 축약 |
| v4 | 2026-01-05 | Staff Engineer Persona 도입 |
| v3 | 2025-12-31 | 승인된 코퍼스 기반 패턴 반영 |
| v2 | 2025-12-30 | 초기 통합 스타일 가이드 |

*Last updated: 2026-03-09*
*Version: 7*


## Auto-applied Update Notes

Updated at: 2026-03-08T16:58:49.698641+00:00

- [fb_260116_150000_001] Structure Guidelines / add: 문서 저장 구조 규칙 - 폴더 단위 관리, DOCUMENT.md 고정, 루트 직접 생성 금지
