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
