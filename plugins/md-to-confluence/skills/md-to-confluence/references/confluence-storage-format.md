# Confluence Storage Format Reference

This document covers the XHTML-based storage format that Confluence uses internally.
Refer to this when debugging conversion issues or adding new element mappings.

## Table of Contents

1. [Basic Elements](#basic-elements)
2. [Code Macro](#code-macro)
3. [Panel Macros](#panel-macros)
4. [Image Tags](#image-tags)
5. [Table of Contents Macro](#table-of-contents-macro)
6. [Page Links](#page-links)
7. [Common Pitfalls](#common-pitfalls)

---

## Basic Elements

Standard HTML elements work in Confluence storage format:

| Markdown         | Confluence Storage Format              |
|------------------|----------------------------------------|
| `# H1`           | `<h1>H1</h1>`                         |
| `**bold**`        | `<strong>bold</strong>`                |
| `*italic*`        | `<em>italic</em>`                      |
| `~~strike~~`      | `<del>strike</del>` (via extension)    |
| `[text](url)`     | `<a href="url">text</a>`              |
| `` `inline` ``    | `<code>inline</code>`                 |
| `> blockquote`    | `<blockquote><p>text</p></blockquote>` |
| `---`             | `<hr/>`                                |

## Code Macro

Confluence uses a structured macro for code blocks, not `<pre><code>`:

```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:parameter ac:name="linenumbers">true</ac:parameter>
  <ac:parameter ac:name="title">example.py</ac:parameter>
  <ac:parameter ac:name="collapse">false</ac:parameter>
  <ac:plain-text-body><![CDATA[
def hello():
    print("world")
  ]]></ac:plain-text-body>
</ac:structured-macro>
```

Supported language values:
actionscript3, bash, c, c#, c++, css, coldfusion, delphi, diff, erlang,
groovy, html, java, javafx, javascript, json, perl, php, plain, powershell,
python, ruby, scala, sql, vb, xml, yaml

## Panel Macros

Info, note, warning, and tip panels:

```xml
<!-- Info panel (blue) -->
<ac:structured-macro ac:name="info">
  <ac:parameter ac:name="title">Optional Title</ac:parameter>
  <ac:rich-text-body><p>Content here</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Warning panel (orange) -->
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body><p>Content here</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Note panel (yellow) -->
<ac:structured-macro ac:name="note">
  <ac:rich-text-body><p>Content here</p></ac:rich-text-body>
</ac:structured-macro>

<!-- Tip panel (green) -->
<ac:structured-macro ac:name="tip">
  <ac:rich-text-body><p>Content here</p></ac:rich-text-body>
</ac:structured-macro>
```

## Image Tags

### Attachment image (uploaded to the same page)

```xml
<ac:image ac:alt="description" ac:width="800">
  <ri:attachment ri:filename="diagram-1.png" />
</ac:image>
```

### External URL image

```xml
<ac:image ac:alt="description">
  <ri:url ri:value="https://example.com/image.png" />
</ac:image>
```

### Image from another page

```xml
<ac:image>
  <ri:attachment ri:filename="shared-logo.png">
    <ri:page ri:content-title="Assets Page" ri:space-key="TEAM" />
  </ri:attachment>
</ac:image>
```

## Table of Contents Macro

```xml
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
</ac:structured-macro>
```

## Page Links

### Link to another Confluence page in the same space

```xml
<ac:link>
  <ri:page ri:content-title="Target Page Title" />
  <ac:plain-text-link-body><![CDATA[Display Text]]></ac:plain-text-link-body>
</ac:link>
```

### Link to a page in a different space

```xml
<ac:link>
  <ri:page ri:content-title="Target Page" ri:space-key="OTHER" />
  <ac:plain-text-link-body><![CDATA[Display Text]]></ac:plain-text-link-body>
</ac:link>
```

## Common Pitfalls

### 1. CDATA escaping in code blocks
The `<![CDATA[...]]>` wrapper in code blocks handles most escaping,
but `]]>` within code will break it. Replace with `]]]]><![CDATA[>` if encountered.

### 2. Empty paragraphs
Confluence rejects or renders blank `<p></p>` tags oddly.
Strip them in post-processing.

### 3. Nested lists
Confluence is strict about `<ul>/<ol>` nesting:
```xml
<!-- CORRECT -->
<ul>
  <li>Item 1
    <ul>
      <li>Sub-item</li>
    </ul>
  </li>
</ul>

<!-- WRONG — will break rendering -->
<ul>
  <li>Item 1</li>
  <ul><li>Sub-item</li></ul>
</ul>
```

### 4. Table headers
Confluence expects `<th>` in a `<thead>` section for proper styling:
```xml
<table>
  <thead>
    <tr><th>Column A</th><th>Column B</th></tr>
  </thead>
  <tbody>
    <tr><td>data</td><td>data</td></tr>
  </tbody>
</table>
```

### 5. HTML entities
Use XML-safe entities only. `&nbsp;` doesn't work — use `&#160;` instead.
Common safe entities: `&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#160;`
