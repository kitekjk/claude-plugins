# 구현 프롬프트 템플릿

## Agent Teams 프롬프트

```text
docs/specs/ 의 Spec을 기반으로 이 프로젝트를 Agent Teams로 처음부터 개발해줘.

팀 구성:
- Teammate 1: 프로젝트 구조 + 인프라
  기반 Spec: architecture-rules.md, infra-config.md, naming-guide.md
  담당: 빌드 설정, Docker, 애플리케이션 설정
  완료 조건: 빌드 성공

- Teammate 2: 도메인 모듈
  기반 Spec: service-definition.md 핵심 모델
  담당: domain/** 만
  의존: Teammate 1 완료 후

- Teammate 3: 애플리케이션 + 인터페이스 + 인프라 모듈
  기반 Spec: Use Case Spec, API Spec, policies/
  담당: application/**, interfaces/**, infrastructure/**
  의존: Teammate 2 완료 후

- Teammate 4: 테스트 코드
  기반 Spec: 각 Use Case "## 테스트 시나리오" (TC-ID, @Tag 필수)
  담당: src/test/** 만
  의존: Teammate 1,2,3 완료 후
  완료 조건: 전체 테스트 통과

규칙:
- Spec에 없는 것은 구현하지 않는다.
- Spec에 모호한 부분이 있으면 최선의 판단으로 구현하되, 판단 근거를 주석으로 남긴다.
- naming-guide.md의 네이밍 규칙을 엄격히 따른다.
- architecture-rules.md의 레이어/의존성 규칙을 엄격히 따른다.
```

## 빌드 검증 프롬프트

```text
빌드 또는 테스트가 실패했습니다. 오류를 분석하고 수정해주세요.

오류 내용:
{error_output}

수정 규칙:
- Spec에 정의된 비즈니스 규칙을 변경하지 않습니다.
- 빌드/설정 문제만 수정합니다.
- 비즈니스 로직 변경이 필요한 경우 Spec을 재확인합니다.
```

## TC-ID 커버리지 확인 프롬프트

```text
다음 TC-ID가 테스트 코드에 @Tag로 존재하는지 확인해주세요:

{tc_id_list}

누락된 TC-ID가 있으면 해당 테스트를 추가로 생성해주세요.
```
