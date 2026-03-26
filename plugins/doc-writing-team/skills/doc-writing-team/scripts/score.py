#!/usr/bin/env python3
"""
score.py

Contract-aware structural scoring helper for ADR/HLD/LLD drafts.
It is not a full reviewer replacement; it provides a quick structural check
aligned to the canonical contract.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT = json.loads((REPO_ROOT / "skills/doc-writing-team/contract.json").read_text(encoding="utf-8"))


def load_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def has_section(text: str, section: str) -> bool:
    escaped = re.escape(section)
    patterns = [
        rf"^#{{1,3}}\s+{escaped}(?:\s*:.*)?\s*$",
        rf"^#{{1,3}}\s+\d+(?:\.\d+)*\.?\s+{escaped}(?:\s*:.*)?\s*$",
    ]
    return any(re.search(pattern, text, flags=re.MULTILINE) for pattern in patterns)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: score.py <ADR|HLD|LLD> [path]", file=sys.stderr)
        return 1

    doc_type = sys.argv[1].upper()
    path = sys.argv[2] if len(sys.argv) > 2 else None
    text = load_text(path)

    if doc_type not in CONTRACT["documentTypes"]:
        print(json.dumps({"error": f"Unknown doc type: {doc_type}"}))
        return 1

    score = 100
    missing_sections: list[str] = []
    required = CONTRACT["documentTypes"][doc_type]["requiredSections"]
    appendix_allowed = CONTRACT["documentTypes"][doc_type]["appendixAllowed"]

    for section in required:
        if not has_section(text, section):
            missing_sections.append(section)
            score -= 12

    if not appendix_allowed and has_section(text, "Appendix"):
        score -= 10

    if doc_type == "ADR" and "**{Option X}**를 선택합니다." in text:
        score -= 10

    result = {
        "doc_type": doc_type,
        "score": max(score, 0),
        "missing_sections": missing_sections,
        "appendix_allowed": appendix_allowed,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
