#!/usr/bin/env python3
"""md2confluence.py — Markdown → Confluence Storage Format converter + uploader.

Zero external dependencies. Uses only Python 3.9+ stdlib.

Converts Markdown to Confluence Storage Format (XHTML) with support for:
- Headings, paragraphs, bold, italic, strikethrough, inline code, links
- Tables with thead/tbody
- Fenced code blocks → Confluence Code macro
- Mermaid code blocks → Macro Pack macro (server-side rendering)
- GFM callouts (> [!NOTE], > [!TIP], etc.) → Confluence panel macros
- Task lists (- [x], - [ ]) → checkbox characters
- Images (external URL / attachment)
- Ordered/unordered lists, blockquotes, horizontal rules

Upload/update via Confluence REST API v2 with auth from ~/.claude.json.

Usage:
    # Convert only (to stdout)
    python md2confluence.py input.md

    # Convert to file
    python md2confluence.py input.md -o output.html

    # Create new Confluence page
    python md2confluence.py input.md --create --space-id 12345 --parent-id 67890

    # Update existing Confluence page
    python md2confluence.py input.md --update --page-id 12345

    # With custom title and version message
    python md2confluence.py input.md --update --page-id 12345 --title "My Page" --version-msg "v2.0"
"""
import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request


# ---------------------------------------------------------------------------
# Markdown → Confluence Storage Format conversion
# ---------------------------------------------------------------------------

def escape(text):
    """HTML-escape text for safe embedding in XHTML."""
    return html.escape(text, quote=True)


def inline_format(text):
    """Convert inline Markdown formatting to HTML."""
    # Process code spans first (to protect their content)
    parts = []
    last = 0
    for m in re.finditer(r'`([^`]+)`', text):
        parts.append(_inline_no_code(text[last:m.start()]))
        parts.append(f'<code>{escape(m.group(1))}</code>')
        last = m.end()
    parts.append(_inline_no_code(text[last:]))
    return ''.join(parts)


def _inline_no_code(text):
    """Handle bold, italic, strikethrough, links outside code spans."""
    # Links [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: f'<a href="{escape(m.group(2))}">{escape(m.group(1))}</a>',
        text,
    )
    # Bold + italic ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Strikethrough ~~text~~
    text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
    return text


def convert_table(lines):
    """Convert Markdown table lines to Confluence storage format HTML."""
    if len(lines) < 2:
        return ''

    headers = [c.strip() for c in lines[0].strip('|').split('|')]
    rows = []
    for line in lines[2:]:  # skip separator line
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)

    out = ['<table><colgroup>']
    for _ in headers:
        out.append('<col />')
    out.append('</colgroup><thead><tr>')
    for h in headers:
        out.append(f'<th><p>{inline_format(h)}</p></th>')
    out.append('</tr></thead><tbody>')
    for row in rows:
        out.append('<tr>')
        for cell in row:
            out.append(f'<td><p>{inline_format(cell)}</p></td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


def convert_mermaid(code):
    """Convert Mermaid code to Macro Pack structured macro."""
    escaped_code = escape(code.strip())
    return (
        '<ac:structured-macro ac:name="macro-pack" ac:schema-version="1">'
        '<ac:parameter ac:name="input">mermaid</ac:parameter>'
        f'<ac:parameter ac:name="text">{escaped_code}</ac:parameter>'
        '<ac:parameter ac:name="source">'
        '{&quot;id&quot;:&quot;text&quot;,&quot;type&quot;:&quot;text&quot;}'
        '</ac:parameter>'
        '<ac:parameter ac:name="mermaid_height">600</ac:parameter>'
        '<ac:parameter ac:name="mermaid_enable_custom_height">false</ac:parameter>'
        '<ac:parameter ac:name="mermaid_custom_icons">false</ac:parameter>'
        '<ac:parameter ac:name="mermaid_links_new_tab">true</ac:parameter>'
        '<ac:parameter ac:name="body"></ac:parameter>'
        '</ac:structured-macro>'
    )


def convert_code_block(lang, code):
    """Convert fenced code block to Confluence Code macro."""
    lang_attr = (
        f'<ac:parameter ac:name="language">{escape(lang)}</ac:parameter>'
        if lang
        else ''
    )
    return (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        f'{lang_attr}'
        '<ac:parameter ac:name="linenumbers">true</ac:parameter>'
        f'<ac:plain-text-body><![CDATA[{code.rstrip()}]]></ac:plain-text-body>'
        '</ac:structured-macro>'
    )


def convert_image(alt, src):
    """Convert image reference to Confluence image tag."""
    if src.startswith('http://') or src.startswith('https://'):
        return (
            f'<ac:image ac:alt="{escape(alt)}">'
            f'<ri:url ri:value="{escape(src)}" />'
            '</ac:image>'
        )
    else:
        filename = os.path.basename(src)
        return (
            f'<ac:image ac:alt="{escape(alt)}">'
            f'<ri:attachment ri:filename="{escape(filename)}" />'
            '</ac:image>'
        )


def convert_callout(callout_type, content_lines):
    """Convert GFM callout to Confluence panel macro."""
    type_map = {
        'note': 'info',
        'tip': 'tip',
        'warning': 'warning',
        'caution': 'warning',
        'important': 'note',
    }
    macro_name = type_map.get(callout_type.lower(), 'info')
    content = inline_format(' '.join(content_lines))
    return (
        f'<ac:structured-macro ac:name="{macro_name}">'
        f'<ac:rich-text-body><p>{content}</p></ac:rich-text-body>'
        '</ac:structured-macro>'
    )


def parse_list_block(lines, start_idx):
    """Parse a list block starting at start_idx. Returns (html, end_idx)."""
    result = []
    i = start_idx
    first_line = lines[i]

    if re.match(r'^\d+\.\s', first_line.strip()):
        tag = 'ol'
        pattern = r'^\d+\.\s+(.*)'
    else:
        tag = 'ul'
        pattern = r'^[-*+]\s+(.*)'

    result.append(f'<{tag}>')
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for task list items
        task_match = re.match(r'^[-*+]\s+\[([ xX])\]\s+(.*)', stripped)
        if task_match and tag == 'ul':
            checked = task_match.group(1).lower() == 'x'
            checkbox = '\u2611' if checked else '\u2610'
            text = inline_format(task_match.group(2))
            result.append(f'<li>{checkbox} {text}</li>')
            i += 1
            continue

        m = re.match(pattern, stripped)
        if not m:
            break
        result.append(f'<li>{inline_format(m.group(1))}</li>')
        i += 1
    result.append(f'</{tag}>')
    return ''.join(result), i


def md_to_confluence(md_text):
    """Convert full Markdown text to Confluence storage format XHTML."""
    lines = md_text.split('\n')
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line — skip
        if not stripped:
            i += 1
            continue

        # HTML comment — skip (<!-- ... -->)
        if stripped.startswith('<!--'):
            while i < len(lines) and '-->' not in lines[i]:
                i += 1
            i += 1  # skip closing line
            continue

        # Fenced code block
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code = '\n'.join(code_lines)

            if lang == 'mermaid':
                output.append(convert_mermaid(code))
            else:
                output.append(convert_code_block(lang, code))
            continue

        # Heading
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            text = inline_format(m.group(2))
            output.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            output.append('<hr />')
            i += 1
            continue

        # Table (current line has |, next line is separator)
        if ('|' in stripped and i + 1 < len(lines)
                and re.match(r'^\|?[\s:]*[-|:]+[\s:]*\|?$', lines[i + 1].strip())):
            table_lines = []
            while i < len(lines) and '|' in lines[i].strip():
                table_lines.append(lines[i])
                i += 1
            output.append(convert_table(table_lines))
            continue

        # Image (standalone line)
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', stripped)
        if img_match:
            output.append(convert_image(img_match.group(1), img_match.group(2)))
            i += 1
            continue

        # Blockquote — check for GFM callout first
        if stripped.startswith('>'):
            # Check for GFM callout: > [!NOTE], > [!TIP], etc.
            callout_match = re.match(
                r'^>\s*\[!(NOTE|TIP|WARNING|CAUTION|IMPORTANT)\]\s*$',
                stripped,
                re.IGNORECASE,
            )
            if callout_match:
                callout_type = callout_match.group(1)
                i += 1
                content_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    content_lines.append(
                        re.sub(r'^>\s?', '', lines[i].strip())
                    )
                    i += 1
                output.append(convert_callout(callout_type, content_lines))
            else:
                # Regular blockquote
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    quote_lines.append(
                        re.sub(r'^>\s?', '', lines[i].strip())
                    )
                    i += 1
                content = inline_format(' '.join(quote_lines))
                output.append(f'<blockquote><p>{content}</p></blockquote>')
            continue

        # Unordered list (including task lists)
        if re.match(r'^[-*+]\s', stripped):
            html_block, i = parse_list_block(lines, i)
            output.append(html_block)
            continue

        # Ordered list
        if re.match(r'^\d+\.\s', stripped):
            html_block, i = parse_list_block(lines, i)
            output.append(html_block)
            continue

        # Regular paragraph — collect contiguous non-special lines
        para_lines = []
        while (i < len(lines) and lines[i].strip()
               and not lines[i].strip().startswith('#')
               and not lines[i].strip().startswith('```')
               and not lines[i].strip().startswith('>')
               and not lines[i].strip().startswith('<!--')
               and not re.match(r'^[-*_]{3,}\s*$', lines[i].strip())
               and not re.match(r'^[-*+]\s', lines[i].strip())
               and not re.match(r'^\d+\.\s', lines[i].strip())
               and not re.match(r'^!\[', lines[i].strip())
               and not ('|' in lines[i].strip() and i + 1 < len(lines)
                        and re.match(r'^\|?[\s:]*[-|:]+',
                                     lines[min(i + 1, len(lines) - 1)].strip()))):
            para_lines.append(lines[i].strip())
            i += 1
        if para_lines:
            text = inline_format(' '.join(para_lines))
            output.append(f'<p>{text}</p>')
        continue

    return '\n'.join(output)


def extract_title(md_text):
    """Extract page title from the first H1 heading."""
    m = re.search(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return 'Untitled'


# ---------------------------------------------------------------------------
# Confluence REST API (auth from ~/.claude.json)
# ---------------------------------------------------------------------------

def get_credentials():
    """Read Confluence credentials from ~/.claude.json MCP server config."""
    claude_json = os.path.expanduser('~/.claude.json')
    if not os.path.isfile(claude_json):
        print('ERROR: ~/.claude.json not found.', file=sys.stderr)
        print('  Configure Confluence MCP server in Claude Code settings.',
              file=sys.stderr)
        sys.exit(1)

    with open(claude_json, 'r', encoding='utf-8') as f:
        config = json.load(f)

    try:
        env = config['mcpServers']['confluence']['env']
        return {
            'site': env['ATLASSIAN_SITE_NAME'],
            'email': env['ATLASSIAN_USER_EMAIL'],
            'token': env['ATLASSIAN_API_TOKEN'],
        }
    except KeyError as e:
        print(f'ERROR: Missing key in ~/.claude.json: {e}', file=sys.stderr)
        print('  Expected: mcpServers.confluence.env.ATLASSIAN_SITE_NAME',
              file=sys.stderr)
        print('            mcpServers.confluence.env.ATLASSIAN_USER_EMAIL',
              file=sys.stderr)
        print('            mcpServers.confluence.env.ATLASSIAN_API_TOKEN',
              file=sys.stderr)
        sys.exit(1)


def _make_auth_header(creds):
    """Create Basic auth header value."""
    auth_str = f"{creds['email']}:{creds['token']}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    return f'Basic {auth_b64}'


def _api_request(url, method='GET', data=None, creds=None):
    """Make an authenticated Confluence API request."""
    headers = {
        'Authorization': _make_auth_header(creds),
        'Accept': 'application/json',
    }
    if data is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        body = json.dumps(data).encode('utf-8')
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        print(f'ERROR {e.code}: {error_body[:500]}', file=sys.stderr)
        sys.exit(1)


def get_page_info(creds, page_id):
    """Get current page version, title, and spaceId."""
    url = f"https://{creds['site']}.atlassian.net/wiki/api/v2/pages/{page_id}"
    result = _api_request(url, creds=creds)
    return {
        'version': result['version']['number'],
        'title': result['title'],
        'spaceId': result['spaceId'],
    }


def create_page(creds, space_id, title, html_content, parent_id=None):
    """Create a new Confluence page."""
    url = f"https://{creds['site']}.atlassian.net/wiki/api/v2/pages"
    payload = {
        'spaceId': space_id,
        'status': 'current',
        'title': title,
        'body': {
            'representation': 'storage',
            'value': html_content,
        },
    }
    if parent_id:
        payload['parentId'] = parent_id

    result = _api_request(url, method='POST', data=payload, creds=creds)
    page_id = result['id']
    page_url = f"https://{creds['site']}.atlassian.net/wiki/pages/{page_id}"
    print(f"SUCCESS: Created '{title}' (id={page_id})")
    print(f"URL: {page_url}")
    return result


def update_page(creds, page_id, html_content, title=None, version_msg='Updated from Markdown'):
    """Update an existing Confluence page with version management."""
    info = get_page_info(creds, page_id)
    new_version = info['version'] + 1
    page_title = title or info['title']

    url = f"https://{creds['site']}.atlassian.net/wiki/api/v2/pages/{page_id}"
    payload = {
        'id': page_id,
        'status': 'current',
        'title': page_title,
        'spaceId': info['spaceId'],
        'body': {
            'representation': 'storage',
            'value': html_content,
        },
        'version': {
            'number': new_version,
            'message': version_msg,
        },
    }

    result = _api_request(url, method='PUT', data=payload, creds=creds)
    page_url = f"https://{creds['site']}.atlassian.net/wiki/pages/{page_id}"
    print(f"SUCCESS: Updated '{page_title}' to version {new_version}")
    print(f"URL: {page_url}")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Markdown → Confluence Storage Format converter + uploader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md                              # convert to stdout
  %(prog)s input.md -o output.html               # convert to file
  %(prog)s input.md --create --space-id 12345 --parent-id 67890
  %(prog)s input.md --update --page-id 12345
  %(prog)s input.md --update --page-id 12345 --title "My Title" --version-msg "v2"
        """,
    )
    parser.add_argument('input', help='Markdown file to convert')
    parser.add_argument('-o', '--output', help='Output HTML file (default: stdout)')
    parser.add_argument('--create', action='store_true',
                        help='Create a new Confluence page')
    parser.add_argument('--update', action='store_true',
                        help='Update an existing Confluence page')
    parser.add_argument('--page-id', help='Page ID for update')
    parser.add_argument('--space-id', help='Space ID for create')
    parser.add_argument('--parent-id', help='Parent page ID for create')
    parser.add_argument('--title', help='Page title (default: first H1 heading)')
    parser.add_argument('--version-msg', default='Updated from Markdown',
                        help='Version message for update')

    args = parser.parse_args()

    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert
    html_content = md_to_confluence(md_text)
    title = args.title or extract_title(md_text)

    if args.create:
        if not args.space_id:
            print('ERROR: --space-id required for --create', file=sys.stderr)
            sys.exit(1)
        creds = get_credentials()
        create_page(creds, args.space_id, title, html_content, args.parent_id)

    elif args.update:
        if not args.page_id:
            print('ERROR: --page-id required for --update', file=sys.stderr)
            sys.exit(1)
        creds = get_credentials()
        update_page(creds, args.page_id, html_content, args.title, args.version_msg)

    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'Output: {args.output} ({len(html_content)} chars)')

    else:
        # Write to stdout (handle encoding on Windows)
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(html_content.encode('utf-8'))
            sys.stdout.buffer.write(b'\n')
        else:
            print(html_content)


if __name__ == '__main__':
    main()
