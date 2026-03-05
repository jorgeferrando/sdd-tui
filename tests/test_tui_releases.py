from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.core.github import ReleaseInfo
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.releases import ReleasesScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_releases_screen_mounts(openspec_with_change: Path) -> None:
    """REQ-RL01: L from EpicsView opens ReleasesScreen."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.releases.get_releases", return_value=[]),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("l")
            assert isinstance(app.screen, ReleasesScreen)


async def test_releases_screen_no_releases_message(openspec_with_change: Path) -> None:
    """REQ-RL04: no releases → 'No releases found' in table."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.releases.get_releases", return_value=[]),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("l")
            assert isinstance(app.screen, ReleasesScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 1
            row = table.get_row_at(0)
            assert any("No releases found" in str(cell) for cell in row)


async def test_releases_screen_shows_releases(openspec_with_change: Path) -> None:
    """REQ-RL02/RL03/RL06: releases shown with tag, name, date, latest marker."""
    releases = [
        ReleaseInfo(
            tag_name="v1.1.0",
            name="Release 1.1",
            published_at="2026-02-01T00:00:00Z",
            is_latest=True,
        ),
        ReleaseInfo(
            tag_name="v1.0.0",
            name="Release 1.0",
            published_at="2026-01-01T00:00:00Z",
            is_latest=False,
        ),
    ]
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.releases.get_releases", return_value=releases),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("l")
            assert isinstance(app.screen, ReleasesScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 2
            row0 = table.get_row_at(0)
            assert any("v1.1.0" in str(cell) for cell in row0)
            assert any("✓" in str(cell) for cell in row0)
            row1 = table.get_row_at(1)
            assert any("·" in str(cell) for cell in row1)


async def test_releases_screen_esc_returns(openspec_with_change: Path) -> None:
    """REQ-RL05: Esc from ReleasesScreen returns to EpicsView."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.releases.get_releases", return_value=[]),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("l")
            assert isinstance(app.screen, ReleasesScreen)
            await pilot.press("escape")
            assert not isinstance(app.screen, ReleasesScreen)
            assert len(app.screen_stack) == 1
