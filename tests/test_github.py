from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.core.github import (
    CiStatus,
    PrStatus,
    ReleaseInfo,
    get_ci_status,
    get_pr_status,
    get_releases,
)


def _mock_result(returncode: int = 0, stdout: str = "[]") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    return m


def test_get_pr_status_returns_none_when_gh_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(returncode=1)):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_when_no_pr_found(tmp_path: Path) -> None:
    payload = '[{"number": 1, "headRefName": "other-branch", "state": "OPEN", "reviews": []}]'
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_invalid_json(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.providers.github.subprocess.run",
        return_value=_mock_result(stdout="not-json"),
    ):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_pr_status_on_match(tmp_path: Path) -> None:
    payload = '[{"number": 42, "headRefName": "my-change", "state": "OPEN", "reviews": []}]'
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_pr_status("my-change", tmp_path)

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
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_pr_status("my-change", tmp_path)

    assert result is not None
    assert result.approvals == 2
    assert result.changes_requested == 1


def test_get_pr_status_matches_substring_in_branch_name(tmp_path: Path) -> None:
    payload = (
        '[{"number": 5, "headRefName": "feature/pr-status", "state": "MERGED", "reviews": []}]'
    )
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_pr_status("pr-status", tmp_path)

    assert result is not None
    assert result.number == 5
    assert result.state == "MERGED"


# --- get_ci_status ---


def test_get_ci_status_returns_none_when_gh_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError):
        assert get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(returncode=1)):
        assert get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_empty_list(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout="[]")):
        assert get_ci_status("main", tmp_path) is None


def test_get_ci_status_returns_none_on_invalid_json(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout="bad")):
        assert get_ci_status("main", tmp_path) is None


def test_get_ci_status_success(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "completed", "conclusion": "success"}]'
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_ci_status("main", tmp_path)

    assert isinstance(result, CiStatus)
    assert result.workflow == "CI"
    assert result.status == "completed"
    assert result.conclusion == "success"


def test_get_ci_status_failure(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "completed", "conclusion": "failure"}]'
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_ci_status("main", tmp_path)

    assert result is not None
    assert result.conclusion == "failure"


def test_get_ci_status_in_progress(tmp_path: Path) -> None:
    payload = '[{"workflowName": "CI", "status": "in_progress", "conclusion": null}]'
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_ci_status("main", tmp_path)

    assert result is not None
    assert result.status == "in_progress"
    assert result.conclusion is None


# --- get_releases ---


def test_get_releases_returns_empty_when_gh_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", side_effect=FileNotFoundError):
        assert get_releases(tmp_path) == []


def test_get_releases_returns_empty_on_nonzero_exit(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(returncode=1)):
        assert get_releases(tmp_path) == []


def test_get_releases_returns_empty_on_invalid_json(tmp_path: Path) -> None:
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout="bad")):
        assert get_releases(tmp_path) == []


def test_get_releases_returns_list(tmp_path: Path) -> None:
    payload = (
        '[{"tagName": "v1.0.0", "name": "Release 1.0", '
        '"publishedAt": "2026-01-01T00:00:00Z", "isLatest": true}]'
    )
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_releases(tmp_path)

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
    with patch("sdd_tui.core.providers.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_releases(tmp_path)

    assert len(result) == 2
    assert result[0].tag_name == "v1.1.0"
    assert result[1].is_latest is False
