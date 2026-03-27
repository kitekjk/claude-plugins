# 작업 계획서

> 생성일: {date}
> Spec 디렉토리: `{spec_dir}`
> Jira 프로젝트: {jira_project}

## 요약

| 항목 | 값 |
|------|-----|
| 총 Spec 수 (스케줄링 대상) | {total_specs} |
| 제외 Spec 수 (이미 완료) | {skipped_specs} |
| 실행 Level 수 | {total_levels} |
| 병렬 실행 가능 | {parallel_count}개 |
| 순차 실행 필요 | {sequential_count}개 |
| Jira 티켓 | {jira_count}개 생성 |

## 제외된 Spec (이미 완료)

| Spec ID | 제목 | status | 제외 사유 |
|---------|------|--------|----------|
| {spec_id} | {title} | {status} | {reason} |

> 제외 Spec이 없으면 이 섹션을 생략합니다.

## 의존성 그래프

```mermaid
graph TD
    %% 의존성 관계를 표시합니다.
    %% spec_id --> 의존하는 spec_id
```

## 실행 순서

### Level 0 (독립 Spec — 병렬 실행)

| Spec ID | 제목 | Jira | 브랜치 |
|---------|------|------|--------|
| {spec_id} | {title} | {jira_key} | {branch} |

### Level 1 (Level 0 의존)

| Spec ID | 제목 | 의존 대상 | Jira | 브랜치 |
|---------|------|-----------|------|--------|
| {spec_id} | {title} | {depends_on} | {jira_key} | {branch} |

### Level N ...

## Jira 티켓 매핑

| Spec ID | Jira Key | 상태 | 실행 Level |
|---------|----------|------|-----------|
| {spec_id} | {jira_key} | To Do | {level} |

## 브랜치 매핑

| 브랜치 | Spec ID | 격리 방식 |
|--------|---------|----------|
| {branch} | {spec_id} | SDK isolation: "worktree" |

## 실행 지침

1. Level 0 Spec들을 병렬로 구현합니다 (최대 {maxParallel}개 동시).
2. Level 0 완료 후 Level 1을 시작합니다.
3. 각 Spec 구현 완료 시:
   - 빌드 + 테스트 통과 확인
   - Spec 파일의 구현 추적 섹션 업데이트
   - Jira 티켓 상태 업데이트
4. 모든 Level 완료 후 전체 통합 검증을 수행합니다.
