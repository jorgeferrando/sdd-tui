from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import CommitInfo


def test_find_commit_returns_none_for_none_fragment(tmp_path: Path) -> None:
    assert GitReader().find_commit(None, tmp_path) is None


def test_find_commit_returns_commit_info(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "a1b2c3d Add pyproject.toml\n"

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().find_commit("[bootstrap] Add pyproject.toml", tmp_path)

    assert isinstance(result, CommitInfo)
    assert result.hash == "a1b2c3d"
    assert result.message == "Add pyproject.toml"


def test_find_commit_returns_none_when_not_found(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().find_commit("[bootstrap] Nonexistent commit", tmp_path)

    assert result is None


def test_get_diff_returns_none_for_none_hash(tmp_path: Path) -> None:
    assert GitReader().get_diff(None, tmp_path) is None


def test_get_diff_returns_output_on_success(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "commit a1b2c3d\nAuthor: ...\n\ndiff --git a/f b/f\n"

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_diff("a1b2c3d", tmp_path)

    assert result == "commit a1b2c3d\nAuthor: ...\n\ndiff --git a/f b/f\n"


def test_get_diff_returns_none_on_error(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 128

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_diff("badhash", tmp_path)

    assert result is None


def test_get_diff_returns_none_when_git_missing(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.git_reader.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        result = GitReader().get_diff("a1b2c3d", tmp_path)

    assert result is None


# ---------------------------------------------------------------------------
# get_branch
# ---------------------------------------------------------------------------


def test_get_branch_returns_branch_name(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "main\n"

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_branch(tmp_path)

    assert result == "main"


def test_get_branch_returns_none_on_nonzero(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 128

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_branch(tmp_path)

    assert result is None


def test_get_branch_returns_none_when_git_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.git_reader.subprocess.run", side_effect=FileNotFoundError):
        result = GitReader().get_branch(tmp_path)

    assert result is None


def test_get_branch_returns_none_on_empty_output(tmp_path: Path) -> None:
    """Detached HEAD returns empty string — treated as None."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "\n"

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_branch(tmp_path)

    assert result is None


# ---------------------------------------------------------------------------
# get_change_log
# ---------------------------------------------------------------------------


def test_get_change_log_returns_commits(tmp_path: Path) -> None:
    sep = "\x1f"
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = (
        f"a1b2c3d{sep}Jorge{sep}2 days ago{sep}[git-local-info] Add branch info\n"
        f"d4e5f6a{sep}Jorge{sep}5 days ago{sep}[git-local-info] Init\n"
    )

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_change_log("git-local-info", tmp_path)

    assert len(result) == 2
    assert result[0].hash == "a1b2c3d"
    assert result[0].author == "Jorge"
    assert result[0].date_relative == "2 days ago"
    assert result[0].message == "[git-local-info] Add branch info"
    assert result[1].hash == "d4e5f6a"


def test_get_change_log_returns_empty_when_no_match(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_change_log("nonexistent-change", tmp_path)

    assert result == []


def test_get_change_log_returns_empty_when_git_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.git_reader.subprocess.run", side_effect=FileNotFoundError):
        result = GitReader().get_change_log("my-change", tmp_path)

    assert result == []


# ---------------------------------------------------------------------------
# get_status_short
# ---------------------------------------------------------------------------


def test_get_status_short_returns_modified_files(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = " M src/foo.py\n?? tests/bar.py\n"

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_status_short(tmp_path)

    assert result == "M src/foo.py\n?? tests/bar.py"


def test_get_status_short_returns_none_when_clean(tmp_path: Path) -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""

    with patch("sdd_tui.core.git_reader.subprocess.run", return_value=mock_result):
        result = GitReader().get_status_short(tmp_path)

    assert result is None


def test_get_status_short_returns_none_when_git_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.git_reader.subprocess.run", side_effect=FileNotFoundError):
        result = GitReader().get_status_short(tmp_path)

    assert result is None
