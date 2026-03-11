# Claude Plugins

개인용 Claude Code 플러그인 마켓플레이스.

## 설치

### 1. 마켓플레이스 등록

```bash
/plugin marketplace add kitekjk/claude-plugins
```

### 2. 플러그인 설치

```bash
/plugin install md-to-confluence@claude-plugins
```

### 3. 사용

Claude Code에서 자연어로 요청하면 스킬이 자동 트리거됩니다:

```
이 HLD.md를 https://mycompany.atlassian.net/wiki/spaces/ARCH/pages/12345 하위에 올려줘
```

## 플러그인 목록

| 플러그인 | 설명 |
|---------|------|
| [md-to-confluence](./plugins/md-to-confluence) | Markdown 설계문서를 Confluence wiki에 발행 (Mermaid→이미지 포함) |

## 구조

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json              # 마켓플레이스 매니페스트
├── plugins/
│   └── md-to-confluence/
│       ├── .claude-plugin/
│       │   └── plugin.json           # 플러그인 매니페스트
│       ├── skills/
│       │   └── md-to-confluence/
│       │       ├── SKILL.md          # 스킬 정의
│       │       ├── scripts/
│       │       │   └── md2confluence.py
│       │       └── references/
│       │           └── confluence-storage-format.md
│       └── README.md
├── LICENSE
└── README.md
```

## 플러그인 추가하기

이 마켓플레이스에 새 플러그인을 추가하려면:

1. `plugins/` 하위에 플러그인 디렉토리 생성
2. `.claude-plugin/plugin.json` 매니페스트 작성
3. `skills/` 디렉토리에 스킬 추가
4. 루트 `.claude-plugin/marketplace.json`의 `plugins` 배열에 등록

## 라이선스

Apache-2.0
