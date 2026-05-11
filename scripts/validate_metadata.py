#!/usr/bin/env python3
"""
Validate RFC metadata tables and auto-assign invalid or missing slugs.

By default, this script writes fixes for missing/blank/invalid `Slug` values and
returns non-zero on any validation issue.
Use `--check` to run in read-only mode.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

EXCLUDE_FILES = {"README.md", "SUMMARY.md", "about.md", "template.md"}
# Fields required for draft and above; raw specs only need name + status.
REQUIRED_FIELDS_ALL = ("name", "slug", "status", "type", "category", "editor")
REQUIRED_FIELDS_RAW = ("name", "status")
ALLOWED_STATUS = {"raw", "draft", "approved", "stable", "verified", "deprecated", "retired", "deleted"}
STATUS_SCOPED_COMPONENTS = {"blockchain", "storage", "anoncomms", "process"}
ALLOWED_TYPES = {"rfc", "cfr"}
ALLOWED_CATEGORIES = {
    "standards track",
    "informational",
    "best current practice",
    "process",
    "infrastructure",
    "networking",
}

SEPARATOR_RE = re.compile(r"^\|\s*:?-{3,}:?\s*\|\s*:?-{3,}:?\s*\|$")
ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$")
HEADER_RE = re.compile(r"^\|\s*field\s*\|\s*value\s*\|$", re.IGNORECASE)
NUMERIC_RE = re.compile(r"^[1-9][0-9]*$")
FRONT_MATTER_KEY_RE = re.compile(
    r"^(title|name|slug|status|type|category|tags|editor|contributors)\s*:",
    re.IGNORECASE,
)
CANONICAL_HEADER = "| Field | Value |"


@dataclass
class TableInfo:
    start: int
    separator: int
    end: int
    rows: Dict[str, Tuple[int, str, str]]


@dataclass
class DocInfo:
    path: Path
    rel: Path
    lines: List[str]
    table: Optional[TableInfo]
    errors: List[str]
    assigned_slug: Optional[int] = None

    def meta(self) -> Dict[str, str]:
        if not self.table:
            return {}
        return {k: v for k, (_, _, v) in self.table.rows.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate RFC metadata.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Read-only mode; do not write missing slugs.",
    )
    return parser.parse_args()


def discover_docs() -> List[Path]:
    files = []
    for path in DOCS.rglob("*.md"):
        if path.name in EXCLUDE_FILES:
            continue
        files.append(path)
    return sorted(files)


def find_metadata_table(lines: List[str]) -> Optional[TableInfo]:
    max_scan = min(len(lines), 220)
    for idx in range(max_scan - 1):
        if not HEADER_RE.match(lines[idx].strip()):
            continue
        if not SEPARATOR_RE.match(lines[idx + 1].strip()):
            continue

        rows: Dict[str, Tuple[int, str, str]] = {}
        row_idx = idx + 2
        while row_idx < len(lines) and lines[row_idx].strip().startswith("|"):
            raw = lines[row_idx].strip()
            match = ROW_RE.match(raw)
            if match:
                key_display = match.group(1).strip()
                key = key_display.lower()
                value = match.group(2).strip()
                if key not in rows:
                    rows[key] = (row_idx, key_display, value)
            row_idx += 1

        return TableInfo(start=idx, separator=idx + 1, end=row_idx, rows=rows)
    return None


def first_nonblank_line(lines: List[str], start: int = 0) -> Optional[int]:
    for idx in range(start, len(lines)):
        if lines[idx].strip():
            return idx
    return None


def has_yaml_front_matter(lines: List[str]) -> bool:
    first = first_nonblank_line(lines)
    if first is None or lines[first].strip() != "---":
        return False

    for idx in range(first + 1, min(len(lines), first + 80)):
        line = lines[idx].strip()
        if line == "---":
            block = lines[first + 1 : idx]
            return any(FRONT_MATTER_KEY_RE.match(item.strip()) for item in block)
    return False


def expected_metadata_table_start(lines: List[str]) -> Optional[int]:
    first = first_nonblank_line(lines)
    if first is None:
        return None
    if lines[first].startswith("# "):
        return first_nonblank_line(lines, first + 1)
    return first


def read_doc(path: Path) -> DocInfo:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    table = find_metadata_table(lines)
    return DocInfo(
        path=path,
        rel=path.relative_to(ROOT),
        lines=lines,
        table=table,
        errors=[],
    )


def lifecycle_status_dir(rel: Path) -> Optional[str]:
    parts = rel.parts
    if len(parts) < 4 or parts[0] != "docs":
        return None
    component = parts[1]
    if component not in STATUS_SCOPED_COMPONENTS:
        return None
    for part in parts[2:-1]:
        if part in ALLOWED_STATUS:
            return part
    return None


def next_free_slug(used: set[int]) -> int:
    candidate = max(used, default=0) + 1
    while candidate in used:
        candidate += 1
    return candidate


def assign_slug(doc: DocInfo, slug: int) -> None:
    assert doc.table is not None
    slug_row = doc.table.rows.get("slug")
    if slug_row:
        row_idx, key_display, _ = slug_row
        doc.lines[row_idx] = f"| {key_display} | {slug} |"
    else:
        name_row = doc.table.rows.get("name")
        status_row = doc.table.rows.get("status")
        if name_row:
            insert_idx = name_row[0] + 1
        elif status_row:
            insert_idx = status_row[0]
        else:
            insert_idx = doc.table.separator + 1
        doc.lines.insert(insert_idx, f"| Slug | {slug} |")
    doc.table = find_metadata_table(doc.lines)
    doc.assigned_slug = slug


def collect_used_numeric_slugs(docs: List[DocInfo]) -> set[int]:
    used: set[int] = set()
    for doc in docs:
        if not doc.table:
            continue
        slug = doc.meta().get("slug", "")
        if NUMERIC_RE.fullmatch(slug):
            used.add(int(slug))
    return used


def slug_needs_assignment(doc: DocInfo, seen: set[int]) -> bool:
    slug = doc.meta().get("slug", "").strip()
    if not NUMERIC_RE.fullmatch(slug):
        return True

    value = int(slug)
    if "previous-versions" in doc.rel.parts:
        return False
    if value in seen:
        return True

    seen.add(value)
    return False


def maybe_assign_slugs(docs: List[DocInfo], check_mode: bool) -> List[DocInfo]:
    if check_mode:
        return []

    changed: List[DocInfo] = []
    used = collect_used_numeric_slugs(docs)
    seen_unique: set[int] = set()
    for doc in docs:
        if not doc.table:
            continue
        if not slug_needs_assignment(doc, seen_unique):
            continue
        free_slug = next_free_slug(used)
        assign_slug(doc, free_slug)
        used.add(free_slug)
        changed.append(doc)
    return changed


def validate_doc(doc: DocInfo) -> None:
    if has_yaml_front_matter(doc.lines):
        doc.errors.append(
            "YAML front matter is not supported; use the canonical Markdown metadata table"
        )

    if not doc.table:
        doc.errors.append(f"missing metadata table '{CANONICAL_HEADER}'")
        return

    expected_start = expected_metadata_table_start(doc.lines)
    if expected_start is not None and doc.table.start != expected_start:
        doc.errors.append(
            "metadata table must appear at the top of the spec, immediately after the optional H1"
        )

    # Ensure standard header rows remain canonical.
    if doc.lines[doc.table.start].strip() != CANONICAL_HEADER:
        doc.errors.append(f"metadata header row must be exactly '{CANONICAL_HEADER}'")
    if not SEPARATOR_RE.match(doc.lines[doc.table.separator].strip()):
        doc.errors.append("metadata separator row is malformed")

    # Row formatting validation.
    for idx in range(doc.table.start + 2, doc.table.end):
        line = doc.lines[idx].strip()
        if line and not ROW_RE.match(line):
            doc.errors.append(f"malformed metadata row at line {idx + 1}: {line}")

    meta = doc.meta()

    status = meta.get("status", "").strip().lower()

    # Raw specs have relaxed requirements; draft and above enforce all fields.
    required_fields = REQUIRED_FIELDS_RAW if status == "raw" else REQUIRED_FIELDS_ALL
    for field in required_fields:
        if not meta.get(field, "").strip():
            doc.errors.append(f"missing required metadata field '{field}'")

    if status and status not in ALLOWED_STATUS:
        allowed = ", ".join(sorted(ALLOWED_STATUS))
        doc.errors.append(f"invalid status '{status}' (allowed: {allowed})")

    rel_parts = set(doc.rel.parts)
    if "deprecated" in rel_parts and status not in {"deprecated", "deleted"}:
        doc.errors.append(
            "file is under '/deprecated/' but status is not deprecated/deleted"
        )

    status_dir = lifecycle_status_dir(doc.rel)
    component = doc.rel.parts[1] if len(doc.rel.parts) > 1 else ""
    if component in STATUS_SCOPED_COMPONENTS:
        if not status_dir:
            doc.errors.append(
                f"file is under status-scoped component '{component}' but not under a lifecycle status directory"
            )
        elif status and status != status_dir:
            doc.errors.append(
                f"file is under '/{status_dir}/' but metadata status is '{status}'"
            )

    slug = meta.get("slug", "").strip()
    if slug and not NUMERIC_RE.fullmatch(slug):
        doc.errors.append("slug must be a positive integer")

    # Validate type field if present (optional, default RFC).
    doc_type = meta.get("type", "").strip().lower()
    if doc_type and doc_type not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        doc.errors.append(
            f"unknown type '{meta.get('type', '')}' (expected one of: {allowed})"
        )

    # Only enforce category for non-raw specs.
    if status != "raw":
        category = meta.get("category", "").strip().lower()
        if category and category not in ALLOWED_CATEGORIES:
            allowed = ", ".join(sorted(ALLOWED_CATEGORIES))
            doc.errors.append(
                f"unknown category '{meta.get('category', '')}' (expected one of: {allowed})"
            )


def validate_slug_uniqueness(docs: List[DocInfo]) -> List[str]:
    # Allow duplicated slugs in archived previous-version snapshots.
    slug_map: Dict[int, List[Path]] = {}
    for doc in docs:
        if not doc.table:
            continue
        if "previous-versions" in doc.rel.parts:
            continue
        slug = doc.meta().get("slug", "").strip()
        if not NUMERIC_RE.fullmatch(slug):
            continue
        slug_map.setdefault(int(slug), []).append(doc.rel)

    errors: List[str] = []
    for slug, paths in sorted(slug_map.items()):
        if len(paths) <= 1:
            continue
        joined = ", ".join(str(p) for p in paths)
        errors.append(f"duplicate slug {slug}: {joined}")
    return errors


def write_if_changed(doc: DocInfo) -> None:
    text = "\n".join(doc.lines).rstrip() + "\n"
    doc.path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    docs = [read_doc(path) for path in discover_docs()]

    changed = maybe_assign_slugs(docs, check_mode=args.check)
    for doc in docs:
        validate_doc(doc)

    global_errors = validate_slug_uniqueness(docs)

    if changed:
        for doc in changed:
            write_if_changed(doc)
            print(f"[FIX] Assigned slug {doc.assigned_slug} in {doc.rel}")

    error_count = len(global_errors)
    for doc in docs:
        for error in doc.errors:
            error_count += 1
            print(f"[ERROR] {doc.rel}: {error}")

    for error in global_errors:
        print(f"[ERROR] {error}")

    if error_count:
        print(f"[FAIL] metadata validation failed with {error_count} error(s)")
        return 1

    print(
        "[OK] metadata validation passed"
        + (f"; updated {len(changed)} file(s)" if changed else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
