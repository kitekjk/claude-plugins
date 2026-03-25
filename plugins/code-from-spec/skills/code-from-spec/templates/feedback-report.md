# Spec 피드백 리포트 템플릿

```markdown
# Spec 피드백 리포트

## 기본 정보
- Spec: {spec_dir}
- 구현: {impl_dir}
- 피드백일: {date}

## 요약

| 항목 | 수 |
|------|-----|
| 모호점 로그 (AMB) | {amb_count} |
| 검증 Spec 갭 | {gap_count} |
| PR 리뷰 피드백 (REV) | {rev_count} |
| 총 피드백 항목 | {total_count} |
| 승인된 항목 | {approved_count} |
| 반영된 항목 | {applied_count} |

## 카테고리별 분포

| 카테고리 | 항목 수 | 수정된 Spec |
|----------|---------|------------|
| 비즈니스 규칙 모호 | {count} | policies/{file} |
| Spec 흐름/조건 미명시 | {count} | {spec_file} |
| 도메인 모델 모호 | {count} | service-definition.md / {model_spec_file} |
| 아키텍처 규칙 부족 | {count} | architecture-rules.md |
| 네이밍 규칙 부족 | {count} | naming-guide.md |
| 테스트 시나리오 부족 | {count} | {spec_file} |

## 피드백 항목 상세

### 항목 #{n}

- **소스**: {ambiguity-log AMB-{nn} / compliance-report V{n} / pr-review REV-{nn}}
- **카테고리**: {카테고리}
- **Spec 파일**: {spec_file_path}
- **섹션**: {section_name}
- **현재 상태**: {현재 Spec 내용 또는 "미기술"}
- **문제**: {무엇이 모호하거나 누락되었는지}
- **수정 제안**: {추가/수정할 구체적 내용}
- **근거**: {구현 시 어떤 판단을 했고, 왜 명시가 필요한지}
- **승인 상태**: {승인 / 거부 / 수정 후 승인}

## 수정된 Spec 파일 목록

| 파일 | 수정 항목 수 | 변경 요약 |
|------|-------------|-----------|
| {file_path} | {count} | {summary} |
```
