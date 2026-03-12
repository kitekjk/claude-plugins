---
name: spec-from-design
description: HLD/LLD 설계 문서에서 코드 생성 가능한 Spec을 생성합니다. 기존 프로젝트와 신규 프로젝트 모두 지원합니다.
allowed-tools: Read, Write, Edit, Grep, Glob, Task, Bash
---

# spec-from-design

HLD/LLD 설계 문서 → Spec 문서 생성. `spec-orchestrator` 에이전트에 위임하여 실행합니다.

## 실행 방법

`spec-from-design:spec-orchestrator` 에이전트를 Task 도구로 호출하세요. 오케스트레이터가 contract.json을 읽고 전체 워크플로우를 자동 수행합니다.

## 오케스트레이터에게 전달할 정보

- LLD/HLD 파일 경로
- 프로젝트 루트 경로
- 사용자 요청 내용 (도메인, Spec 유형 등)

## 서브에이전트 구조

spec-orchestrator → design-analyzer → policy-extractor → usecase-api-writer → spec-reviewer

상세 규칙은 `contract.json`과 각 에이전트 정의에 있으며, 오케스트레이터가 직접 읽습니다.
