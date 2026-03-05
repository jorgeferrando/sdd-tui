from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PrStatus:
    number: int
    state: str  # "OPEN" | "MERGED" | "CLOSED"
    approvals: int
    changes_requested: int


@dataclass
class CiStatus:
    workflow: str
    status: str  # "queued" | "in_progress" | "completed"
    conclusion: str | None  # "success" | "failure" | "cancelled" | None


@dataclass
class ReleaseInfo:
    tag_name: str
    name: str
    published_at: str  # ISO 8601
    is_latest: bool


def get_ci_status(branch: str, cwd: Path) -> CiStatus | None:
    """Return CI status for the latest workflow run on branch, or None on any failure."""
    try:
        result = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--branch",
                branch,
                "--limit",
                "1",
                "--json",
                "status,conclusion,workflowName",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None

    if result.returncode != 0:
        return None

    try:
        runs = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return None

    if not runs:
        return None

    run = runs[0]
    return CiStatus(
        workflow=run.get("workflowName", ""),
        status=run.get("status", ""),
        conclusion=run.get("conclusion") or None,
    )


def get_releases(cwd: Path) -> list[ReleaseInfo]:
    """Return list of GitHub releases, or empty list on any failure."""
    try:
        result = subprocess.run(
            [
                "gh",
                "release",
                "list",
                "--json",
                "tagName,name,publishedAt,isLatest",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []

    if result.returncode != 0:
        return []

    try:
        releases = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return []

    return [
        ReleaseInfo(
            tag_name=r.get("tagName", ""),
            name=r.get("name", ""),
            published_at=r.get("publishedAt", ""),
            is_latest=bool(r.get("isLatest", False)),
        )
        for r in releases
    ]


def get_pr_status(change_name: str, cwd: Path) -> PrStatus | None:
    """Return PR status for the given change name, or None on any failure."""
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--json",
                "number,headRefName,state,reviews",
                "--state",
                "all",
                "--limit",
                "20",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None

    if result.returncode != 0:
        return None

    try:
        prs = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return None

    pr = next((p for p in prs if change_name in p.get("headRefName", "")), None)
    if pr is None:
        return None

    reviews = pr.get("reviews", [])
    approvals = sum(1 for r in reviews if r.get("state") == "APPROVED")
    changes_requested = sum(1 for r in reviews if r.get("state") == "CHANGES_REQUESTED")

    return PrStatus(
        number=pr["number"],
        state=pr["state"],
        approvals=approvals,
        changes_requested=changes_requested,
    )
