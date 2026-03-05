from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.core.models import Change, CommitInfo
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.git_log import GitLogScreen


def _git_mock(branch: str = "main", commits: list | None = None) -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    m.return_value.get_branch.return_value = branch
    m.return_value.get_change_log.return_value = commits or []
    return m


def _change(openspec: Path) -> Change:
    change_dir = openspec / "changes" / "my-change"
    change_dir.mkdir(parents=True, exist_ok=True)
    (change_dir / "proposal.md").write_text("# proposal")
    return Change(name="my-change", path=change_dir, project_path=openspec.parent)


async def test_git_log_screen_mounts(openspec_with_change: Path) -> None:
    """GitLogScreen mounts without errors when no commits exist."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock(commits=[])):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)
            await pilot.press("g")
            assert isinstance(app.screen, GitLogScreen)


async def test_git_log_screen_no_commits_message(openspec_with_change: Path) -> None:
    """REQ-GL06: no commits → shows 'No commits found' message in table."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock(commits=[])),
        patch("sdd_tui.tui.git_log.GitReader") as mock_log_reader,
    ):
        mock_log_reader.return_value.get_change_log.return_value = []
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("g")
            assert isinstance(app.screen, GitLogScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 1
            row = table.get_row_at(0)
            assert any("No commits found" in str(cell) for cell in row)


async def test_git_log_screen_shows_commits(openspec_with_change: Path) -> None:
    """REQ-GL02/GL03: commits are shown with hash, author, date, message."""
    commits = [
        CommitInfo(
            hash="a1b2c3d",
            message="[my-change] Add feature",
            author="Jorge",
            date_relative="2 days ago",
        ),
        CommitInfo(
            hash="d4e5f6a",
            message="[my-change] Init",
            author="Jorge",
            date_relative="5 days ago",
        ),
    ]
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock(commits=commits)),
        patch("sdd_tui.tui.git_log.GitReader") as mock_log_reader,
    ):
        mock_log_reader.return_value.get_change_log.return_value = commits
        mock_log_reader.return_value.get_diff.return_value = "diff --git a/f b/f\n"
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("g")
            assert isinstance(app.screen, GitLogScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 2


async def test_git_log_screen_esc_returns_to_detail(openspec_with_change: Path) -> None:
    """REQ-GL07: Esc from GitLogScreen returns to ChangeDetailScreen."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock(commits=[])),
        patch("sdd_tui.tui.git_log.GitReader") as mock_log_reader,
    ):
        mock_log_reader.return_value.get_change_log.return_value = []
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("g")
            assert isinstance(app.screen, GitLogScreen)
            await pilot.press("escape")
            assert isinstance(app.screen, ChangeDetailScreen)
