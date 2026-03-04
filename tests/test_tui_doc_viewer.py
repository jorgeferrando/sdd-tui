from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import Static

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.doc_viewer import DocumentViewerScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_doc_viewer_renders_content(openspec_with_change: Path) -> None:
    """REQ-19: DocumentViewerScreen renders the file content when it exists."""
    proposal_path = openspec_with_change / "changes" / "my-change" / "proposal.md"
    assert proposal_path.exists()

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")  # navigate to ChangeDetailScreen
            await pilot.press("p")  # open proposal via DocumentViewerScreen
            assert isinstance(app.screen, DocumentViewerScreen)
            content_widget = app.screen.query_one("#doc-content", Static)
            # Content should be a Markdown renderable, not the "not found" message
            rendered = str(content_widget.render())
            assert "not found" not in rendered


async def test_doc_viewer_not_found(tmp_path: Path) -> None:
    """REQ-20: DocumentViewerScreen shows a 'not found' message for missing files."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    change = openspec / "changes" / "my-change"
    change.mkdir()
    # proposal.md does NOT exist — pressing 'p' will open a not-found viewer
    (change / "tasks.md").write_text("- [ ] **T01** Pending\n")

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("p")
            assert isinstance(app.screen, DocumentViewerScreen)
            content_widget = app.screen.query_one("#doc-content", Static)
            assert "not found" in str(content_widget.render())


async def test_doc_viewer_esc_goes_back(openspec_with_change: Path) -> None:
    """REQ-21: pressing Esc pops back to the previous screen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("p")
            assert isinstance(app.screen, DocumentViewerScreen)
            await pilot.press("escape")
            assert isinstance(app.screen, ChangeDetailScreen)


async def test_doc_viewer_missing_emits_warning(tmp_path: Path) -> None:
    """REQ-07: DocumentViewerScreen calls app.notify with severity=warning for missing files."""
    from sdd_tui.tui.doc_viewer import DocumentViewerScreen

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
            with patch.object(app, "notify") as mock_notify:
                await pilot.press("p")  # opens DocumentViewerScreen for missing file
                assert isinstance(app.screen, DocumentViewerScreen)
                mock_notify.assert_called_once()
                call_kwargs = mock_notify.call_args
                assert call_kwargs.kwargs.get("severity") == "warning"


def test_document_viewer_jk_bindings() -> None:
    """REQ-01/02/03: DocumentViewerScreen exposes j/k scroll bindings."""
    keys = {b.key for b in DocumentViewerScreen.BINDINGS}
    assert "j" in keys
    assert "k" in keys


async def test_spec_selector_q_closes(tmp_path: Path) -> None:
    """REQ-08/09: pressing 'q' in SpecSelectorScreen closes the screen."""
    from sdd_tui.tui.doc_viewer import SpecSelectorScreen

    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    change = openspec / "changes" / "my-change"
    change.mkdir()
    (change / "tasks.md").write_text("- [ ] **T01** Pending\n")
    # Two spec domains so SpecSelectorScreen is opened
    for domain in ("core", "tui"):
        spec_dir = change / "specs" / domain
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(f"# Spec: {domain}\n")

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)
            await pilot.press("s")  # opens SpecSelectorScreen (2 domains)
            assert isinstance(app.screen, SpecSelectorScreen)
            await pilot.press("q")
            assert isinstance(app.screen, ChangeDetailScreen)
