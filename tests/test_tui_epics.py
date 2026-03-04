from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.epics import EpicsView
from sdd_tui.tui.spec_health import SpecHealthScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_epics_loads_changes(openspec_with_change: Path) -> None:
    """REQ-04: EpicsView renders one row per active change."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as _:
            table = app.query_one(DataTable)
            assert table.row_count == 1


async def test_epics_toggle_archived_shows_archived(
    openspec_with_archive: Path,
) -> None:
    """REQ-05: pressing 'a' adds archived changes to the table."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            rows_before = table.row_count
            await pilot.press("a")
            rows_after = table.row_count
            assert rows_after > rows_before


async def test_epics_toggle_archived_hides_again(openspec_with_archive: Path) -> None:
    """REQ-05: pressing 'a' twice returns to original row count."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            rows_before = table.row_count
            await pilot.press("a")
            await pilot.press("a")
            assert table.row_count == rows_before


async def test_epics_enter_navigates_to_change_detail(
    openspec_with_change: Path,
) -> None:
    """REQ-06: Enter on a change row pushes ChangeDetailScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)


async def test_epics_h_navigates_to_spec_health(openspec_with_change: Path) -> None:
    """REQ-07: pressing 'h' pushes SpecHealthScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            assert isinstance(app.screen, SpecHealthScreen)


async def test_epics_r_stays_on_epics(openspec_with_change: Path) -> None:
    """REQ-08: pressing 'r' reloads without navigating away."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("r")
            # Still on the default screen (EpicsView is a widget, not a Screen)
            assert app.query_one(EpicsView) is not None
            assert len(app.screen_stack) == 1


async def test_toggle_archived_label_changes(openspec_with_archive: Path) -> None:
    """REQ-01/02: pressing 'a' changes the binding label to 'Hide archived'."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            await pilot.press("a")
            labels = [b.description for b in epics.BINDINGS]
            assert "Hide archived" in labels
            assert "Show archived" not in labels


async def test_toggle_archived_label_reverts(openspec_with_archive: Path) -> None:
    """REQ-01/02: pressing 'a' twice reverts the binding label to 'Show archived'."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            await pilot.press("a")
            await pilot.press("a")
            labels = [b.description for b in epics.BINDINGS]
            assert "Show archived" in labels
            assert "Hide archived" not in labels


async def test_refresh_emits_notify(openspec_with_archive: Path) -> None:
    """REQ-04: pressing 'r' emits a notify with change count."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            with patch.object(epics, "notify") as mock_notify:
                await pilot.press("r")
                mock_notify.assert_called_once()
                message = mock_notify.call_args[0][0]
                assert "changes loaded" in message
                assert "archived" in message
