# 프리셋 가이드

## 프리셋이란?

new-project 모드에서 코드가 없을 때 아키텍처, 네이밍, 기술 스택의 **기본값**을 제공하는 파일입니다.

## 기본 프리셋

- `ddd-clean-kotlin.md` — DDD + Clean Architecture + Kotlin/Spring Boot

## 새 프리셋 추가 방법

1. 이 디렉토리에 `{이름}.md` 파일을 추가합니다.
2. `contract.json`의 `presets.available` 배열에 이름을 추가합니다.
3. 다음 섹션을 포함합니다:
   - 기술 스택
   - 레이어 구조
   - 의존성 규칙
   - 네이밍 컨벤션 (패키지, 클래스, API 경로, 변수)
   - 테스트 규칙

## 프리셋 vs HLD/LLD

프리셋은 **기본값**일 뿐입니다. HLD/LLD 내용과 충돌하면 항상 HLD/LLD가 우선합니다.

예: 프리셋이 Kotlin을 기본으로 하지만 HLD에서 Java를 명시하면 Java로 Spec을 생성합니다.

## 사용법

```text
# 기본 프리셋 사용
/generate-spec-from-design

# 특정 프리셋 지정
/generate-spec-from-design --preset ddd-clean-kotlin
```
