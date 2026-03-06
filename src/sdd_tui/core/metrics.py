from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from sdd_tui.core.models import Change, PhaseState

INACTIVE_THRESHOLD_DAYS = 7

_EARS_TAGS = frozenset({"[Event]", "[State]", "[Unwanted]", "[Optional]", "[Ubiquitous]"})
_REQ_PATTERN = re.compile(r"\*\*(REQ-\d+)\*\*")
_TASK_LINE = re.compile(r"^\s*-\s+\[[ x]\]")
_COMPLEXITY_THRESHOLDS = [(41, "XL"), (25, "L"), (13, "M"), (6, "S"), (0, "XS")]

_ARTIFACT_FILES = [
    ("proposal", "proposal.md"),
    ("spec", None),  # special: specs/*/spec.md
    ("research", "research.md"),
    ("requirements", "requirements.md"),
    ("design", "design.md"),
    ("tasks", "tasks.md"),
]


@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str] = field(default_factory=list)
    inactive_days: int | None = None
    complexity_score: int = 0
    complexity_label: str = "XS"


def repair_hints(metrics: ChangeMetrics, change: Change) -> list[str]:
    """Return hints ordered by priority (most urgent first).

    The TUI displays hints[0]; the full list is available for testing.
    """
    hints: list[str] = []
    p = change.pipeline

    if p.propose == PhaseState.PENDING:
        hints.append(f"/sdd-propose {change.name}")
    if p.spec == PhaseState.PENDING:
        hints.append(f"/sdd-spec {change.name}")
        return hints  # REQ-RH-05: skip quality hints when spec is missing

    if p.design == PhaseState.PENDING:
        hints.append(f"/sdd-design {change.name}")
    if p.tasks == PhaseState.PENDING:
        hints.append(f"/sdd-tasks {change.name}")
    if p.apply == PhaseState.PENDING:
        hints.append(f"/sdd-apply {change.name}")
    if p.verify == PhaseState.PENDING:
        hints.append(f"/sdd-verify {change.name}")

    if metrics.req_count == 0:
        hints.append("add REQ-XX tags")
    elif metrics.ears_count < metrics.req_count:
        hints.append("add EARS tags")

    return hints if hints else ["✓"]


def parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics:
    req_count, ears_count = _count_reqs(change_path)
    artifacts = _get_artifacts(change_path)
    inactive_days = _get_inactive_days(change_path.name, repo_cwd)
    complexity_score, complexity_label = _get_complexity(change_path, repo_cwd)
    return ChangeMetrics(
        req_count=req_count,
        ears_count=ears_count,
        artifacts=artifacts,
        inactive_days=inactive_days,
        complexity_score=complexity_score,
        complexity_label=complexity_label,
    )


def _count_reqs(change_path: Path) -> tuple[int, int]:
    seen: set[str] = set()
    ears: set[str] = set()

    specs_dir = change_path / "specs"
    if specs_dir.exists():
        for md_file in specs_dir.rglob("*.md"):
            _scan_req_lines(md_file, seen, ears)

    req_file = change_path / "requirements.md"
    if req_file.exists():
        _scan_req_lines(req_file, seen, ears)

    return len(seen), len(ears)


def _scan_req_lines(path: Path, seen: set[str], ears: set[str]) -> None:
    for line in path.read_text(errors="replace").splitlines():
        match = _REQ_PATTERN.search(line)
        if match:
            req_id = match.group(1)
            seen.add(req_id)
            if any(tag in line for tag in _EARS_TAGS):
                ears.add(req_id)


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


def _get_complexity(change_path: Path, repo_cwd: Path) -> tuple[int, str]:
    task_count = _count_tasks(change_path)
    spec_lines = _count_spec_lines(change_path)
    git_files = _count_git_files(change_path.name, repo_cwd)
    score = task_count * 3 + spec_lines // 50 + git_files
    label = next(lbl for threshold, lbl in _COMPLEXITY_THRESHOLDS if score >= threshold)
    return score, label


def _count_tasks(change_path: Path) -> int:
    tasks_file = change_path / "tasks.md"
    if not tasks_file.exists():
        return 0
    return sum(
        1
        for line in tasks_file.read_text(errors="replace").splitlines()
        if _TASK_LINE.match(line)
    )


def _count_spec_lines(change_path: Path) -> int:
    specs_dir = change_path / "specs"
    if not specs_dir.exists():
        return 0
    total = 0
    for md in specs_dir.rglob("*.md"):
        total += len(md.read_text(errors="replace").splitlines())
    return total


def _count_git_files(change_name: str, repo_cwd: Path) -> int:
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--format=", "-F", f"--grep=[{change_name}]"],
            cwd=repo_cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return 0
        files = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        return len(files)
    except FileNotFoundError:
        return 0


def _get_inactive_days(change_name: str, repo_cwd: Path) -> int | None:
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--format=%ad",
                "--date=short",
                "-1",
                "-F",
                f"--grep={change_name}",
            ],
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
