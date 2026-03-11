---
name: md-to-confluence
description: >
  Markdown 설계문서(HLD, LLD, 아키텍처 문서)를 Confluence wiki에 발행하는 스킬.
  사용자가 MD 파일을 Confluence에 올려달라고 하거나, 수정된 MD를 wiki에 반영해달라고
  요청할 때 트리거한다. "wiki에 올려줘", "Confluence에 발행해줘", "wiki 반영해줘",
  "이 문서 Confluence에 공유해줘", "MD를 wiki로 변환해줘" 등의 표현에 반응한다.
  Mermaid 다이어그램이 포함된 문서도 Macro Pack 매크로로 변환하여 처리한다.
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

### Step 4: MD → ADF 변환

Markdown을 Atlassian Document Format(ADF) JSON으로 변환한다.
ADF는 Confluence의 네이티브 문서 포맷이며, Mermaid 다이어그램을 Macro Pack 매크로로 직접 렌더링할 수 있다.

변환 결과는 아래 구조의 JSON 문자열이다:

```json
{
  "version": 1,
  "type": "doc",
  "content": [ /* ADF 노드 배열 */ ]
}
```

### Step 5: 업로드 (MCP)

`contentFormat: "adf"`로 ADF JSON을 업로드한다.

#### 새 페이지 생성

```
mcp__plugin_atlassian_atlassian__createConfluencePage(
  cloudId: "{domain}.atlassian.net",
  spaceId: "{space_id}",
  title: "{문서 제목}",
  parentId: "{parent_page_id}",
  body: "{ADF JSON 문자열}",
  contentFormat: "adf"
)
```

#### 기존 페이지 업데이트

```
mcp__plugin_atlassian_atlassian__updateConfluencePage(
  cloudId: "{domain}.atlassian.net",
  pageId: "{page_id}",
  title: "{문서 제목}",
  body: "{ADF JSON 문자열}",
  contentFormat: "adf",
  versionMessage: "Updated from Markdown"
)
```

### Step 6: 결과 안내

업로드 결과에서 page ID를 확인하고 사용자에게 페이지 URL을 안내한다:
`https://{domain}.atlassian.net/wiki/pages/{page_id}`

---

## MD → ADF 변환 규칙

### 기본 노드 타입

#### Heading

```json
{"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "제목"}]}
```

`# H1` → level 1, `## H2` → level 2, ... `###### H6` → level 6

#### Paragraph

```json
{"type": "paragraph", "content": [{"type": "text", "text": "본문 텍스트"}]}
```

#### 줄바꿈 (한 paragraph 내)

```json
{"type": "hardBreak"}
```

### 인라인 서식 (marks)

텍스트 노드에 `marks` 배열로 적용한다:

| Markdown | mark |
|----------|------|
| `**bold**` | `{"type": "strong"}` |
| `*italic*` | `{"type": "em"}` |
| `~~strike~~` | `{"type": "strike"}` |
| `` `code` `` | `{"type": "code"}` |
| `[text](url)` | `{"type": "link", "attrs": {"href": "url"}}` |

예시: `**bold** and *italic*` →
```json
{"type": "paragraph", "content": [
  {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
  {"type": "text", "text": " and "},
  {"type": "text", "text": "italic", "marks": [{"type": "em"}]}
]}
```

### 리스트

#### Bullet List (`- item`)

```json
{"type": "bulletList", "content": [
  {"type": "listItem", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "항목"}]}
  ]}
]}
```

#### Ordered List (`1. item`)

```json
{"type": "orderedList", "attrs": {"order": 1}, "content": [
  {"type": "listItem", "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "항목"}]}
  ]}
]}
```

#### Task List (`- [x] item`)

```json
{"type": "taskList", "content": [
  {"type": "taskItem", "attrs": {"state": "DONE"}, "content": [
    {"type": "text", "text": "완료된 항목"}
  ]},
  {"type": "taskItem", "attrs": {"state": "TODO"}, "content": [
    {"type": "text", "text": "미완료 항목"}
  ]}
]}
```

### Code Block

````markdown
```kotlin
fun main() {}
```
````

```json
{"type": "codeBlock", "attrs": {"language": "kotlin"}, "content": [
  {"type": "text", "text": "fun main() {}"}
]}
```

### Blockquote

```json
{"type": "blockquote", "content": [
  {"type": "paragraph", "content": [{"type": "text", "text": "인용문"}]}
]}
```

### 수평선 (`---`)

```json
{"type": "rule"}
```

### Table

```json
{"type": "table", "attrs": {"layout": "align-start"}, "content": [
  {"type": "tableRow", "content": [
    {"type": "tableHeader", "content": [
      {"type": "paragraph", "content": [{"type": "text", "text": "헤더1"}]}
    ]},
    {"type": "tableHeader", "content": [
      {"type": "paragraph", "content": [{"type": "text", "text": "헤더2"}]}
    ]}
  ]},
  {"type": "tableRow", "content": [
    {"type": "tableCell", "content": [
      {"type": "paragraph", "content": [{"type": "text", "text": "값1"}]}
    ]},
    {"type": "tableCell", "content": [
      {"type": "paragraph", "content": [{"type": "text", "text": "값2"}]}
    ]}
  ]}
]}
```

### Mermaid → Macro Pack 매크로

````markdown
```mermaid
flowchart TD
    A --> B
```
````

Mermaid 코드블록은 Confluence의 Macro Pack `extension` 노드로 변환한다.
**codeBlock이 아닌 extension 타입을 사용해야 한다.**

```json
{
  "type": "extension",
  "attrs": {
    "layout": "default",
    "extensionType": "com.atlassian.confluence.macro.core",
    "extensionKey": "macro-pack",
    "parameters": {
      "macroParams": {
        "input": {"value": "mermaid"},
        "mermaid_height": {"value": "600"},
        "mermaid_enable_custom_height": {"value": "false"},
        "mermaid_custom_icons": {"value": "false"},
        "source": {"value": "{\"id\":\"text\",\"type\":\"text\"}"},
        "text": {"value": "flowchart TD\n    A --> B"},
        "body": {"value": ""},
        "mermaid_links_new_tab": {"value": "true"}
      },
      "macroMetadata": {
        "schemaVersion": {"value": "1"},
        "title": "Macro Pack"
      }
    }
  }
}
```

**핵심 필드:**
- `text.value` — Mermaid 코드 원문 (줄바꿈은 `\n`으로)
- `input.value` — 항상 `"mermaid"`
- `source.value` — 항상 `"{\"id\":\"text\",\"type\":\"text\"}"`

---

## 사전 요구사항

Atlassian MCP 연결만 되어 있으면 추가 설정 불필요.
- 환경변수, API 토큰 설정 없음
- pip/npm 패키지 설치 없음
- Mermaid 렌더링을 위해 Confluence에 **Macro Pack** 앱이 설치되어 있어야 함
