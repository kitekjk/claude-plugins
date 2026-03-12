# Spec 준수도 리포트 템플릿

```markdown
# Spec 준수도 리포트

## 기본 정보
- Spec: {spec_dir}
- 구현: {impl_dir}
- 검증일: {date}

## 점수 요약

| 영역 | 항목 | 점수 | 비고 |
|------|------|------|------|
| V1 | 기능 구현 완결성 | {score}/40 | {summary} |
| V2 | 비즈니스 규칙 준수 | {score}/30 | {summary} |
| V3 | 아키텍처 준수 | {score}/15 | {summary} |
| V4 | 테스트 커버리지 | {score}/15 | {summary} |
| **총점** | | **{total}/100** | **등급: {grade}** |

## 영역별 상세

### V1: 기능 구현 완결성 ({score}/40)

#### Use Case 구현 현황
| UC-ID | Use Case명 | 구현 여부 | 코드 위치 | 비고 |
|-------|-----------|-----------|-----------|------|
| {uc_id} | {name} | {O/X} | {path} | {note} |

#### API 엔드포인트 구현 현황
| 메서드 | 경로 | 구현 여부 | Controller | 비고 |
|--------|------|-----------|-----------|------|
| {method} | {path} | {O/X} | {controller} | {note} |

### V2: 비즈니스 규칙 준수 ({score}/30)

| 규칙 ID | 규칙 내용 | 준수 여부 | 코드 위치 | 비고 |
|---------|----------|-----------|-----------|------|
| {rule_id} | {description} | {O/X} | {path} | {note} |

### V3: 아키텍처 준수 ({score}/15)

| 규칙 | 준수 여부 | 상세 |
|------|-----------|------|
| {rule} | {O/X} | {detail} |

### V4: 테스트 커버리지 ({score}/15)

- TC-ID 총 수: {total}
- 구현된 TC-ID: {implemented}
- 테스트 통과율: {pass_rate}%

#### 누락된 TC-ID
| TC-ID | Use Case | 시나리오 |
|-------|----------|---------|
| {tc_id} | {uc_name} | {scenario} |

## 미준수 항목 요약

### 수정 필요 항목

{n}. **[V{area} -{점수}점] {미준수 제목}**
   - Spec: {spec_file} > {section}
   - 코드: {code_path}
   - 유형: {누락/불일치/불완전}
   - 상세: {구체적 내용}
   - 권고: {수정 방향}

## 종합 평가

- 총점: {total_score}점 (등급 {grade})
- 주요 강점: {strengths}
- 개선 필요: {improvements}
```
