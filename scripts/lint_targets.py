#!/usr/bin/env python3
"""List changed non-raw Markdown files under docs/ for linting."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

RAW_STATUS_RE = re.compile(r"^\|\s*status\s*\|\s*raw\s*\|$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-sha", required=True, help="Base commit SHA")
    parser.add_argument("--head-sha", required=True, help="Head commit SHA")
    parser.add_argument("--output", help="Write targets to this file")
    return parser.parse_args()


def changed_files(base_sha: str, head_sha: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "diff", "--name-only", base_sha, head_sha],
        text=True,
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def log(message: str) -> None:
    print(message, file=sys.stderr)


def is_in_raw_dir(path: Path) -> bool:
    return "raw" in path.parts


def has_raw_status(path: Path) -> bool:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return False

    for line in lines[:220]:
        if RAW_STATUS_RE.match(line.strip()):
            return True
    return False


def lint_targets(base_sha: str, head_sha: str) -> list[str]:
    targets: list[str] = []
    skipped = 0
    for rel_path in changed_files(base_sha, head_sha):
        path = Path(rel_path)
        if not rel_path.startswith("docs/"):
            continue
        if path.suffix.lower() != ".md":
            continue
        if not path.exists():
            skipped += 1
            log(f"SKIP   {rel_path} (deleted or missing in working tree)")
            continue
        if is_in_raw_dir(path):
            skipped += 1
            log(f"SKIP   {rel_path} (path is under /raw/)")
            continue
        if has_raw_status(path):
            skipped += 1
            log(f"SKIP   {rel_path} (metadata status is raw)")
            continue
        targets.append(rel_path)
        log(f"SELECT {rel_path}")

    unique_targets = sorted(set(targets))
    log(f"Summary: selected={len(unique_targets)} skipped={skipped}")
    return unique_targets


def main() -> int:
    args = parse_args()
    targets = lint_targets(args.base_sha, args.head_sha)
    output = "\n".join(targets)

    if args.output:
        Path(args.output).write_text((output + "\n") if output else "", encoding="utf-8")
        log(f"Wrote {len(targets)} lint target(s) to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
