---
name: md-to-confluence
description: >
  Markdown 설계문서(HLD, LLD, 아키텍처 문서)를 Confluence wiki에 발행하는 스킬.
  사용자가 MD 파일을 Confluence에 올려달라고 하거나, 수정된 MD를 wiki에 반영해달라고
  요청할 때 트리거한다. "wiki에 올려줘", "Confluence에 발행해줘", "wiki 반영해줘",
  "이 문서 Confluence에 공유해줘", "MD를 wiki로 변환해줘" 등의 표현에 반응한다.
  Mermaid 다이어그램이 포함된 문서도 이미지 변환을 포함하여 처리한다.
---

# Markdown → Confluence Publisher

사용자가 Markdown 파일을 Confluence wiki에 올리거나 업데이트하라고 요청할 때,
이 스킬의 절차를 따른다.

## 핵심 원칙

**원본은 항상 Markdown이다.** Confluence는 사람들이 보는 공유 뷰일 뿐이다.
수정이 필요하면 Markdown을 고치고 다시 발행한다.

## 사용자 요청 패턴

### 패턴 1: 새 페이지 생성
> "이 MD 파일을 https://xxx.atlassian.net/wiki/.../pages/12345 하위에 올려줘"

필요한 정보:
- MD 파일 (업로드된 파일 또는 경로)
- 대상 Confluence wiki URL (부모 페이지)

### 패턴 2: 기존 페이지 업데이트
> "이 MD 수정했어, wiki에 반영해줘"

필요한 정보:
- 수정된 MD 파일
- 대상 Confluence 페이지 URL (이전에 공유했거나 알려준 URL)

### 패턴 3: 변환만 요청
> "이 MD를 Confluence 형식으로 변환해줘"

필요한 정보:
- MD 파일만

---

## 처리 워크플로우

### Step 1: MD 파일 읽기

- MD 파일을 읽는다
- 첫 번째 `# H1` 헤딩에서 페이지 제목을 추출한다

### Step 2: URL 파싱

사용자가 제공하는 Confluence URL에서 필요한 값을 추출한다:

| URL 패턴 | 추출 |
|----------|------|
| `https://{domain}.atlassian.net/wiki/spaces/{SPACE}/pages/{PAGE_ID}/...` | domain, space key, page ID |
| `https://{domain}.atlassian.net/wiki/spaces/{SPACE}/overview` | domain, space key (space 최상위) |
| `https://{domain}.atlassian.net/wiki/x/{SHORT_LINK}` | domain (short link — page ID를 사용자에게 확인) |

### Step 3: Confluence 정보 조회

MCP 도구로 업로드에 필요한 ID를 확인한다:

- **cloudId**: URL의 도메인 (`{domain}.atlassian.net`)을 그대로 사용
- **spaceId**: space key로 space ID를 조회한다:
  ```
  mcp__plugin_atlassian_atlassian__getConfluenceSpaces(cloudId="{domain}.atlassian.net")
  ```
  결과에서 해당 space key에 매칭되는 spaceId를 추출

### Step 4: 업로드 (MCP)

Atlassian MCP 도구를 사용하여 Markdown 원문을 직접 업로드한다.
별도 변환 없이 `contentFormat: "markdown"`으로 전달하면 Confluence가 렌더링한다.

#### 새 페이지 생성

```
mcp__plugin_atlassian_atlassian__createConfluencePage(
  cloudId: "{domain}.atlassian.net",
  spaceId: "{space_id}",
  title: "{문서 제목}",
  parentId: "{parent_page_id}",   // URL에서 추출한 부모 페이지 ID
  body: "{MD 파일 원문 전체}",
  contentFormat: "markdown"
)
```

#### 기존 페이지 업데이트

```
mcp__plugin_atlassian_atlassian__updateConfluencePage(
  cloudId: "{domain}.atlassian.net",
  pageId: "{page_id}",
  title: "{문서 제목}",
  body: "{MD 파일 원문 전체}",
  contentFormat: "markdown",
  versionMessage: "Updated from Markdown"
)
```

### Step 5: 결과 안내

업로드 결과에서 page ID를 확인하고 사용자에게 페이지 URL을 안내한다:
`https://{domain}.atlassian.net/wiki/pages/{page_id}`

---

## 변환만 요청 시 (패턴 3)

변환만 요청한 경우 MCP 업로드 없이 로컬 변환만 수행한다:

### 의존성 설치

```bash
pip install markdown pymdown-extensions --break-system-packages -q
```

Mermaid 다이어그램이 있는 경우 추가로:
```bash
npm install -g @mermaid-js/mermaid-cli
npx puppeteer browsers install chrome
```

### 변환 스크립트 실행

스킬 번들의 `scripts/md2confluence.py`를 사용한다:

```bash
python <skill-path>/scripts/md2confluence.py <input.md> -o /home/claude/confluence-output/
```

이 스크립트가 수행하는 작업:
1. Mermaid 코드블록 추출 → PNG 이미지 렌더링 (`confluence-output/images/`)
2. Mermaid 블록을 이미지 참조로 교체
3. Markdown → Confluence Storage Format XHTML 변환
4. 결과를 `<stem>.confluence.html`로 저장

### 결과물

- `.confluence.html` — Confluence 페이지 본문 (storage format XHTML)
- `images/*.png` — Mermaid 다이어그램 이미지 파일들 (있는 경우)

---

## Mermaid 다이어그램 처리

MCP 업로드 시 Markdown 원문을 그대로 전달하므로, Mermaid 코드블록은 Confluence 측에서 처리된다.

- **Confluence Mermaid 앱이 설치된 경우**: 자동 렌더링됨
- **미설치 시**: 코드블록으로 표시됨. 사용자에게 안내한다:
  - "Mermaid 다이어그램이 코드블록으로 표시됩니다. Confluence의 Mermaid 앱 설치를 권장합니다."

이미지 렌더링이 반드시 필요한 경우, 로컬 변환(`md2confluence.py`)을 사용한다.

---

## 변환 상세 (참고)

Confluence Storage Format 태그 매핑 상세는 `references/confluence-storage-format.md`를 참조한다.
로컬 변환 스크립트(`md2confluence.py`)에서 사용하는 매핑이다.

### 주요 변환 매핑

| Markdown 요소 | Confluence 변환 결과 |
|--------------|---------------------|
| `# Heading` | `<h1>Heading</h1>` |
| ` ```kotlin ... ``` ` | `<ac:structured-macro ac:name="code">` (language=kotlin) |
| ` ```mermaid ... ``` ` | PNG 이미지 → `<ac:image><ri:attachment>` |
| `> [!NOTE]` | `<ac:structured-macro ac:name="info">` |
| `> [!WARNING]` | `<ac:structured-macro ac:name="warning">` |
| `[TOC]` | `<ac:structured-macro ac:name="toc"/>` |
| `- [x] task` | ☑ / ☐ 텍스트 |
| 테이블 | `<table>` with `<thead>/<tbody>` |
| `![alt](url)` | `<ac:image>` (외부 URL 또는 attachment) |

---

## 사전 요구사항

### MCP 업로드 (기본)

Atlassian MCP 연결만 되어 있으면 추가 설정 불필요.
환경변수, API 토큰 별도 설정 없음.

### 로컬 변환 (변환만 요청 시)

```bash
pip install markdown pymdown-extensions
```

Mermaid 렌더링이 필요한 경우 추가:
```bash
npm install -g @mermaid-js/mermaid-cli
```
