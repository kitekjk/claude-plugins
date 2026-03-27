---
name: review-procedure
description: 절차형 스킬/에이전트 문서의 4요소(Context, Invariant, Verification, Success Criteria) 누락을 자동 검출합니다. "절차 리뷰", "procedure review", "4요소 검증", "스킬 검증", "에이전트 검증", "모호점 검출" 키워드로 트리거됩니다.
allowed-tools: Read, Grep, Glob, Write, Task
---

# review-procedure

## 목적

절차형 스킬과 에이전트 문서를 분석하여, AI가 임의로 단계를 스킵할 수 있는 모호점을 검출합니다.

## 4요소 프레임워크

모든 절차의 모든 단계는 다음 4가지를 포함해야 합니다:

| 요소 | 질문 | 누락 시 위험 |
|------|------|-------------|
| **Context** | 이 단계는 어디서, 언제, 어떤 조건에서 실행되는가? | Action만 있고 실행 맥락 없음 |
| **Invariant** | 이 절차가 실패하지 않으려면 어떤 불변 조건이 필요한가? | 목표만 있고 제약 없음 |
| **Verification** | 잘못된 실행을 막는 검증 단계가 있는가? | Step 후 확인 없음 |
| **Success Criteria** | 성공/실패를 판정할 기준이 있는가? | 완료 선언만 있고 조건 없음 |

## 사용 방법

```
"이 플러그인의 절차를 리뷰해줘"                    # 현재 디렉토리 플러그인
"spec-from-design 절차 리뷰해줘"                  # 특정 플러그인
"이 에이전트의 4요소 검증해줘"                     # 특정 에이전트 파일
"모호점 검출해줘"                                  # 전체 검출
```

## 워크플로우

1. `procedure-reviewer` 에이전트에게 대상 경로 전달
2. 에이전트가 모든 절차 문서 분석
3. 4요소 누락 리포트 생성 (reports/procedure-review-{date}.md)
4. 통계 요약 출력

## 리포트 출력

- HIGH/MEDIUM/LOW 심각도별 분류
- 각 항목에 구체적 수정 제안 포함
- HIGH 1건 이상이면 전체 FAIL 판정
