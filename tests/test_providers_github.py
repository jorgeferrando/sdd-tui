from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.core.providers.github import (
    GitHubHost,
    GitHubIssueTracker,
    get_ci_status,
    get_pr_status,
    get_releases,
)
from sdd_tui.core.providers.protocol import CiStatus, Issue, PrStatus, ReleaseInfo


def _mock_result(returncode: int = 0, stdout: str = "[]") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    return m


# --- GitHubHost.get_pr_status ---


def test_get_pr_status_returns_none_when_gh_missing(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError
    ):
        assert host.get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert host.get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_when_no_pr_found(tmp_path: Path) -> None:
    payload = '[{"number": 1, "headRefName": "other-branch", "state": "OPEN", "reviews": []}]'
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        assert host.get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_invalid_json(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="not-json"),
    ):
        assert host.get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_pr_status_on_match(tmp_path: Path) -> None:
    payload = '[{"number": 42, "headRefName": "my-change", "state": "OPEN", "reviews": []}]'
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_pr_status("my-change", tmp_path)

    assert isinstance(result, PrStatus)
    assert result.number == 42
    assert result.state == "OPEN"
    assert result.approvals == 0
    assert result.changes_requested == 0


def test_get_pr_status_counts_approvals_and_changes_requested(tmp_path: Path) -> None:
    payload = (
        '[{"number": 7, "headRefName": "my-change", "state": "OPEN", "reviews": ['
        '{"state": "APPROVED"}, {"state": "APPROVED"}, {"state": "CHANGES_REQUESTED"}'
        "]}]"
    )
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_pr_status("my-change", tmp_path)

    assert result is not None
    assert result.approvals == 2
    assert result.changes_requested == 1


def test_get_pr_status_matches_substring_in_branch_name(tmp_path: Path) -> None:
    payload = (
        '[{"number": 5, "headRefName": "feature/pr-status", "state": "MERGED", "reviews": []}]'
    )
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_pr_status("pr-status", tmp_path)

    assert result is not None
    assert result.number == 5
    assert result.state == "MERGED"


# --- GitHubHost.get_ci_status ---


def test_get_ci_status_returns_none_when_gh_missing(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError
    ):
        assert host.get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert host.get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_empty_list(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="[]"),
    ):
        assert host.get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_invalid_json(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="bad"),
    ):
        assert host.get_ci_status("main", tmp_path) is None


def test_get_ci_status_success(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "completed", "conclusion": "success"}]'
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_ci_status("main", tmp_path)

    assert isinstance(result, CiStatus)
    assert result.workflow == "CI"
    assert result.status == "completed"
    assert result.conclusion == "success"


def test_get_ci_status_failure(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "completed", "conclusion": "failure"}]'
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_ci_status("main", tmp_path)

    assert result is not None
    assert result.conclusion == "failure"


def test_get_ci_status_in_progress(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "in_progress", "conclusion": null}]'
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_ci_status("main", tmp_path)

    assert result is not None
    assert result.status == "in_progress"
    assert result.conclusion is None


# --- GitHubHost.get_releases ---


def test_get_releases_returns_empty_when_gh_missing(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError
    ):
        assert host.get_releases(tmp_path) == []


def test_get_releases_returns_empty_on_nonzero_exit(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert host.get_releases(tmp_path) == []


def test_get_releases_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="bad"),
    ):
        assert host.get_releases(tmp_path) == []


def test_get_releases_returns_list(tmp_path: Path) -> None:
    payload = (
        '[{"tagName": "v1.0.0", "name": "Release 1.0", '
        '"publishedAt": "2026-01-01T00:00:00Z", "isLatest": true}]'
    )
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_releases(tmp_path)

    assert len(result) == 1
    assert isinstance(result[0], ReleaseInfo)
    assert result[0].tag_name == "v1.0.0"
    assert result[0].name == "Release 1.0"
    assert result[0].is_latest is True


def test_get_releases_returns_multiple(tmp_path: Path) -> None:
    payload = (
        '[{"tagName": "v1.1.0", "name": "R1.1", "publishedAt": "2026-02-01T00:00:00Z",'
        ' "isLatest": true},'
        ' {"tagName": "v1.0.0", "name": "R1.0", "publishedAt": "2026-01-01T00:00:00Z",'
        ' "isLatest": false}]'
    )
    host = GitHubHost()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = host.get_releases(tmp_path)

    assert len(result) == 2
    assert result[0].tag_name == "v1.1.0"
    assert result[1].is_latest is False


# --- Module-level compat functions ---


def test_compat_get_pr_status_delegates_to_default_host(tmp_path: Path) -> None:
    payload = '[{"number": 1, "headRefName": "branch", "state": "OPEN", "reviews": []}]'
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = get_pr_status("branch", tmp_path)
    assert result is not None
    assert result.number == 1


def test_compat_get_ci_status_delegates_to_default_host(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "completed", "conclusion": "success"}]'
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = get_ci_status("main", tmp_path)
    assert result is not None
    assert result.workflow == "CI"


def test_compat_get_releases_delegates_to_default_host(tmp_path: Path) -> None:
    payload = '[{"tagName": "v1.0.0", "name": "R", "publishedAt": "2026-01-01", "isLatest": true}]'
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = get_releases(tmp_path)
    assert len(result) == 1


# --- GitHubIssueTracker.get_issues ---


def test_get_issues_returns_empty_when_gh_missing(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError
    ):
        assert tracker.get_issues(cwd=tmp_path) == []


def test_get_issues_returns_empty_on_nonzero_exit(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert tracker.get_issues(cwd=tmp_path) == []


def test_get_issues_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="bad"),
    ):
        assert tracker.get_issues(cwd=tmp_path) == []


def test_get_issues_returns_list(tmp_path: Path) -> None:
    payload = (
        '[{"number": 1, "title": "Bug", "state": "open", "url": "http://example.com/1",'
        ' "labels": [{"name": "bug"}], "assignees": [{"login": "alice"}], "body": "desc"}]'
    )
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = tracker.get_issues(cwd=tmp_path)

    assert len(result) == 1
    assert isinstance(result[0], Issue)
    assert result[0].number == 1
    assert result[0].title == "Bug"
    assert result[0].state == "open"
    assert result[0].labels == ["bug"]
    assert result[0].assignees == ["alice"]
    assert result[0].body == "desc"


def test_get_issues_closed_state_passed_to_gh(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="[]"),
    ) as mock_run:
        tracker.get_issues(state="closed", cwd=tmp_path)
    call_args = mock_run.call_args[0][0]
    assert "closed" in call_args


# --- GitHubIssueTracker.get_issue ---


def test_get_issue_returns_none_when_gh_missing(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError
    ):
        assert tracker.get_issue("42", cwd=tmp_path) is None


def test_get_issue_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert tracker.get_issue("42", cwd=tmp_path) is None


def test_get_issue_returns_issue(tmp_path: Path) -> None:
    payload = (
        '{"number": 42, "title": "Fix it", "state": "open",'
        ' "url": "http://example.com/42", "labels": [], "assignees": [], "body": ""}'
    )
    tracker = GitHubIssueTracker()
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout=payload),
    ):
        result = tracker.get_issue("42", cwd=tmp_path)

    assert result is not None
    assert result.number == 42
    assert result.title == "Fix it"


# --- NotImplementedError methods ---


def test_git_host_create_pr_raises() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        GitHubHost().create_pr("title")


def test_git_host_create_release_raises() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        GitHubHost().create_release("v1.0")


def test_issue_tracker_create_issue_raises() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        GitHubIssueTracker().create_issue("title")


def test_issue_tracker_close_issue_raises() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        GitHubIssueTracker().close_issue("42")


def test_issue_tracker_assign_issue_raises() -> None:
    import pytest

    with pytest.raises(NotImplementedError):
        GitHubIssueTracker().assign_issue("42", "alice")
