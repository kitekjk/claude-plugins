#!/usr/bin/env python3
"""
validate_repo_contract.py  (doc-writing-team v3.2.0)

플러그인 루트 기준으로 contract.json과 실제 파일들의 정합성을 검증합니다.
설치된 프로젝트의 doc-orchestrator가 content-reviewer 완료 후 호출합니다.

사용법:
    python3 validate_repo_contract.py [plugin_root]

    plugin_root: 플러그인 루트 경로 (기본값: 이 스크립트 기준 3단계 상위)
                 scripts/ → skills/doc-writing-team/ → plugins/doc-writing-team/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def resolve_plugin_root(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1]).resolve()
    return Path(__file__).resolve().parents[2]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def file_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def contains(root: Path, rel: str, needle: str) -> bool:
    return needle in read_text(root, rel)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    plugin_root = resolve_plugin_root(sys.argv)
    contract_path = plugin_root / "skills/doc-writing-team/contract.json"

    errors: list[str] = []

    # ── contract.json 존재 확인 ──────────────────────────────────────────────
    if not contract_path.exists():
        print("FAIL")
        print("  - contract.json 없음")
        return 1

    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    # ── documentTypes 필수 파일 존재 확인 ───────────────────────────────────
    for doc_type, dt in contract.get("documentTypes", {}).items():
        for key in ("specFile", "templateFile", "checklistFile"):
            rel = dt.get(key, "")
            # contract.json의 경로는 plugin root 기준 상대경로
            require(
                file_exists(plugin_root, f"skills/doc-writing-team/{rel}") or file_exists(plugin_root, rel),
                f"{doc_type}: {key} 경로 없음 → {rel}",
                errors,
            )

    # ── 스토리지 규칙: style_guide에 DOCUMENT.md 명시 ───────────────────────
    style_guide_rel = "skills/doc-writing-team/memory/style_guide.md"
    if file_exists(plugin_root, style_guide_rel):
        require(
            contains(plugin_root, style_guide_rel, "DOCUMENT.md"),
            "style_guide.md에 DOCUMENT.md 저장 규칙이 없음",
            errors,
        )

    # ── ADR Decision 정책 ────────────────────────────────────────────────────
    adr_spec_rel = "skills/doc-writing-team/specs/adr.md"
    if file_exists(plugin_root, adr_spec_rel):
        require(
            contains(plugin_root, adr_spec_rel, "[TBD]"),
            "ADR spec에 [TBD] 정책이 없음",
            errors,
        )

    adr_checklist_rel = "skills/doc-writing-team/checklists/adr-checklist.md"
    if file_exists(plugin_root, adr_checklist_rel):
        require(
            contains(plugin_root, adr_checklist_rel, "TBD"),
            "ADR 체크리스트에 Decision/TBD 검증 항목이 없음",
            errors,
        )

    # ── HLD / LLD Appendix 지원 ──────────────────────────────────────────────
    for writer_rel, label in [("agents/hld-writer.md", "HLD"), ("agents/lld-writer.md", "LLD")]:
        if file_exists(plugin_root, writer_rel):
            require(
                contains(plugin_root, writer_rel, "Appendix"),
                f"{label} writer에 Appendix 지원 선언이 없음",
                errors,
            )

    # ── v3.x: specDerivability 확인 ─────────────────────────────────────────
    for doc_type in ("HLD", "LLD"):
        dt = contract.get("documentTypes", {}).get(doc_type, {})
        require(
            "specDerivability" in dt,
            f"contract.json의 {doc_type}에 specDerivability 필드 없음",
            errors,
        )

    # ── v3.1: HLD→LLD 추적성 확인 ───────────────────────────────────────────
    lld_dt = contract.get("documentTypes", {}).get("LLD", {})
    require(
        "hldTraceability" in lld_dt,
        "contract.json의 LLD에 hldTraceability 필드 없음",
        errors,
    )

    lld_writer_rel = "agents/lld-writer.md"
    if file_exists(plugin_root, lld_writer_rel):
        require(
            contains(plugin_root, lld_writer_rel, "연관 HLD"),
            "lld-writer.md에 연관 HLD 처리 로직이 없음",
            errors,
        )

    lld_checklist_rel = "skills/doc-writing-team/checklists/lld-checklist.md"
    if file_exists(plugin_root, lld_checklist_rel):
        require(
            contains(plugin_root, lld_checklist_rel, "HLD 정합성"),
            "lld-checklist.md에 HLD 정합성 섹션이 없음",
            errors,
        )

    # ── 피드백 스키마 ─────────────────────────────────────────────────────────
    schema_rel = "skills/doc-writing-team/memory/FEEDBACK_SCHEMA.md"
    if file_exists(plugin_root, schema_rel):
        require(
            contains(plugin_root, schema_rel, "user_feedback_raw"),
            "FEEDBACK_SCHEMA.md에 user_feedback_raw 필드가 없음",
            errors,
        )

    style_learner_rel = "agents/style-learner.md"
    if file_exists(plugin_root, style_learner_rel):
        require(
            contains(plugin_root, style_learner_rel, "user_feedback_raw"),
            "style-learner.md에 user_feedback_raw 필드가 없음",
            errors,
        )

    # ── 결과 출력 ────────────────────────────────────────────────────────────
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
