from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.core.github import PrStatus, get_pr_status


def _mock_result(returncode: int = 0, stdout: str = "[]") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    return m


def test_get_pr_status_returns_none_when_gh_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.github.subprocess.run", side_effect=FileNotFoundError):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    with patch("sdd_tui.core.github.subprocess.run", return_value=_mock_result(returncode=1)):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_when_no_pr_found(tmp_path: Path) -> None:
    payload = '[{"number": 1, "headRefName": "other-branch", "state": "OPEN", "reviews": []}]'
    with patch("sdd_tui.core.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_none_on_invalid_json(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.github.subprocess.run",
        return_value=_mock_result(stdout="not-json"),
    ):
        assert get_pr_status("my-change", tmp_path) is None


def test_get_pr_status_returns_pr_status_on_match(tmp_path: Path) -> None:
    payload = '[{"number": 42, "headRefName": "my-change", "state": "OPEN", "reviews": []}]'
    with patch("sdd_tui.core.github.subprocess.run", return_value=_mock_result(stdout=payload)):
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
    with patch("sdd_tui.core.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_pr_status("my-change", tmp_path)

    assert result is not None
    assert result.approvals == 2
    assert result.changes_requested == 1


def test_get_pr_status_matches_substring_in_branch_name(tmp_path: Path) -> None:
    payload = (
        '[{"number": 5, "headRefName": "feature/pr-status", "state": "MERGED", "reviews": []}]'
    )
    with patch("sdd_tui.core.github.subprocess.run", return_value=_mock_result(stdout=payload)):
        result = get_pr_status("pr-status", tmp_path)

    assert result is not None
    assert result.number == 5
    assert result.state == "MERGED"
