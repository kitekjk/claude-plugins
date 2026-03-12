---
name: md-to-confluence
description: >
  Markdown 설계문서(HLD, LLD, 아키텍처 문서)를 Confluence wiki에 발행하는 스킬.
  사용자가 MD 파일을 Confluence에 올려달라고 하거나, 수정된 MD를 wiki에 반영해달라고
  요청할 때 트리거한다. "wiki에 올려줘", "Confluence에 발행해줘", "wiki 반영해줘",
  "이 문서 Confluence에 공유해줘", "MD를 wiki로 변환해줘" 등의 표현에 반응한다.
  Mermaid 다이어그램이 포함된 문서도 Macro Pack 매크로로 변환하여 처리한다.
allowed-tools: Read, Write, Edit, Bash
---

# Markdown → Confluence Publisher

핵심 원칙: **원본은 항상 Markdown이다.** Confluence는 공유 뷰일 뿐이다.

## 사전 요구사항

- Python 3.9+ (외부 패키지 불필요)
- Confluence에 Macro Pack 앱 설치 (Mermaid 렌더링용)
- `~/.claude.json`에 Confluence MCP 서버 설정 (auth 자동 읽기)

## 사용자 요청 패턴

### 패턴 1: 새 페이지 생성
> "이 MD를 Confluence에 올려줘" / "wiki에 발행해줘"

필요한 정보: MD 파일 경로, 대상 Confluence URL (부모 페이지)

### 패턴 2: 기존 페이지 업데이트
> "이 MD 수정했어, wiki에 반영해줘"

필요한 정보: 수정된 MD 파일, 대상 Confluence 페이지 URL 또는 page ID

### 패턴 3: 변환만 요청
> "이 MD를 Confluence 형식으로 변환해줘"

필요한 정보: MD 파일만

---

## 처리 워크플로우

### Step 1: MD 파일 읽기
- 파일 경로를 확인하고 Read 도구로 MD 파일을 읽는다

### Step 2: URL 파싱 (업로드 시)
사용자가 제공한 Confluence URL에서 도메인, Space key, Page ID를 추출한다:

| URL 패턴 | 추출 |
|----------|------|
| `https://{domain}.atlassian.net/wiki/spaces/{SPACE}/pages/{PAGE_ID}/...` | domain, space key, page ID |
| `https://{domain}.atlassian.net/wiki/spaces/{SPACE}/overview` | domain, space key (space 최상위) |

### Step 3: 변환 + 업로드

`scripts/md2confluence.py` 스크립트를 사용한다. 인증은 `~/.claude.json`에서 자동으로 읽는다.

#### 변환만:
```bash
python scripts/md2confluence.py input.md -o output.html
```

#### 새 페이지 생성:
```bash
python scripts/md2confluence.py input.md --create --space-id {SPACE_ID} --parent-id {PARENT_PAGE_ID}
```

#### 기존 페이지 업데이트:
```bash
python scripts/md2confluence.py input.md --update --page-id {PAGE_ID}
```

#### 옵션:
- `--title "Custom Title"` — 페이지 제목 (기본: MD의 첫 H1 헤딩)
- `--version-msg "업데이트 메시지"` — 버전 메시지 (기본: "Updated from Markdown")

### Step 4: 결과 안내
스크립트가 출력하는 URL을 사용자에게 안내한다.

---

## 변환 지원 요소

| Markdown | Confluence |
|----------|-----------|
| `# H1` ~ `###### H6` | `<h1>` ~ `<h6>` |
| `**bold**`, `*italic*` | `<strong>`, `<em>` |
| `` `code` `` | `<code>` |
| `~~strike~~` | `<del>` |
| `[text](url)` | `<a href>` |
| Tables | `<table>` with `<thead>/<tbody>` |
| Code blocks | `<ac:structured-macro ac:name="code">` |
| Mermaid blocks | `<ac:structured-macro ac:name="macro-pack">` (Macro Pack) |
| `> [!NOTE]` 등 GFM callout | `<ac:structured-macro ac:name="info/warning/tip/note">` |
| `- [x]` task lists | ☑/☐ 체크박스 |
| `![alt](url)` Images | `<ac:image>` (attachment/external) |
| `> blockquote` | `<blockquote>` |
| `- item` / `1. item` Lists | `<ul>/<ol>` |
| `---` Horizontal rule | `<hr />` |

## 인증

스크립트가 `~/.claude.json`에서 Confluence 인증 정보를 자동으로 읽는다:
- `mcpServers.confluence.env.ATLASSIAN_SITE_NAME`
- `mcpServers.confluence.env.ATLASSIAN_USER_EMAIL`
- `mcpServers.confluence.env.ATLASSIAN_API_TOKEN`

수동 설정 불필요.

## 주의사항

- 대용량 문서(100KB+)는 MCP 도구 대신 이 스크립트를 사용한다
- Mermaid 렌더링에 mmdc CLI 불필요 (Macro Pack이 서버에서 렌더링)
- Storage Format은 ADF보다 3-5배 작아 대용량 문서에 적합하다
