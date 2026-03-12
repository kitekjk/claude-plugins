# Style Summary (토큰 효율 버전)

> Source of truth: `skills/doc-writing-team/contract.json` v2.0.0
> 전체 규칙은 `memory/style_guide.md v7`을 참조합니다.

---

## Contract Essentials

- 생성 문서 저장 경로: `documents/{type}/{slug}/DOCUMENT.md`
- 선택 파일: `documents/{type}/{slug}/REVIEW.md`, `documents/{type}/{slug}/assets/`
- 루트에 직접 `.md` 파일 생성 금지
- 공통 체크리스트 적용 대상: ADR, HLD, LLD
- 통과 기준: **88점**
- 승인 코퍼스는 **style reference only**, 구조와 정책은 `contract.json`이 결정

---

## Document Type Rules

| 타입 | 필수 섹션 | 선택 섹션 | Appendix | 핵심 정책 |
|------|----------|----------|----------|----------|
| ADR | Context, Agenda, Decision, Next Step | 없음 | 금지 | Decision은 `[TBD]` 또는 사용자/팀 확인값만 허용 |
| HLD | Glossary, Overview, System Context, High-Level Architecture, Key Design Decisions, Non-Functional Requirements | Deployment Overview, Appendix | 허용 | HLD는 전체 구조와 핵심 설계 결정을 책임짐 |
| LLD | Glossary, Problem Statement, Functional Requirements, Non-Functional Requirements, Goal / Non-Goal, Proposed Design | Appendix | 허용 | LLD는 HLD를 구현 수준으로 상세화 |

---

## Voice & Tone

- 전문적이되 과장하지 않음
- 모든 주장에 근거 포함
- 트레이드오프를 숨기지 않음
- 기술 문서는 3인칭 또는 중립적 서술 사용

---

## Phrase Bank

**결정 표현**
- 채택: "`~를 채택합니다`", "`~를 선정합니다`"
- 탈락: "`탈락. [Physical Limit]`", "`탈락. [Operational Risk]`"

**수치 형식**
- Latency: `P99 {X}ms`
- Throughput: `{X} TPS`
- Availability: `{99.X}%`
- RTO/RPO: `RTO {X}분`, `RPO {X}분`

**금지 표현**
- "시너지", "혁신적인", "획기적인" (근거 없이)
- "game changer", "패러다임 전환"
- "당연히", "자명하게"

---

## Non-Negotiables

- 코퍼스 예시보다 계약이 우선
- ADR 작성자가 임의로 Decision 확정 금지
- HLD/LLD Appendix는 허용되지만 본문 대체 불가
- 수치, 비용, SLA는 출처 없이 쓰지 않음

---

## Patterns

**옵션 비교**

```markdown
| 옵션 | 장점 | 단점 | 선정 여부 |
|------|------|------|----------|
| A | ... | ... | 탈락. [Compatibility] |
| B | ... | ... | **채택** |
```

**컴포넌트 설명**

```markdown
### {컴포넌트명}
**Challenge:** ...
**Strategy:** ...
**Resilience:** ...
```

---

*Source: `memory/style_guide.md` v7 + `skills/doc-writing-team/contract.json` v2.0.0*
*Last: 2026-03-09*
