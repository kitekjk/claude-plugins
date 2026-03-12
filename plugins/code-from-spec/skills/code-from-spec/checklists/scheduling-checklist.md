# 스케줄링 체크리스트

## S-00: 사전 확인

- [ ] Spec 디렉토리가 존재하고 1개 이상 Spec 파일이 있는가
- [ ] Git 저장소가 초기화되어 있는가
- [ ] Jira MCP 서버 연결이 가능한가
- [ ] Jira 프로젝트 키가 지정되었는가

## S-01: Spec 수집

- [ ] 모든 Spec 파일을 정상 파싱했는가
- [ ] 기초 Spec(service-definition, architecture-rules, naming-guide)을 스케줄링 대상에서 제외했는가
- [ ] 스케줄링 대상 Spec 수가 1개 이상인가

## S-02: 의존성 분석

- [ ] 모든 Spec의 `dependsOn` 메타데이터를 추출했는가
- [ ] `dependsOn`이 없는 Spec은 독립 Spec으로 분류했는가
- [ ] 순환 의존성이 없는가 (있으면 FAIL → 사용자 보고)
- [ ] 의존 대상 Spec ID가 실제 존재하는 Spec을 가리키는가

## S-03: 실행 순서

- [ ] 위상 정렬이 정상 완료되었는가
- [ ] 모든 Spec에 실행 Level이 할당되었는가
- [ ] 같은 Level 내 병렬 수가 `maxParallel`을 초과하지 않는가

## S-04: Jira 티켓

- [ ] 기존 티켓이 있는 Spec은 중복 생성하지 않았는가
- [ ] 모든 대상 Spec에 Jira 티켓이 생성되었는가
- [ ] 티켓 제목이 `[Spec] {spec_id}: {title}` 형식인가
- [ ] 의존 관계가 Jira 이슈 링크로 반영되었는가

## S-05: Git worktree

- [ ] 기존 worktree를 확인하고 재사용했는가
- [ ] 모든 대상 Spec에 worktree가 생성되었는가
- [ ] 브랜치명이 `{jira_key}-{spec_id_kebab}` 형식인가
- [ ] worktree 경로가 접근 가능한가

## S-06: 구현 추적

- [ ] 모든 대상 Spec 파일에 구현 추적 섹션이 있는가
- [ ] 기존 구현 추적 정보를 덮어쓰지 않았는가
- [ ] `status`, `jiraTicket`, `branch` 필드가 올바르게 기록되었는가

## S-07: 작업 계획서

- [ ] `reports/work-plan-{date}.md`가 생성되었는가
- [ ] 의존성 그래프(Mermaid)가 포함되었는가
- [ ] 실행 순서 테이블이 Level별로 정리되었는가
- [ ] Jira 매핑 테이블이 포함되었는가
- [ ] Worktree 매핑 테이블이 포함되었는가

## 판정

- 모든 섹션 통과: **PASS**
- S-02 순환 의존성 발견: **FAIL** → 사용자 보고 후 중단
- S-04 Jira 연결 실패: **WARN** → Jira 없이 worktree만 생성 후 계속
- 기타 FAIL: 해당 단계 수정 후 재시도
