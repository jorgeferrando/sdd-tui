from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen, DiffPanel
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


async def test_diff_panel_shows_loading_placeholder(openspec_with_change: Path) -> None:
    """REQ-01: DiffPanel shows loading placeholder immediately when a row is highlighted."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await _navigate_to_detail(pilot, app)
            screen = app.screen
            assert isinstance(screen, ChangeDetailScreen)
            diff_panel = screen.query_one(DiffPanel)
            shown: list[str] = []
            original_show_message = diff_panel.show_message
            diff_panel.show_message = lambda t: shown.append(t)  # type: ignore[method-assign]
            # Patch worker to no-op so panel stays at placeholder state
            with patch.object(screen, "_load_diff_worker"):
                await pilot.press("down")
                await pilot.pause()
            diff_panel.show_message = original_show_message  # type: ignore[method-assign]
            assert any("Loading diff" in s for s in shown)


async def test_diff_panel_updates_after_worker_completes(openspec_with_change: Path) -> None:
    """REQ-02/03: DiffPanel show_diff is called after worker completes for a pending task."""
    app_git = _git_mock()
    worker_git = MagicMock()
    worker_git.return_value.get_working_diff.return_value = "diff --git a/f b/f\n+added line"
    with patch("sdd_tui.tui.app.GitReader", app_git):
        with patch("sdd_tui.tui.change_detail.GitReader", worker_git):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await _navigate_to_detail(pilot, app)
                screen = app.screen
                assert isinstance(screen, ChangeDetailScreen)
                diffs_shown: list[str] = []
                diff_panel = screen.query_one(DiffPanel)
                diff_panel.show_diff = lambda t: diffs_shown.append(t)  # type: ignore[method-assign]
                await pilot.press("down")
                await pilot.pause(0.2)
                await pilot.pause()
                assert len(diffs_shown) == 1
                assert "diff --git" in diffs_shown[0]


async def test_diff_panel_reflects_last_navigation_after_rapid_moves(
    openspec_with_change: Path,
) -> None:
    """REQ-04/05: After rapid navigation, show_diff is called for the final selected task."""
    app_git = _git_mock()
    worker_git = MagicMock()
    worker_git.return_value.get_working_diff.return_value = "diff --git a/f b/f\n+added line"
    with patch("sdd_tui.tui.app.GitReader", app_git):
        with patch("sdd_tui.tui.change_detail.GitReader", worker_git):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await _navigate_to_detail(pilot, app)
                screen = app.screen
                assert isinstance(screen, ChangeDetailScreen)
                diffs_shown: list[str] = []
                diff_panel = screen.query_one(DiffPanel)
                diff_panel.show_diff = lambda t: diffs_shown.append(t)  # type: ignore[method-assign]
                # Navigate quickly: down → up → down (exclusive=True cancels intermediates)
                await pilot.press("down")
                await pilot.press("up")
                await pilot.press("down")
                await pilot.pause(0.2)
                await pilot.pause()
                # At least one diff was shown (the last worker completed)
                assert len(diffs_shown) >= 1
                assert all("diff --git" in d for d in diffs_shown)


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
