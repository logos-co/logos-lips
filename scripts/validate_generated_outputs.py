#!/usr/bin/env python3
"""
Validate generated mdBook and landing-page indexes against source specs.

Run this after `gen_rfc_index.py` and `gen_summary.py`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple

from validate_metadata import DOCS, ROOT, discover_docs, read_doc

SUMMARY = DOCS / "SUMMARY.md"
INDEX = DOCS / "logos-lips.json"
EXCLUDE_INDEX_PARTS = {"previous-versions"}
SUMMARY_LINK_RE = re.compile(r"\[(?:\\.|[^\]\\])+\]\(([^)]+\.md(?:#[^)]+)?)\)")


def parse_summary_links() -> Tuple[set[Path], List[str]]:
    links: set[Path] = set()
    errors: List[str] = []

    if not SUMMARY.exists():
        return links, [f"{SUMMARY.relative_to(ROOT)} is missing"]

    text = SUMMARY.read_text(encoding="utf-8", errors="ignore")
    for match in SUMMARY_LINK_RE.finditer(text):
        raw_target = match.group(1).split("#", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9+.-]*:", raw_target, re.IGNORECASE):
            continue
        target = (DOCS / raw_target).resolve()
        if not target.is_relative_to(DOCS.resolve()):
            errors.append(f"{SUMMARY.relative_to(ROOT)} links outside docs/: {raw_target}")
            continue
        if not target.exists():
            errors.append(f"{SUMMARY.relative_to(ROOT)} links to missing file: {raw_target}")
            continue
        links.add(target)

    return links, errors


def validate_summary_coverage() -> List[str]:
    linked_paths, errors = parse_summary_links()
    expected_paths = {path.resolve() for path in discover_docs()}

    missing = sorted(expected_paths - linked_paths)
    if missing:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        errors.append(f"{SUMMARY.relative_to(ROOT)} is missing spec link(s): {joined}")

    extra = sorted(
        path
        for path in linked_paths - expected_paths
        if path.name not in {"README.md", "about.md"}
    )
    if extra:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in extra)
        errors.append(f"{SUMMARY.relative_to(ROOT)} links non-spec Markdown file(s): {joined}")

    return errors


def validate_index_coverage() -> List[str]:
    if not INDEX.exists():
        return [f"{INDEX.relative_to(ROOT)} is missing"]

    try:
        data = json.loads(INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{INDEX.relative_to(ROOT)} is invalid JSON: {exc}"]

    if not isinstance(data, list):
        return [f"{INDEX.relative_to(ROOT)} must contain a JSON list"]

    actual_paths = {
        item.get("path")
        for item in data
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    expected_paths = {
        read_doc(path).rel.relative_to("docs").with_suffix(".html").as_posix()
        for path in discover_docs()
        if not EXCLUDE_INDEX_PARTS.intersection(path.relative_to(ROOT).parts)
    }

    errors: List[str] = []
    missing = sorted(expected_paths - actual_paths)
    if missing:
        errors.append(
            f"{INDEX.relative_to(ROOT)} is missing spec path(s): {', '.join(missing)}"
        )

    extra = sorted(actual_paths - expected_paths)
    if extra:
        errors.append(
            f"{INDEX.relative_to(ROOT)} contains non-spec path(s): {', '.join(extra)}"
        )

    return errors


def main() -> int:
    errors = validate_summary_coverage()
    errors.extend(validate_index_coverage())

    for error in errors:
        print(f"[ERROR] {error}")

    if errors:
        print(f"[FAIL] generated output validation failed with {len(errors)} error(s)")
        return 1

    print("[OK] generated output validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
