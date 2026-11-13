#!/usr/bin/env python3
"""
Validate generated mdBook and landing-page indexes against source specs.

Run this after `gen_rfc_index.py` and `gen_summary.py`.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List, Tuple

from target_args import add_target_args, load_target_paths
from validate_metadata import DOCS, ROOT, EXCLUDE_FILES, EXCLUDE_PARTS, discover_docs, read_doc

SUMMARY = DOCS / "SUMMARY.md"
INDEX = DOCS / "logos-lips.json"
EXCLUDE_INDEX_PARTS = {"previous-versions", "appendix", "appendices", "rfc"}
SUMMARY_AUXILIARY_PARTS = {"appendix", "appendices", "rfc"}
SUMMARY_ALLOWED_NON_SPEC_FILES = {"README.md", "about.md", "template.md"}
SUMMARY_LINK_RE = re.compile(r"\[(?:\\.|[^\]\\])+\]\(([^)]+\.md(?:#[^)]+)?)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    add_target_args(parser)
    return parser.parse_args()


def target_spec_rels(targets: list[Path] | None) -> set[Path]:
    if targets is None:
        return set()

    rels: set[Path] = set()
    for target in targets:
        if len(target.parts) < 2 or target.parts[0] != "docs":
            continue
        docs_rel = Path(*target.parts[1:])
        if docs_rel.suffix.lower() != ".md":
            continue
        if docs_rel.name in EXCLUDE_FILES:
            continue
        if EXCLUDE_PARTS.intersection(docs_rel.parts):
            continue
        rels.add(docs_rel)
    return rels


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


def validate_summary_coverage(targets: list[Path] | None = None) -> List[str]:
    linked_paths, errors = parse_summary_links()
    expected_paths = {path.resolve() for path in discover_docs(targets)}

    missing = sorted(expected_paths - linked_paths)
    if missing:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        errors.append(f"{SUMMARY.relative_to(ROOT)} is missing spec link(s): {joined}")

    if targets is not None:
        deleted = sorted(
            (DOCS / rel).resolve()
            for rel in target_spec_rels(targets)
            if not (DOCS / rel).exists()
        )
        stale = [path for path in deleted if path in linked_paths]
        if stale:
            joined = ", ".join(str(path.relative_to(ROOT)) for path in stale)
            errors.append(f"{SUMMARY.relative_to(ROOT)} still links deleted spec(s): {joined}")
        return errors

    extra = sorted(
        path
        for path in linked_paths - expected_paths
        if path.name not in SUMMARY_ALLOWED_NON_SPEC_FILES
        and not SUMMARY_AUXILIARY_PARTS.intersection(path.relative_to(DOCS).parts)
    )
    if extra:
        joined = ", ".join(str(path.relative_to(ROOT)) for path in extra)
        errors.append(f"{SUMMARY.relative_to(ROOT)} links non-spec Markdown file(s): {joined}")

    return errors


def validate_index_coverage(targets: list[Path] | None = None) -> List[str]:
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
        for path in discover_docs(targets)
        if not EXCLUDE_INDEX_PARTS.intersection(path.relative_to(ROOT).parts)
    }

    errors: List[str] = []
    missing = sorted(expected_paths - actual_paths)
    if missing:
        errors.append(
            f"{INDEX.relative_to(ROOT)} is missing spec path(s): {', '.join(missing)}"
        )

    if targets is not None:
        deleted = sorted(
            rel.with_suffix(".html").as_posix()
            for rel in target_spec_rels(targets)
            if not (DOCS / rel).exists()
            and not EXCLUDE_INDEX_PARTS.intersection(("docs", *rel.parts))
        )
        stale = sorted(path for path in deleted if path in actual_paths)
        if stale:
            errors.append(
                f"{INDEX.relative_to(ROOT)} still contains deleted spec path(s): {', '.join(stale)}"
            )
        return errors

    extra = sorted(actual_paths - expected_paths)
    if extra:
        errors.append(
            f"{INDEX.relative_to(ROOT)} contains non-spec path(s): {', '.join(extra)}"
        )

    return errors


def main() -> int:
    args = parse_args()
    targets = load_target_paths(ROOT, args)
    errors = validate_summary_coverage(targets)
    errors.extend(validate_index_coverage(targets))

    for error in errors:
        print(f"[ERROR] {error}")

    if errors:
        print(f"[FAIL] generated output validation failed with {len(errors)} error(s)")
        return 1

    print("[OK] generated output validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
