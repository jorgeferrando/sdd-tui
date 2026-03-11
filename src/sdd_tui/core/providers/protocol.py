from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


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


@dataclass
class PrInfo:
    number: int
    url: str
    title: str


@dataclass
class Issue:
    number: int
    title: str
    state: str  # "open" | "closed"
    url: str
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    body: str = ""


@dataclass
class GitWorkflowConfig:
    issue_tracker: str = "none"  # "github" | "jira" | "trello" | "none"
    git_host: str = "none"  # "github" | "bitbucket" | "gitlab" | "none"
    branching_model: str = "github-flow"  # "github-flow" | "git-flow"
    change_prefix: str = "issue"
    changelog_format: str = "both"  # "labels" | "commit-prefix" | "both"


@dataclass
class ReleaseWorkflowConfig:
    enabled: bool = False
    versioning: str = "semver"          # "semver" | "calver" | "none"
    changelog_source: str = "openspec"  # "openspec" | "manual" | "none"
    homebrew_formula: str | None = None  # relative path to formula, or None


@runtime_checkable
class IssueTracker(Protocol):
    def get_issues(self, state: str = "open", cwd: Path = Path(".")) -> list[Issue]: ...
    def get_issue(self, issue_id: str, cwd: Path = Path(".")) -> Issue | None: ...
    def create_issue(self, title: str, body: str = "", cwd: Path = Path(".")) -> Issue: ...
    def close_issue(self, issue_id: str, cwd: Path = Path(".")) -> None: ...
    def assign_issue(self, issue_id: str, assignee: str, cwd: Path = Path(".")) -> None: ...


@runtime_checkable
class GitHost(Protocol):
    def get_pr_status(self, branch: str, cwd: Path) -> PrStatus | None: ...
    def get_ci_status(self, branch: str, cwd: Path) -> CiStatus | None: ...
    def get_releases(self, cwd: Path) -> list[ReleaseInfo]: ...
    def create_pr(self, title: str, body: str = "", cwd: Path = Path(".")) -> PrInfo: ...
    def create_release(self, tag: str, name: str = "", cwd: Path = Path(".")) -> None: ...


def make_git_host(cfg: GitWorkflowConfig) -> GitHost:
    if cfg.git_host == "github":
        from sdd_tui.core.providers.github import GitHubHost

        return GitHubHost()
    from sdd_tui.core.providers.null import NullGitHost

    return NullGitHost()


def make_issue_tracker(cfg: GitWorkflowConfig) -> IssueTracker:
    if cfg.issue_tracker == "github":
        from sdd_tui.core.providers.github import GitHubIssueTracker

        return GitHubIssueTracker()
    from sdd_tui.core.providers.null import NullIssueTracker

    return NullIssueTracker()
