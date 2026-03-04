from pathlib import Path
from unittest.mock import patch, MagicMock

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.spec_evolution import SpecEvolutionScreen
from sdd_tui.tui.doc_viewer import DocumentViewerScreen
from textual.widgets import DataTable


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def _navigate_to_detail(pilot, app) -> None:
    """Helper: navigate from EpicsView to ChangeDetailScreen."""
    await pilot.press("enter")
    assert isinstance(app.screen, ChangeDetailScreen)


async def test_change_detail_shows_tasks(openspec_with_change: Path) -> None:
    """REQ-09: ChangeDetailScreen displays a DataTable with the change tasks."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            table = app.screen.query_one(DataTable)
            assert table.row_count >= 1


async def test_change_detail_esc_goes_back(openspec_with_change: Path) -> None:
    """REQ-10: pressing Esc pops back to EpicsView."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            await pilot.press("escape")
            assert not isinstance(app.screen, ChangeDetailScreen)
            assert len(app.screen_stack) == 1


async def test_change_detail_p_opens_doc_viewer(openspec_with_change: Path) -> None:
    """REQ-11: pressing 'p' pushes DocumentViewerScreen for proposal."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            await pilot.press("p")
            assert isinstance(app.screen, DocumentViewerScreen)


async def test_change_detail_e_opens_spec_evolution(openspec_with_change: Path) -> None:
    """REQ-12: pressing 'e' pushes SpecEvolutionScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            await pilot.press("e")
            assert isinstance(app.screen, SpecEvolutionScreen)
