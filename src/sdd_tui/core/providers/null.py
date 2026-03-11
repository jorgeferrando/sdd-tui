from __future__ import annotations

from pathlib import Path

from sdd_tui.core.providers.protocol import (
    CiStatus,
    Issue,
    PrInfo,
    PrStatus,
    ReleaseInfo,
)


class NullGitHost:
    def get_pr_status(self, branch: str, cwd: Path) -> PrStatus | None:
        return None

    def get_ci_status(self, branch: str, cwd: Path) -> CiStatus | None:
        return None

    def get_releases(self, cwd: Path) -> list[ReleaseInfo]:
        return []

    def create_pr(self, title: str, body: str = "", cwd: Path = Path(".")) -> PrInfo:
        raise NotImplementedError

    def create_release(self, tag: str, name: str = "", cwd: Path = Path(".")) -> None:
        raise NotImplementedError


class NullIssueTracker:
    def get_issues(self, state: str = "open", cwd: Path = Path(".")) -> list[Issue]:
        return []

    def get_issue(self, issue_id: str, cwd: Path = Path(".")) -> Issue | None:
        return None

    def create_issue(self, title: str, body: str = "", cwd: Path = Path(".")) -> Issue:
        raise NotImplementedError

    def close_issue(self, issue_id: str, cwd: Path = Path(".")) -> None:
        raise NotImplementedError

    def assign_issue(self, issue_id: str, assignee: str, cwd: Path = Path(".")) -> None:
        raise NotImplementedError
