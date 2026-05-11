#!/usr/bin/env python3
import subprocess
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import re

VERBOSE = False
PATH_HISTORY_FALLBACKS = (
    ("docs/research/", "docs/process/"),
)


def log(msg: str):
    print(f"[INFO] {msg}", flush=True)


def debug(msg: str):
    if VERBOSE:
        print(f"[DEBUG] {msg}", flush=True)


def run_git(args: list, log_cmd: bool = True) -> str:
    cmd = ["git"] + args
    if log_cmd:
        debug("Running: " + " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print("[ERROR] Command failed:", " ".join(cmd))
        print(result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )

    return result.stdout.strip()


def run_git_optional(args: list) -> Optional[str]:
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def normalize_without_timeline(text: str) -> str:
    pattern = re.compile(
        r"<!-- timeline:start -->.*?<!-- timeline:end -->",
        re.DOTALL,
    )
    cleaned = pattern.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def get_file_at_commit(commit: str, path: str) -> Optional[str]:
    return run_git_optional(["show", f"{commit}:{path}"])


def is_timeline_only_change(commit: str, path: str) -> bool:
    current = get_file_at_commit(commit, path)
    if current is None:
        return False

    parent = run_git_optional(["rev-parse", f"{commit}^"])
    if parent is None:
        return False

    parent_text = get_file_at_commit(parent, path)
    if parent_text is None:
        return False

    return normalize_without_timeline(current) == normalize_without_timeline(parent_text)


def get_repo_https_url() -> Optional[str]:
    try:
        url = run_git(["config", "--get", "remote.origin.url"]).strip()
    except subprocess.CalledProcessError:
        return None

    if url.startswith("git@github.com:"):
        path = url[len("git@github.com:"):]
        if path.endswith(".git"):
            path = path[:-4]
        return f"https://github.com/{path}"

    if url.startswith("https://github.com/"):
        path = url[len("https://github.com/"):]
        if path.endswith(".git"):
            path = path[:-4]
        return f"https://github.com/{path}"

    return None


def get_repo_file_path(path: str) -> str:
    debug(f"Resolving file path via git: {path}")
    try:
        out = run_git(["ls-files", "--full-name", path], log_cmd=False)
    except subprocess.CalledProcessError:
        raise SystemExit(f"[ERROR] {path!r} is not tracked by git")

    if not out:
        raise SystemExit(f"[ERROR] {path!r} is not tracked by git")

    resolved = out.splitlines()[0]
    debug(f"Resolved path inside repo: {resolved}")
    return resolved


def get_history_file_path(path: str) -> Optional[str]:
    try:
        return get_repo_file_path(path)
    except SystemExit:
        pass

    for current_prefix, historical_prefix in PATH_HISTORY_FALLBACKS:
        if not path.startswith(current_prefix):
            continue

        candidate = historical_prefix + path[len(current_prefix):]
        if run_git_optional(["cat-file", "-e", f"HEAD:{candidate}"]) is None:
            continue

        debug(f"Using historical path for untracked rename: {path} -> {candidate}")
        return candidate

    print(f"[WARN] {path!r} is not tracked by git; skipping timeline generation")
    return None


def get_file_commits(path: str) -> List[Tuple[str, str, str, str]]:
    debug(f"Collecting commit history for: {path}")

    log_output = run_git([
        "log",
        "--follow",
        "--format=%H%x09%ad%x09%s",
        "--date=short",
        "--name-only",
        "--",
        path,
    ])

    if not log_output:
        debug("No history found.")
        return []

    commits: List[Tuple[str, str, str, str]] = []
    current: Optional[Dict[str, str]] = None
    for line in log_output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        # Detect commit line
        if len(parts) == 3 and len(parts[0]) >= 7 and all(c in "0123456789abcdef" for c in parts[0].lower()):
            if current:
                commits.append((current["commit"], current["date"], current["subject"], current.get("path", path)))
            current = {"commit": parts[0], "date": parts[1], "subject": parts[2]}
            continue

        # If we are in a commit block and we see a path, record the first one
        if current and "path" not in current:
            current["path"] = line.strip()

    if current:
        commits.append((current["commit"], current["date"], current["subject"], current.get("path", path)))

    commits.reverse()
    debug(f"Found {len(commits)} commits.")
    return commits


def filter_timeline_commits(
    commits: List[Tuple[str, str, str, str]]
) -> List[Tuple[str, str, str, str]]:
    filtered: List[Tuple[str, str, str, str]] = []
    for commit, date, subject, path_at_commit in commits:
        if is_timeline_only_change(commit, path_at_commit):
            continue
        filtered.append((commit, date, subject, path_at_commit))
    return filtered


def build_markdown_history(
    repo_url: str,
    file_path: str,
    commits: List[Tuple[str, str, str, str]],
) -> str:
    debug("Generating markdown history...")
    entries = []

    # newest first
    for commit, date, subject, path_at_commit in reversed(commits):
        blob_url = f"{repo_url}/blob/{commit}/{path_at_commit}"
        entries.append((date, commit, subject, blob_url))

    lines: List[str] = []
    lines.append("## Timeline\n")

    for date, commit, subject, blob_url in entries:
        lines.append(f"- **{date}** — [`{commit[:7]}`]({blob_url}) — {subject}")

    return "\n".join(lines).rstrip() + "\n"


def find_metadata_table_end(lines: List[str]) -> Optional[int]:
    header_idx = None
    for idx, line in enumerate(lines[:80]):
        if line.strip() == "| Field | Value |":
            header_idx = idx
            break
    if header_idx is None:
        return None

    if header_idx + 1 >= len(lines):
        return None

    if not lines[header_idx + 1].strip().startswith("|"):
        return None

    end_idx = header_idx + 2
    while end_idx < len(lines) and lines[end_idx].strip().startswith("|"):
        end_idx += 1

    return end_idx


def inject_timeline(file_path: Path, timeline_md: str) -> bool:
    """
    Insert or replace a timeline block near the top of the file.
    Returns True if the file was modified.
    """
    content = file_path.read_text(encoding="utf-8")
    start_marker = "<!-- timeline:start -->"
    end_marker = "<!-- timeline:end -->"
    block = (
        f"{start_marker}\n\n"
        f"{timeline_md.strip()}\n\n"
        f"{end_marker}"
    )

    if start_marker in content and end_marker in content:
        pattern = re.compile(
            re.escape(start_marker) + r".*?" + re.escape(end_marker),
            re.DOTALL,
        )
        new_content, count = pattern.subn(block, content, count=1)
        new_content = re.sub(
            re.escape(end_marker) + r"\n{3,}",
            end_marker + "\n\n",
            new_content,
        )
        if count and new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        return False

    lines = content.splitlines()
    insert_pos = 0
    table_end = find_metadata_table_end(lines)
    if table_end is not None:
        insert_pos = len("\n".join(lines[:table_end]))
    else:
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                insert_pos = len("\n".join(lines[: idx + 1]))
                break

    new_content = content[:insert_pos] + "\n\n" + block + "\n\n" + content[insert_pos:]
    new_content = re.sub(
        re.escape(end_marker) + r"\n{3,}",
        end_marker + "\n\n",
        new_content,
    )
    if new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def is_rfc_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False

    if "# " not in text:
        return False

    if "| Field | Value |" not in text:
        return False

    return True


def find_rfc_files(root: Path) -> List[Path]:
    candidates: List[Path] = []
    for path in root.rglob("*.md"):
        if path.name in {"README.md", "SUMMARY.md", "template.md"}:
            continue
        if is_rfc_file(path):
            candidates.append(path)
    return sorted(candidates)


def main():
    log("Starting history generation")

    repo_url = get_repo_https_url()
    if not repo_url:
        raise SystemExit("[ERROR] Could not determine GitHub repo URL")

    log(f"Repo URL: {repo_url}")

    root = Path("docs")
    files = find_rfc_files(root)
    if not files:
        raise SystemExit(f"[ERROR] No LIPs found under {root}")

    updated = 0
    for file_path in files:
        repo_file_path = get_history_file_path(str(file_path))
        if repo_file_path is None:
            continue

        commits = get_file_commits(repo_file_path)
        commits = filter_timeline_commits(commits)
        if not commits:
            debug(f"[WARN] No history found for {repo_file_path}")
            continue

        markdown = build_markdown_history(
            repo_url=repo_url,
            file_path=repo_file_path,
            commits=commits,
        )

        modified = inject_timeline(file_path, markdown)
        if modified:
            updated += 1
            debug(f"Timeline injected into {file_path}")

    log(f"Timelines updated in {updated} files")


if __name__ == "__main__":
    main()
