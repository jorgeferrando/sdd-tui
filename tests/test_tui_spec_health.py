from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.text import Text
from textual.widgets import DataTable

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.spec_health import SpecHealthScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_spec_health_shows_changes(openspec_with_change: Path) -> None:
    """REQ-13: SpecHealthScreen renders one row per active change."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            assert isinstance(app.screen, SpecHealthScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 1


async def test_spec_health_zero_reqs_styled_yellow(openspec_with_change: Path) -> None:
    """REQ-14: a change with req_count == 0 has its name cell styled in yellow."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            table = app.screen.query_one(DataTable)
            row = table.get_row_at(0)
            name_cell = row[0]
            # Row should be styled yellow when req_count == 0
            assert isinstance(name_cell, Text)
            assert "yellow" in str(name_cell.style)


async def test_spec_health_esc_goes_back(openspec_with_change: Path) -> None:
    """REQ-15: pressing Esc pops back to EpicsView."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            assert isinstance(app.screen, SpecHealthScreen)
            await pilot.press("escape")
            assert not isinstance(app.screen, SpecHealthScreen)
            assert len(app.screen_stack) == 1

async def test_spec_health_enter_opens_change_detail(openspec_with_change: Path) -> None:
    """REQ-04: pressing Enter on a change row opens ChangeDetailScreen."""
    from sdd_tui.tui.change_detail import ChangeDetailScreen

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            assert isinstance(app.screen, SpecHealthScreen)
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)


async def test_spec_health_separator_no_drill_down(tmp_path: Path) -> None:
    """REQ-05: pressing Enter on the archived separator row does nothing."""
    from sdd_tui.tui.epics import EpicsView

    openspec = tmp_path / "openspec"
    archive = openspec / "changes" / "archive"
    (openspec / "specs").mkdir(parents=True)
    active = openspec / "changes" / "active-change"
    active.mkdir(parents=True)
    archived = archive / "2026-01-01-old-change"
    archived.mkdir(parents=True)

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec)
        async with app.run_test() as pilot:
            await pilot.press("a")   # show archived
            await pilot.press("h")   # open SpecHealthScreen
            assert isinstance(app.screen, SpecHealthScreen)
            table = app.screen.query_one(DataTable)
            # Move cursor to the separator row (row 1: active=0, separator=1)
            table.move_cursor(row=1)
            await pilot.press("enter")
            # Should still be on SpecHealthScreen (no drill-down for separator)
            assert isinstance(app.screen, SpecHealthScreen)
