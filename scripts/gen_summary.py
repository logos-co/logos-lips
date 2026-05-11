#!/usr/bin/env python3
"""
Generate docs/SUMMARY.md from the docs/ tree.

This keeps a consistent navigation structure for mdBook without manual edits.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, List, Optional

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUTPUT = DOCS / "SUMMARY.md"

SKIP_FILES = {"README.md", "SUMMARY.md", "template.md"}

TOP_LEVEL = ["messaging", "blockchain", "storage", "anoncomms", "research"]

LABEL_OVERRIDES = {
    "anoncomms": "AnonComms",
    "messaging/raw": "Raw",
    "messaging/draft": "Draft",
    "messaging/stable": "Stable",
    "messaging/deprecated": "Deprecated",
    "messaging/deleted": "Deleted",
    "blockchain/raw": "Raw",
    "blockchain/draft": "Draft",
    "blockchain/deprecated": "Deprecated",
    "storage/raw": "Raw",
    "storage/draft": "Draft",
    "storage/deprecated": "Deprecated",
    "anoncomms/raw": "Raw",
    "anoncomms/draft": "Draft",
    "anoncomms/deleted": "Deleted",
    "research": "Research",
    "research/draft": "Draft",
}

ORDER_OVERRIDES = {
    "messaging": [
        "raw",
        "draft",
        "stable",
        "deprecated",
        "deleted",
    ],
    "blockchain": ["raw", "draft", "deprecated"],
    "storage": ["raw", "draft", "deprecated"],
    "anoncomms": ["raw", "draft", "deleted"],
    "research": ["draft"],
}

ACRONYMS = {
    "api",
    "bcp",
    "coss",
    "dns",
    "dht",
    "enr",
    "eth",
    "ift",
    "ipfs",
    "id",
    "mls",
    "mvds",
    "nomosda",
    "p2p",
    "rfc",
    "rln",
    "rpc",
    "sds",
    "waku",
    "x3dh",
}


@dataclass
class Item:
    label: str
    path: Path
    children: List["Item"]


def read_h1(path: Path) -> Optional[str]:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def humanize(stem: str) -> str:
    parts = re.split(r"[-_]+", stem)
    words = []
    for part in parts:
        if not part:
            continue
        lower = part.lower()
        if lower in ACRONYMS:
            words.append(part.upper())
        elif re.fullmatch(r"v\d+", lower):
            words.append(part.upper())
        elif re.search(r"\d", part):
            words.append(part.upper())
        else:
            words.append(part.capitalize())
    return " ".join(words)


def label_for_file(path: Path) -> str:
    title = read_h1(path)
    if not title:
        title = humanize(path.stem)
    parent = path.parent
    if parent.name.isdigit() and not title.startswith(f"{parent.name}/"):
        return f"{parent.name}/{title}"
    return title


def label_for_dir(rel_dir: Path) -> str:
    key = rel_dir.as_posix()
    return LABEL_OVERRIDES.get(key, humanize(rel_dir.name))


def sorted_dirs(base: Path, rel_base: Path) -> Iterable[Path]:
    overrides = ORDER_OVERRIDES.get(rel_base.as_posix())
    dirs = [p for p in base.iterdir() if p.is_dir()]
    if overrides:
        ordered = []
        for item in overrides:
            match = base / item
            if match.exists() and match.is_dir():
                ordered.append(match)
        remaining = [d for d in dirs if d not in ordered]
        return ordered + sorted(remaining, key=lambda p: p.name)
    return sorted(dirs, key=lambda p: p.name)


def has_child_readme(path: Path) -> bool:
    return any((child / "README.md").exists() for child in path.iterdir() if child.is_dir())


def item_sort_key(item: Item) -> tuple:
    parent = item.path.parent
    num = None
    if parent.name.isdigit():
        num = int(parent.name)
    else:
        match = re.match(r"(\\d+)", item.path.stem)
        if match:
            num = int(match.group(1))
    if num is not None:
        return (0, num, item.label.lower())
    return (1, item.label.lower())


def build_items(base: Path, rel_base: Path) -> List[Item]:
    sections: List[Item] = []
    items: List[Item] = []

    for subdir in sorted_dirs(base, rel_base):
        if subdir.name == "previous-versions":
            continue
        rel_subdir = subdir.relative_to(DOCS)
        readme = subdir / "README.md"
        if readme.exists():
            children = build_items(subdir, rel_subdir)
            sections.append(Item(label=label_for_dir(rel_subdir), path=readme, children=children))
            continue
        if has_child_readme(subdir):
            continue

        md_files = [p for p in subdir.glob("*.md") if p.name not in SKIP_FILES]
        if not md_files:
            md_files = [
                p
                for p in subdir.rglob("*.md")
                if "previous-versions" not in p.parts and p.name not in SKIP_FILES
            ]
        for file in sorted(md_files, key=lambda p: p.name):
            item = Item(label=label_for_file(file), path=file, children=[])
            prev_dir = subdir / "previous-versions"
            if prev_dir.exists() and prev_dir.is_dir():
                for version_dir in sorted(prev_dir.iterdir(), key=lambda p: p.name):
                    if not version_dir.is_dir():
                        continue
                    for prev_file in sorted(version_dir.glob("*.md"), key=lambda p: p.name):
                        label = f"{version_dir.name} (previous)"
                        item.children.append(Item(label=label, path=prev_file, children=[]))
            items.append(item)

    for file in sorted(base.glob("*.md"), key=lambda p: p.name):
        if file.name in SKIP_FILES:
            continue
        items.append(Item(label=label_for_file(file), path=file, children=[]))

    items.sort(key=item_sort_key)

    return sections + items


def render_items(items: Iterable[Item], depth: int, lines: List[str]) -> None:
    indent = "  " * depth
    for item in items:
        rel = item.path.relative_to(DOCS).as_posix()
        lines.append(f"{indent}- [{item.label}]({rel})")
        if item.children:
            render_items(item.children, depth + 1, lines)


def main() -> None:
    lines: List[str] = ["# Summary", ""]

    if (DOCS / "README.md").exists():
        lines.append("[Introduction](README.md)")
    if (DOCS / "about.md").exists():
        lines.append("[About](about.md)")
    lines.append("")

    for section in TOP_LEVEL:
        section_dir = DOCS / section
        readme = section_dir / "README.md"
        if not readme.exists():
            continue
        label = LABEL_OVERRIDES.get(section, humanize(section))
        lines.append(f"- [{label}]({section}/{readme.name})")
        children = build_items(section_dir, Path(section))
        render_items(children, 1, lines)
        lines.append("")

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
