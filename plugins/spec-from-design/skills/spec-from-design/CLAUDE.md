# spec-from-design 내부 규칙

이 파일은 spec-from-design 플러그인 내 모든 에이전트가 따라야 하는 내부 규칙입니다.

## 1. contract.json 단일 기준

`contract.json`이 이 플러그인의 **단일 기준**입니다. 다른 파일(specs, templates, checklists, agents)과 충돌이 발생하면 contract.json을 따릅니다.

## 2. No-code 원칙

- **구현 코드 금지**: Spec에 Java, Kotlin, Python 등 구현 코드 블록을 포함하지 않습니다.
- **pseudocode 허용**: 자연어만으로 표현하기 어려운 알고리즘 흐름은 pseudocode로 기술할 수 있습니다.
- **yaml dependsOn 허용**: 의존성 표현을 위한 yaml 블록은 구현 코드로 간주하지 않습니다.

## 3. 에이전트 역할 분리

각 에이전트는 지정된 역할만 수행합니다:

| 에이전트 유형 | 역할 | 금지 사항 |
|-------------|------|----------|
| orchestrator | 파이프라인 조율, 모드 판별, 게이트 관리 | Spec 본문 직접 작성/수정 |
| identifier | 구현 클래스 식별, UC 목록 산출 | Spec 작성, 유형 변경 |
| verifier (identification) | 식별 완전성·1:1 매핑 검증 | Spec 작성/수정, 식별 목록 수정 |
| writer | 검증된 UC 기반 Spec 작성 | 유형 변경, 식별 작업 |
| verifier (traceability) | HLD/LLD ↔ Spec 양방향 전수 대조 | Spec/Policy 직접 수정, 매핑 임의 보완 |
| reviewer | 품질 평가, auto-FAIL 검증 | Spec 본문 직접 수정 |

## 4. 직접 작성 금지

- **orchestrator**가 Spec 본문을 직접 쓰거나 고치지 않습니다.
- **reviewer**가 Spec 본문을 직접 쓰거나 고치지 않습니다.
- **traceability-verifier**가 Spec/Policy를 직접 쓰거나 고치지 않습니다.
- 수정이 필요하면 피드백을 writer에 전달하여 writer가 수정합니다.

## 5. 식별과 작성 분리

- **identifier**가 식별하고, **writer**가 작성합니다.
- 역할 교차 금지: identifier가 Spec을 작성하거나, writer가 새로운 UC를 식별하지 않습니다.
- 이 분리는 유형 오분류를 방지하기 위한 구조적 제약입니다.
