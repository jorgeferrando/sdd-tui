from __future__ import annotations

import json
import subprocess
from pathlib import Path

from sdd_tui.core.providers.protocol import (
    CiStatus,
    Issue,
    PrInfo,
    PrStatus,
    ReleaseInfo,
)


class GitHubHost:
    def get_pr_status(self, branch: str, cwd: Path) -> PrStatus | None:
        """Return PR status for the given branch, or None on any failure."""
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

        pr = next((p for p in prs if branch in p.get("headRefName", "")), None)
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

    def get_ci_status(self, branch: str, cwd: Path) -> CiStatus | None:
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

    def get_releases(self, cwd: Path) -> list[ReleaseInfo]:
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

    def create_pr(self, title: str, body: str = "", cwd: Path = Path(".")) -> PrInfo:
        raise NotImplementedError

    def create_release(self, tag: str, name: str = "", cwd: Path = Path(".")) -> None:
        raise NotImplementedError


class GitHubIssueTracker:
    def get_issues(self, state: str = "open", cwd: Path = Path(".")) -> list[Issue]:
        """Return list of GitHub issues for the given state, or empty list on failure."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--state",
                    state,
                    "--json",
                    "number,title,body,labels,assignees,state,url",
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
            items = json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            return []

        return [
            Issue(
                number=i.get("number", 0),
                title=i.get("title", ""),
                state=i.get("state", ""),
                url=i.get("url", ""),
                labels=[lbl.get("name", "") for lbl in i.get("labels", [])],
                assignees=[a.get("login", "") for a in i.get("assignees", [])],
                body=i.get("body", "") or "",
            )
            for i in items
        ]

    def get_issue(self, issue_id: str, cwd: Path = Path(".")) -> Issue | None:
        """Return a single GitHub issue, or None on failure."""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    issue_id,
                    "--json",
                    "number,title,body,labels,assignees,state,url",
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
            i = json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            return None

        return Issue(
            number=i.get("number", 0),
            title=i.get("title", ""),
            state=i.get("state", ""),
            url=i.get("url", ""),
            labels=[lbl.get("name", "") for lbl in i.get("labels", [])],
            assignees=[a.get("login", "") for a in i.get("assignees", [])],
            body=i.get("body", "") or "",
        )

    def create_issue(self, title: str, body: str = "", cwd: Path = Path(".")) -> Issue:
        raise NotImplementedError

    def close_issue(self, issue_id: str, cwd: Path = Path(".")) -> None:
        raise NotImplementedError

    def assign_issue(self, issue_id: str, assignee: str, cwd: Path = Path(".")) -> None:
        raise NotImplementedError


# Module-level backward-compat functions — used by core/github.py shim
_default_host = GitHubHost()


def get_pr_status(branch: str, cwd: Path) -> PrStatus | None:
    return _default_host.get_pr_status(branch, cwd)


def get_ci_status(branch: str, cwd: Path) -> CiStatus | None:
    return _default_host.get_ci_status(branch, cwd)


def get_releases(cwd: Path) -> list[ReleaseInfo]:
    return _default_host.get_releases(cwd)
