# 결정성 리포트 템플릿

```markdown
# Spec 결정성 리포트

## 기본 정보
- Spec: {spec_dir}
- regen1: {regen1_dir}
- regen2: {regen2_dir}
- 검증일: {date}

## 점수 요약

| Level | 항목 | 점수 | 비고 |
|-------|------|------|------|
| L1 | 테스트 상호 실행 | {score}/30 | {summary} |
| L2 | API 계약 일치 | {score}/25 | {summary} |
| L3 | 비즈니스 시나리오 일치 | {score}/25 | {summary} |
| L4 | 코드 구조 일치 | {score}/10 | {summary} |
| L5 | 네이밍 일치 | {score}/10 | {summary} |
| **총점** | | **{total}/100** | **등급: {grade}** |

## Level별 상세

### L1: 테스트 상호 실행 ({score}/30)

- 컴파일 성공률: {compile_rate}%
- 테스트 통과율: {pass_rate}%

#### 실패 항목
| 방향 | 테스트 | 실패 유형 | 원인 |
|------|--------|-----------|------|
| {regen1→regen2} | {test_name} | {compile/runtime} | {cause} |

### L2: API 계약 일치 ({score}/25)

- 총 엔드포인트: {total}
- 구조 일치: {match}
- 구조 불일치: {mismatch}

#### 불일치 항목
| 엔드포인트 | regen1 | regen2 | 차이 유형 |
|-----------|--------|--------|-----------|
| {path} | {response1} | {response2} | {field/status} |

### L3: 비즈니스 시나리오 일치 ({score}/25)

| 시나리오 | 일치 | regen1 결과 | regen2 결과 |
|----------|------|------------|------------|
| {scenario} | {O/X} | {result1} | {result2} |

### L4: 코드 구조 일치 ({score}/10)

| 패턴 | regen1 | regen2 | 일치 |
|------|--------|--------|------|
| {pattern} | {value1} | {value2} | {O/X} |

### L5: 네이밍 일치 ({score}/10)

| 카테고리 | regen1 | regen2 | 일치 |
|----------|--------|--------|------|
| {class/api/enum} | {name1} | {name2} | {O/X} |

## Spec 보강 대상

### 차이점 상세

{n}. **[L{level} -{점수}점] {차이 제목}**
   - regen1: {값1}
   - regen2: {값2}
   - 보강 대상: {spec_file}
   - 보강 방향: {구체적 보강 내용}

## 보강 후 예상 점수

- 현재: {current_score}점 (등급 {current_grade})
- 예상: {expected_score}점 (등급 {expected_grade})
- 보강 항목: {count}건
```
