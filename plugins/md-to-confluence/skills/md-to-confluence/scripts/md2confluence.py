#!/usr/bin/env python3
"""
md2confluence.py — Markdown → Confluence Storage Format converter

Core principle: Markdown is the Single Source of Truth.
This script converts .md files to Confluence-compatible XHTML,
rendering Mermaid diagrams to PNG images along the way.

Usage:
    # Convert single file
    python md2confluence.py input.md -o output/

    # Convert directory of .md files
    python md2confluence.py specs/ -o output/

    # Convert and upload to Confluence
    python md2confluence.py specs/ --upload

Dependencies:
    pip install markdown pymdown-extensions --break-system-packages
    npm install -g @mermaid-js/mermaid-cli  # for Mermaid rendering
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.toc import TocExtension
except ImportError:
    print("ERROR: 'markdown' package required. Install with:")
    print("  pip install markdown pymdown-extensions --break-system-packages")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Mermaid Rendering
# ---------------------------------------------------------------------------

def find_mmdc() -> Optional[str]:
    """Locate the mmdc (mermaid-cli) binary."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        return mmdc
    # Common npm global paths
    for candidate in [
        os.path.expanduser("~/.npm-global/bin/mmdc"),
        "/usr/local/bin/mmdc",
        os.path.expanduser("~/node_modules/.bin/mmdc"),
    ]:
        if os.path.isfile(candidate):
            return candidate
    return None


def extract_mermaid_blocks(md_content: str) -> list[dict]:
    """Extract ```mermaid code blocks from Markdown content.

    Returns list of dicts with keys: start, end, code, block_id
    """
    pattern = re.compile(
        r"```mermaid\s*\n(.*?)```",
        re.DOTALL,
    )
    blocks = []
    for i, match in enumerate(pattern.finditer(md_content)):
        code = match.group(1).strip()
        block_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        blocks.append({
            "start": match.start(),
            "end": match.end(),
            "code": code,
            "block_id": f"diagram-{i + 1}-{block_hash}",
        })
    return blocks


def render_mermaid_block(
    code: str,
    output_path: Path,
    mmdc_path: str,
    width: int = 1200,
) -> bool:
    """Render a single Mermaid diagram to PNG."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mmd", delete=False
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                mmdc_path,
                "-i", tmp_path,
                "-o", str(output_path),
                "-b", "transparent",
                "-w", str(width),
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"  WARNING: mmdc failed: {result.stderr.strip()}")
            return False
        return output_path.exists()
    except subprocess.TimeoutExpired:
        print("  WARNING: mmdc timed out (30s)")
        return False
    except FileNotFoundError:
        print("  WARNING: mmdc not found")
        return False
    finally:
        os.unlink(tmp_path)


def process_mermaid_diagrams(
    md_content: str,
    images_dir: Path,
    mmdc_path: Optional[str] = None,
) -> tuple[str, list[str]]:
    """Replace Mermaid blocks with image references, render PNGs.

    Returns (modified_md_content, list_of_image_filenames)
    """
    blocks = extract_mermaid_blocks(md_content)
    if not blocks:
        return md_content, []

    if mmdc_path is None:
        mmdc_path = find_mmdc()

    if mmdc_path is None:
        print("WARNING: mmdc not found. Mermaid blocks will be kept as code blocks.")
        print("  Install with: npm install -g @mermaid-js/mermaid-cli")
        return md_content, []

    images_dir.mkdir(parents=True, exist_ok=True)
    image_files = []
    # Process in reverse order to preserve string positions
    for block in reversed(blocks):
        img_filename = f"{block['block_id']}.png"
        img_path = images_dir / img_filename

        print(f"  Rendering {block['block_id']}...")
        success = render_mermaid_block(block["code"], img_path, mmdc_path)

        if success:
            # Replace with image reference
            replacement = f"![{block['block_id']}](./images/{img_filename})"
            image_files.append(img_filename)
        else:
            # Fallback: keep as plain code block
            replacement = f"```\n{block['code']}\n```"

        md_content = (
            md_content[: block["start"]] + replacement + md_content[block["end"] :]
        )

    image_files.reverse()
    return md_content, image_files


# ---------------------------------------------------------------------------
# Markdown → Confluence Storage Format
# ---------------------------------------------------------------------------

# Language aliases for Confluence code macro
CONFLUENCE_LANG_MAP = {
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "javascript",
    "ts": "javascript",
    "java": "java",
    "kotlin": "kotlin",
    "kt": "kotlin",
    "bash": "bash",
    "sh": "bash",
    "shell": "bash",
    "zsh": "bash",
    "sql": "sql",
    "json": "json",
    "xml": "xml",
    "html": "html",
    "css": "css",
    "yaml": "yaml",
    "yml": "yaml",
    "groovy": "groovy",
    "ruby": "ruby",
    "go": "go",
    "rust": "rust",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "csharp": "csharp",
    "c#": "csharp",
    "scala": "scala",
    "swift": "swift",
    "r": "r",
    "perl": "perl",
    "php": "php",
    "powershell": "powershell",
    "dockerfile": "bash",
    "makefile": "bash",
    "terraform": "plain",
    "hcl": "plain",
    "toml": "plain",
    "ini": "plain",
    "properties": "plain",
    "markdown": "plain",
    "md": "plain",
    "text": "plain",
    "txt": "plain",
    "mermaid": "plain",
}


def code_block_to_confluence(match: re.Match) -> str:
    """Convert a fenced code block to Confluence Code macro."""
    lang = (match.group(1) or "").strip().lower()
    code = match.group(2)
    confluence_lang = CONFLUENCE_LANG_MAP.get(lang, "plain")

    # XML-escape the code content
    code = (
        code.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return (
        f'<ac:structured-macro ac:name="code">'
        f'<ac:parameter ac:name="language">{confluence_lang}</ac:parameter>'
        f'<ac:parameter ac:name="linenumbers">true</ac:parameter>'
        f'<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>'
        f'</ac:structured-macro>'
    )


def image_to_confluence(match: re.Match) -> str:
    """Convert Markdown image to Confluence image tag."""
    alt_text = match.group(1)
    src = match.group(2)

    if src.startswith("http://") or src.startswith("https://"):
        # External image
        return (
            f'<ac:image ac:alt="{alt_text}">'
            f'<ri:url ri:value="{src}" />'
            f'</ac:image>'
        )
    else:
        # Attachment image — use filename only
        filename = os.path.basename(src)
        return (
            f'<ac:image ac:alt="{alt_text}">'
            f'<ri:attachment ri:filename="{filename}" />'
            f'</ac:image>'
        )


def callout_to_confluence(match: re.Match) -> str:
    """Convert GitHub-style callout to Confluence panel macro.

    Supports: > [!NOTE], > [!TIP], > [!WARNING], > [!CAUTION], > [!IMPORTANT]
    """
    callout_type = match.group(1).lower()
    content = match.group(2).strip()
    # Remove leading '> ' from each line
    content = re.sub(r"^>\s?", "", content, flags=re.MULTILINE)

    type_map = {
        "note": "info",
        "tip": "tip",
        "warning": "warning",
        "caution": "warning",
        "important": "note",
    }
    macro_name = type_map.get(callout_type, "info")

    return (
        f'<ac:structured-macro ac:name="{macro_name}">'
        f'<ac:rich-text-body><p>{content}</p></ac:rich-text-body>'
        f'</ac:structured-macro>'
    )


def task_list_to_html(match: re.Match) -> str:
    """Convert GFM task list item to HTML checkbox."""
    checked = match.group(1) == "x"
    text = match.group(2)
    checkbox = "☑" if checked else "☐"
    return f"<li>{checkbox} {text}</li>"


def md_to_confluence_storage(md_content: str) -> str:
    """Convert Markdown to Confluence storage format XHTML.

    This is a two-pass process:
    1. Pre-process: handle elements that need special Confluence macros
    2. Convert remaining Markdown to HTML via python-markdown
    """
    content = md_content

    # --- Pre-pass: Extract code blocks to protect them ---
    code_blocks = {}
    code_counter = [0]

    def stash_code_block(match):
        placeholder = f"%%CODE_BLOCK_{code_counter[0]}%%"
        code_blocks[placeholder] = code_block_to_confluence(match)
        code_counter[0] += 1
        return placeholder

    content = re.sub(
        r"```(\w*)\s*\n(.*?)```",
        stash_code_block,
        content,
        flags=re.DOTALL,
    )

    # --- Pre-pass: Handle GFM callouts ---
    content = re.sub(
        r"^>\s*\[!(NOTE|TIP|WARNING|CAUTION|IMPORTANT)\]\s*\n((?:>.*\n?)*)",
        callout_to_confluence,
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # --- Pre-pass: Handle images ---
    content = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        image_to_confluence,
        content,
    )

    # --- Pre-pass: Handle task lists ---
    content = re.sub(
        r"^-\s+\[([ x])\]\s+(.*)",
        task_list_to_html,
        content,
        flags=re.MULTILINE,
    )

    # --- Pre-pass: Replace TOC markers ---
    content = re.sub(
        r"^\[TOC\]\s*$",
        '<ac:structured-macro ac:name="toc"/>',
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # --- Main conversion: Markdown → HTML ---
    md_converter = markdown.Markdown(
        extensions=[
            "tables",
            "sane_lists",
            "smarty",
        ],
        output_format="html5",
    )
    html_content = md_converter.convert(content)

    # --- Post-pass: Restore code blocks ---
    for placeholder, replacement in code_blocks.items():
        html_content = html_content.replace(
            f"<p>{placeholder}</p>", replacement
        )
        html_content = html_content.replace(placeholder, replacement)

    # --- Post-pass: Clean up ---
    # Remove empty paragraphs
    html_content = re.sub(r"<p>\s*</p>", "", html_content)

    return html_content


# ---------------------------------------------------------------------------
# Title Extraction
# ---------------------------------------------------------------------------

def extract_title(md_content: str) -> str:
    """Extract page title from the first H1 heading."""
    match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


# ---------------------------------------------------------------------------
# Confluence API Upload
# ---------------------------------------------------------------------------

def upload_to_confluence(
    title: str,
    body_html: str,
    image_files: list[Path],
    domain: str,
    space_id: str,
    api_token: str,
    email: str,
    parent_id: Optional[str] = None,
    page_id: Optional[str] = None,
) -> dict:
    """Create or update a Confluence page with attachments.

    Uses Confluence REST API v2 for page operations.
    Uses REST API v1 for attachments (v2 doesn't support file upload).
    """
    try:
        import requests
    except ImportError:
        print("ERROR: 'requests' package required for upload.")
        print("  pip install requests --break-system-packages")
        sys.exit(1)

    base_url = f"https://{domain}.atlassian.net/wiki"
    auth = (email, api_token)

    headers_json = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if page_id:
        # --- Update existing page ---
        # First, get current version number
        resp = requests.get(
            f"{base_url}/api/v2/pages/{page_id}",
            auth=auth,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        current_version = resp.json()["version"]["number"]

        payload = {
            "id": page_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": body_html,
            },
            "version": {
                "number": current_version + 1,
                "message": "Updated from Markdown (md2confluence)",
            },
        }
        resp = requests.put(
            f"{base_url}/api/v2/pages/{page_id}",
            auth=auth,
            headers=headers_json,
            json=payload,
        )
        resp.raise_for_status()
        page_data = resp.json()
        print(f"  Updated page: {title} (id={page_id}, v{current_version + 1})")

    else:
        # --- Create new page ---
        payload = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": body_html,
            },
        }
        if parent_id:
            payload["parentId"] = parent_id

        resp = requests.post(
            f"{base_url}/api/v2/pages",
            auth=auth,
            headers=headers_json,
            json=payload,
        )
        resp.raise_for_status()
        page_data = resp.json()
        page_id = page_data["id"]
        print(f"  Created page: {title} (id={page_id})")

    # --- Upload image attachments (v1 API — v2 doesn't support file upload) ---
    for img_path in image_files:
        if not img_path.exists():
            print(f"  WARNING: Image not found: {img_path}")
            continue

        with open(img_path, "rb") as f:
            resp = requests.post(
                f"{base_url}/rest/api/content/{page_id}/child/attachment",
                auth=auth,
                headers={"X-Atlassian-Token": "nocheck"},
                files={"file": (img_path.name, f, "image/png")},
            )
        if resp.status_code in (200, 201):
            print(f"  Uploaded attachment: {img_path.name}")
        else:
            print(f"  WARNING: Failed to upload {img_path.name}: {resp.status_code}")

    return page_data


# ---------------------------------------------------------------------------
# Mapping file (tracks MD file ↔ Confluence page ID)
# ---------------------------------------------------------------------------

MAPPING_FILE = ".confluence-mapping.json"


def load_mapping(base_dir: Path) -> dict:
    mapping_path = base_dir / MAPPING_FILE
    if mapping_path.exists():
        with open(mapping_path) as f:
            return json.load(f)
    return {}


def save_mapping(base_dir: Path, mapping: dict):
    mapping_path = base_dir / MAPPING_FILE
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_single_file(
    md_path: Path,
    output_dir: Path,
    upload: bool = False,
    mapping: Optional[dict] = None,
) -> dict:
    """Process a single Markdown file through the full pipeline."""
    print(f"\nProcessing: {md_path}")

    md_content = md_path.read_text(encoding="utf-8")
    title = extract_title(md_content)

    # Stage 1: Mermaid → Images
    images_dir = output_dir / "images"
    processed_md, image_files = process_mermaid_diagrams(md_content, images_dir)

    # Stage 2: Markdown → Confluence storage format
    body_html = md_to_confluence_storage(processed_md)

    # Save output
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = md_path.stem
    html_path = output_dir / f"{stem}.confluence.html"
    html_path.write_text(body_html, encoding="utf-8")
    print(f"  Output: {html_path}")

    result = {
        "source": str(md_path),
        "title": title,
        "output_html": str(html_path),
        "images": image_files,
    }

    # Stage 3: Upload (optional)
    if upload:
        domain = os.environ.get("CONFLUENCE_DOMAIN")
        space_id = os.environ.get("CONFLUENCE_SPACE_ID")
        api_token = os.environ.get("CONFLUENCE_API_TOKEN")
        email = os.environ.get("CONFLUENCE_EMAIL")
        parent_id = os.environ.get("CONFLUENCE_PARENT_PAGE_ID")

        if not all([domain, space_id, api_token, email]):
            print("  ERROR: Missing environment variables for upload.")
            print("  Required: CONFLUENCE_DOMAIN, CONFLUENCE_SPACE_ID,")
            print("            CONFLUENCE_API_TOKEN, CONFLUENCE_EMAIL")
            return result

        # Check if page already exists in mapping
        page_id = None
        if mapping and str(md_path) in mapping:
            page_id = mapping[str(md_path)]

        image_paths = [images_dir / f for f in image_files]
        page_data = upload_to_confluence(
            title=title,
            body_html=body_html,
            image_files=image_paths,
            domain=domain,
            space_id=space_id,
            api_token=api_token,
            email=email,
            parent_id=parent_id,
            page_id=page_id,
        )

        result["page_id"] = page_data.get("id")
        if mapping is not None:
            mapping[str(md_path)] = page_data.get("id")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to Confluence storage format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s README.md -o output/
  %(prog)s specs/ -o output/
  %(prog)s specs/ --upload
        """,
    )
    parser.add_argument(
        "input",
        help="Markdown file or directory containing .md files",
    )
    parser.add_argument(
        "-o", "--output",
        default="./confluence-output",
        help="Output directory (default: ./confluence-output)",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload to Confluence (requires env vars)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="Mermaid diagram width in pixels (default: 1200)",
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: {input_path} does not exist")
        sys.exit(1)

    # Collect .md files
    if input_path.is_file():
        md_files = [input_path]
    else:
        md_files = sorted(input_path.rglob("*.md"))
        if not md_files:
            print(f"No .md files found in {input_path}")
            sys.exit(1)

    print(f"Found {len(md_files)} Markdown file(s)")

    # Load mapping for upload tracking
    mapping = load_mapping(input_path if input_path.is_dir() else input_path.parent)

    results = []
    for md_file in md_files:
        # Preserve directory structure in output
        if input_path.is_dir():
            relative = md_file.relative_to(input_path)
            file_output_dir = output_dir / relative.parent
        else:
            file_output_dir = output_dir

        result = process_single_file(
            md_file, file_output_dir, args.upload, mapping
        )
        results.append(result)

    # Save mapping
    if args.upload:
        save_mapping(
            input_path if input_path.is_dir() else input_path.parent,
            mapping,
        )

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Processed {len(results)} file(s)")
    print(f"Output directory: {output_dir}")
    if args.upload:
        uploaded = sum(1 for r in results if r.get("page_id"))
        print(f"Uploaded: {uploaded}/{len(results)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
