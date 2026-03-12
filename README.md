# Kay's Plugins

개인용 Claude Code 플러그인 마켓플레이스.

## 설치

### 1. 마켓플레이스 등록

```bash
/plugin marketplace add kitekjk/kitekjk-plugins
```

### 2. 플러그인 설치

```bash
/plugin install doc-writing-team@kitekjk-plugins
/plugin install spec-from-design@kitekjk-plugins
/plugin install md-to-confluence@kitekjk-plugins
```

### 3. 사용

Claude Code에서 자연어로 요청하면 스킬이 자동 트리거됩니다:

```
# 설계 문서 작성
주문 도메인 HLD를 작성해줘

# HLD/LLD → Spec 도출
이 HLD와 LLD를 기반으로 Use Case Spec을 생성해줘

# Confluence 발행
이 HLD.md를 Confluence에 올려줘
```

## 플러그인 목록

| 플러그인 | 버전 | 설명 |
|---------|------|------|
| [doc-writing-team](./plugins/doc-writing-team) | v3.0.0 | ADR/HLD/LLD 설계 문서 작성 — 멀티 에이전트 품질 루프, Spec 도출 가능 수준 보장 |
| [spec-from-design](./plugins/spec-from-design) | v1.0.0 | HLD/LLD → Use Case·API·Policy·Test Spec 도출 — 3 scales, 프리셋 시스템 |
| [md-to-confluence](./plugins/md-to-confluence) | v0.1.0 | Markdown 설계문서를 Confluence wiki에 발행 (Mermaid→이미지 포함) |

### 워크플로우 연계

```
개발 요청
  ↓
doc-writing-team  →  HLD / LLD 작성
  ↓
spec-from-design  →  Use Case / API / Policy / Test Spec 도출
  ↓
md-to-confluence  →  Confluence wiki 발행
```

## 구조

```
kitekjk-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── doc-writing-team/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                    # 7 agents (orchestrator, writers, reviewer, style)
│   │   └── skills/doc-writing-team/
│   │       ├── contract.json          # 단일 기준
│   │       ├── specs/                 # ADR, HLD, LLD 스펙
│   │       ├── templates/             # 문서 템플릿
│   │       ├── checklists/            # 품질 체크리스트 (88점 게이트)
│   │       └── memory/               # 페르소나, 스타일 가이드
│   ├── spec-from-design/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/                    # 6 agents (orchestrator, analyzer, writers, reviewer)
│   │   └── skills/spec-from-design/
│   │       ├── contract.json          # 단일 기준
│   │       ├── specs/                 # Use Case, API, Policy 스펙
│   │       ├── templates/             # Spec + 아키텍처 템플릿
│   │       ├── checklists/            # 품질 체크리스트 (80점 게이트)
│   │       ├── mappings/              # HLD→Spec, LLD→Spec 변환 규칙
│   │       └── presets/               # DDD+Clean+Kotlin (확장 가능)
│   └── md-to-confluence/
│       ├── .claude-plugin/plugin.json
│       ├── skills/md-to-confluence/
│       └── README.md
├── LICENSE
└── README.md
```

## 플러그인 추가하기

1. `plugins/` 하위에 플러그인 디렉토리 생성
2. `.claude-plugin/plugin.json` 매니페스트 작성
3. `skills/` 디렉토리에 스킬 추가
4. 루트 `.claude-plugin/marketplace.json`의 `plugins` 배열에 등록

## 라이선스

Apache-2.0
