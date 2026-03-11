import pytest

from sdd_tui.core.providers.null import NullGitHost, NullIssueTracker


# --- NullGitHost ---


def test_null_git_host_get_pr_status_returns_none(tmp_path) -> None:
    assert NullGitHost().get_pr_status("branch", tmp_path) is None


def test_null_git_host_get_ci_status_returns_none(tmp_path) -> None:
    assert NullGitHost().get_ci_status("main", tmp_path) is None


def test_null_git_host_get_releases_returns_empty(tmp_path) -> None:
    assert NullGitHost().get_releases(tmp_path) == []


def test_null_git_host_create_pr_raises() -> None:
    with pytest.raises(NotImplementedError):
        NullGitHost().create_pr("title")


def test_null_git_host_create_release_raises() -> None:
    with pytest.raises(NotImplementedError):
        NullGitHost().create_release("v1.0")


# --- NullIssueTracker ---


def test_null_issue_tracker_get_issues_returns_empty(tmp_path) -> None:
    assert NullIssueTracker().get_issues(cwd=tmp_path) == []


def test_null_issue_tracker_get_issue_returns_none(tmp_path) -> None:
    assert NullIssueTracker().get_issue("42", cwd=tmp_path) is None


def test_null_issue_tracker_create_issue_raises() -> None:
    with pytest.raises(NotImplementedError):
        NullIssueTracker().create_issue("title")


def test_null_issue_tracker_close_issue_raises() -> None:
    with pytest.raises(NotImplementedError):
        NullIssueTracker().close_issue("42")


def test_null_issue_tracker_assign_issue_raises() -> None:
    with pytest.raises(NotImplementedError):
        NullIssueTracker().assign_issue("42", "alice")
