# procedural-skill-reviewer

절차형 스킬/에이전트 문서의 4요소 누락을 자동 검출하는 리뷰 플러그인.

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
이 플러그인의 절차를 리뷰해줘
spec-from-design 4요소 검증해줘
code-from-spec 모호점 검출해줘
```

## 서브에이전트 구조

```text
procedure-reviewer    # 절차 문서 분석 + 4요소 누락 검출 + 리포트 생성
```

## 리포트

`reports/procedure-review-{date}.md`에 저장. HIGH 항목이 1건 이상이면 전체 FAIL 판정.
