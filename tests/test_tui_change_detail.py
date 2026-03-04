from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.doc_viewer import DocumentViewerScreen
from sdd_tui.tui.spec_evolution import SpecEvolutionScreen


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


async def test_open_existing_doc_notifies(openspec_with_change: Path) -> None:
    """REQ-06: opening an existing document triggers notify 'Opening {label}'."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            screen = app.screen
            assert isinstance(screen, ChangeDetailScreen)
            with patch.object(screen, "notify") as mock_notify:
                await pilot.press("p")  # proposal.md exists in fixture
                mock_notify.assert_called_once_with("Opening proposal")


async def test_open_missing_doc_no_notify_in_detail(tmp_path: Path) -> None:
    """REQ-06: opening a missing document does NOT notify in ChangeDetailScreen."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    change = openspec / "changes" / "my-change"
    change.mkdir()
    (change / "tasks.md").write_text("- [ ] **T01** Pending\n")
    # proposal.md intentionally absent

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            screen = app.screen
            assert isinstance(screen, ChangeDetailScreen)
            with patch.object(screen, "notify") as mock_notify:
                await pilot.press("p")  # proposal.md missing
                mock_notify.assert_not_called()
