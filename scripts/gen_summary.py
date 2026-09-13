#!/usr/bin/env python3
"""
Generate docs/SUMMARY.md from the docs/ tree.

This keeps a consistent navigation structure for mdBook without manual edits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Iterable, List, Optional

import blockchain_structure as bc

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUTPUT = DOCS / "SUMMARY.md"
BLOCKCHAIN_TREE_JSON = DOCS / "blockchain-structure.json"

SKIP_FILES = {"README.md", "SUMMARY.md"}
AUXILIARY_DIR_NAMES = ("appendices", "appendix")

TOP_LEVEL = ["messaging", "blockchain", "storage", "anoncomms", "research", "logos-core"]

LABEL_OVERRIDES = {
    "anoncomms": "AnonComms",
    "messaging/core/raw": "Raw",
    "messaging/core/draft": "Draft",
    "messaging/core/stable": "Stable",
    "messaging/core/deprecated": "Deprecated",
    "messaging/application/raw": "Raw",
    "messaging/application/draft": "Draft",
    "messaging/application/stable": "Stable",
    "messaging/application/deprecated": "Deprecated",
    "messaging/application/deleted": "Deleted",
    "messaging/informational/raw": "Raw",
    "messaging/informational/draft": "Draft",
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
        "core",
        "application",
        "informational",
    ],
    "messaging/core": ["raw", "draft", "stable", "deprecated", "deleted"],
    "messaging/application": ["raw", "draft", "stable", "deprecated", "deleted"],
    "messaging/informational": ["raw", "draft", "stable", "deprecated", "deleted"],
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
    path: Optional[Path]  # None -> rendered as a draft (greyed) entry: `[Label]()`
    children: List["Item"] = field(default_factory=list)


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


def appendix_items_for_file(path: Path) -> List[Item]:
    """Return auxiliary appendix pages stored beside a spec file."""
    items: List[Item] = []
    base = path.with_suffix("")
    for dirname in AUXILIARY_DIR_NAMES:
        appendix_dir = base / dirname
        if not appendix_dir.is_dir():
            continue
        for file in sorted(appendix_dir.rglob("*.md"), key=lambda p: p.as_posix()):
            if file.name in SKIP_FILES:
                continue
            if "previous-versions" in file.parts:
                continue
            items.append(Item(label=label_for_file(file), path=file, children=[]))
    return sorted(items, key=lambda item: item.label.lower())


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
        if subdir.name in AUXILIARY_DIR_NAMES:
            continue
        if (base / f"{subdir.name}.md").exists():
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
            item = Item(label=label_for_file(file), path=file, children=appendix_items_for_file(file))
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
        items.append(Item(label=label_for_file(file), path=file, children=appendix_items_for_file(file)))

    items.sort(key=item_sort_key)

    return sections + items


def escape_label(label: str) -> str:
    """Escape `[` and `]` so they survive Markdown link-text parsing."""
    return label.replace("[", "\\[").replace("]", "\\]")


def render_items(items: Iterable[Item], depth: int, lines: List[str]) -> None:
    indent = "  " * depth
    for item in items:
        label = escape_label(item.label)
        if item.path is None:
            lines.append(f"{indent}- [{label}]()")
        else:
            rel = item.path.relative_to(DOCS).as_posix()
            lines.append(f"{indent}- [{label}]({rel})")
        if item.children:
            render_items(item.children, depth + 1, lines)


def read_status(path: Path) -> Optional[str]:
    """Return the lowercased value of the `Status` row in a spec metadata table."""
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"^\|\s*Status\s*\|\s*([^|]+?)\s*\|", line, re.IGNORECASE)
            if m:
                return m.group(1).strip().lower()
    except OSError:
        pass
    return None


def blockchain_groups() -> list[tuple[str, list[str]]]:
    groups = getattr(bc, "GROUPS", None)
    if not groups:
        return [(bc.BEDROCK_LABEL, bc.TOPIC_ORDER)]
    return [(label, list(topics)) for label, topics in groups]


def blockchain_topic_order() -> list[str]:
    topics: list[str] = []
    for _, group_topics in blockchain_groups():
        topics.extend(group_topics)
    return topics


def empty_blockchain_grouped() -> dict:
    return {
        topic: {bucket: [] for bucket in bc.buckets_for_topic(topic)}
        for topic in blockchain_topic_order()
    }


def build_blockchain_items() -> List[Item]:
    """
    Build the Blockchain section under the Notion-style topology defined in
    `blockchain_structure.py`. Each spec lands under its mapped topic; the
    bucket is derived from its `Status` field. Notion-only entries are emitted
    as draft links so the full target structure stays visible.
    """
    # Group real files by (topic, bucket).
    grouped: dict = empty_blockchain_grouped()
    for rel_path, (topic, label) in bc.FILE_ASSIGNMENTS.items():
        abs_path = DOCS / rel_path
        if not abs_path.exists():
            continue
        status = read_status(abs_path) or "raw"
        bucket = bc.STATUS_TO_BUCKET.get(status, "Merged")
        if topic not in grouped:
            grouped[topic] = {b: [] for b in bc.buckets_for_topic(topic)}
        if bucket not in grouped[topic]:
            grouped[topic][bucket] = []
        grouped[topic][bucket].append(
            Item(label=label, path=abs_path, children=appendix_items_for_file(abs_path))
        )

    group_items: List[Item] = []
    for group_label, group_topics in blockchain_groups():
        topic_items: List[Item] = []
        for topic in group_topics:
            bucket_items: List[Item] = []
            placeholders = bc.PLACEHOLDERS.get(topic, {})
            for bucket in bc.buckets_for_topic(topic):
                children: List[Item] = sorted(
                    grouped.get(topic, {}).get(bucket, []),
                    key=lambda i: i.label.lower(),
                )
                for placeholder_label in placeholders.get(bucket, []):
                    children.append(Item(label=placeholder_label, path=None))
                if not children:
                    continue
                bucket_items.append(Item(label=bucket, path=None, children=children))
            if bucket_items:
                if group_topics == [group_label]:
                    topic_items.extend(bucket_items)
                else:
                    topic_items.append(Item(label=topic, path=None, children=bucket_items))
        if topic_items:
            group_items.append(Item(label=group_label, path=None, children=topic_items))

    return group_items


def build_blockchain_tree_data() -> dict:
    """
    Same topology as `build_blockchain_items`, but emitted as a JSON-friendly
    dict for the in-page tree view on the Blockchain landing page.
    Each spec entry carries its `path` (relative to docs/) and `status`.
    Placeholder entries have `path: null` and `status: null`.
    """
    grouped: dict = empty_blockchain_grouped()
    for rel_path, (topic, label) in bc.FILE_ASSIGNMENTS.items():
        abs_path = DOCS / rel_path
        if not abs_path.exists():
            continue
        status = read_status(abs_path) or "raw"
        bucket = bc.STATUS_TO_BUCKET.get(status, "Merged")
        if topic not in grouped:
            grouped[topic] = {b: [] for b in bc.buckets_for_topic(topic)}
        if bucket not in grouped[topic]:
            grouped[topic][bucket] = []
        grouped[topic][bucket].append({
            "label": label,
            "path": rel_path,
            "status": status,
        })

    groups_out = []
    legacy_topics_out = []
    for group_label, group_topics in blockchain_groups():
        topics_out = []
        group_data = {"label": group_label, "topics": topics_out}
        for topic in group_topics:
            placeholders = bc.PLACEHOLDERS.get(topic, {})
            buckets_out = []
            for bucket in bc.buckets_for_topic(topic):
                specs = sorted(
                    grouped.get(topic, {}).get(bucket, []),
                    key=lambda s: s["label"].lower(),
                )
                for placeholder_label in placeholders.get(bucket, []):
                    specs.append({"label": placeholder_label, "path": None, "status": None})
                buckets_out.append({"name": bucket, "specs": specs})
            if group_topics == [group_label]:
                group_data = {"label": group_label, "buckets": buckets_out}
                legacy_topics_out.append({"name": group_label, "buckets": buckets_out})
            else:
                topic_data = {"name": topic, "buckets": buckets_out}
                topics_out.append(topic_data)
                legacy_topics_out.append(topic_data)
        groups_out.append(group_data)

    return {
        "label": "Blockchain",
        "topics": legacy_topics_out,
        "groups": groups_out,
    }


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
        if section == "blockchain":
            children = build_blockchain_items()
        else:
            children = build_items(section_dir, Path(section))
        render_items(children, 1, lines)
        lines.append("")

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")

    tree_data = build_blockchain_tree_data()
    BLOCKCHAIN_TREE_JSON.write_text(
        json.dumps(tree_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {BLOCKCHAIN_TREE_JSON}")


if __name__ == "__main__":
    main()
