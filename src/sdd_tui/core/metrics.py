from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

INACTIVE_THRESHOLD_DAYS = 7

_EARS_TAGS = frozenset({"[Event]", "[State]", "[Unwanted]", "[Optional]", "[Ubiquitous]"})
_REQ_PATTERN = re.compile(r"\*\*(REQ-\d+)\*\*")

_ARTIFACT_FILES = [
    ("proposal", "proposal.md"),
    ("spec", None),        # special: specs/*/spec.md
    ("research", "research.md"),
    ("design", "design.md"),
    ("tasks", "tasks.md"),
]


@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str] = field(default_factory=list)
    inactive_days: int | None = None


def parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics:
    req_count, ears_count = _count_reqs(change_path)
    artifacts = _get_artifacts(change_path)
    inactive_days = _get_inactive_days(change_path.name, repo_cwd)
    return ChangeMetrics(
        req_count=req_count,
        ears_count=ears_count,
        artifacts=artifacts,
        inactive_days=inactive_days,
    )


def _count_reqs(change_path: Path) -> tuple[int, int]:
    specs_dir = change_path / "specs"
    if not specs_dir.exists():
        return 0, 0

    seen: set[str] = set()
    ears: set[str] = set()
    for md_file in specs_dir.rglob("*.md"):
        for line in md_file.read_text(errors="replace").splitlines():
            match = _REQ_PATTERN.search(line)
            if match:
                req_id = match.group(1)
                seen.add(req_id)
                if any(tag in line for tag in _EARS_TAGS):
                    ears.add(req_id)
    return len(seen), len(ears)


def _get_artifacts(change_path: Path) -> list[str]:
    result = []
    for name, filename in _ARTIFACT_FILES:
        if filename is None:
            # spec: check specs/*/spec.md
            specs_dir = change_path / "specs"
            if specs_dir.exists() and any(
                (d / "spec.md").exists() for d in specs_dir.iterdir() if d.is_dir()
            ):
                result.append(name)
        else:
            if (change_path / filename).exists():
                result.append(name)
    return result


def _get_inactive_days(change_name: str, repo_cwd: Path) -> int | None:
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ad", "--date=short", "-1", "-F",
             f"--grep={change_name}"],
            cwd=repo_cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        commit_date = date.fromisoformat(result.stdout.strip())
        return (date.today() - commit_date).days
    except (FileNotFoundError, ValueError):
        return None
