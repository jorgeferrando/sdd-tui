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
