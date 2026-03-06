from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.core.github import CiStatus, PrStatus
from sdd_tui.core.models import PhaseState, Pipeline
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import (
    _CI_LOADING,
    _PR_LOADING,
    ChangeDetailScreen,
    DiffPanel,
    PipelinePanel,
    next_command,
)
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


def test_pipeline_panel_shows_loading_pr_row(minimal_change) -> None:
    """REQ-PR02: PipelinePanel with sentinel shows '…  PR'."""
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    panel = PipelinePanel(pipeline, [], pr_status=_PR_LOADING)
    assert "…" in panel._text
    assert "PR" in panel._text


def test_pipeline_panel_shows_pr_none_row(minimal_change) -> None:
    """REQ-PR04: update_pr(None) shows '—  PR'."""
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    panel = PipelinePanel(pipeline, [], pr_status=_PR_LOADING)
    panel.update_pr(None)
    assert "—" in panel._text
    assert "PR" in panel._text


def test_pipeline_panel_shows_open_pr(minimal_change) -> None:
    """REQ-PR03: update_pr with OPEN PrStatus shows ⧗ and number."""
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    panel = PipelinePanel(pipeline, [], pr_status=_PR_LOADING)
    panel.update_pr(PrStatus(number=42, state="OPEN", approvals=0, changes_requested=0))
    assert "⧗" in panel._text
    assert "42" in panel._text


def test_pipeline_panel_shows_review_counts(minimal_change) -> None:
    """REQ-PR03/PR08: review counts shown for non-zero values."""
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    panel = PipelinePanel(pipeline, [], pr_status=_PR_LOADING)
    panel.update_pr(PrStatus(number=7, state="OPEN", approvals=2, changes_requested=1))
    assert "2✓" in panel._text
    assert "1✗" in panel._text


def test_pipeline_panel_omits_zero_counts(minimal_change) -> None:
    """REQ-PR08: zero approval count is omitted."""
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    panel = PipelinePanel(pipeline, [], pr_status=_PR_LOADING)
    panel.update_pr(PrStatus(number=3, state="OPEN", approvals=0, changes_requested=1))
    assert "0✓" not in panel._text
    assert "1✗" in panel._text


def _full_pipeline() -> Pipeline:
    return Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )


def test_pipeline_panel_ci_loading(minimal_change) -> None:
    """REQ-CI02: sentinel → '… CI'."""
    panel = PipelinePanel(_full_pipeline(), [], ci_status=_CI_LOADING)
    assert "…" in panel._text
    assert "CI" in panel._text


def test_pipeline_panel_ci_none(minimal_change) -> None:
    """REQ-CI03/CI04: update_ci(None) → '— CI'."""
    panel = PipelinePanel(_full_pipeline(), [], ci_status=_CI_LOADING)
    panel.update_ci(None)
    assert "—" in panel._text
    assert "CI" in panel._text


def test_pipeline_panel_ci_success(minimal_change) -> None:
    """REQ-CI05: completed+success → '✓ CI'."""
    panel = PipelinePanel(_full_pipeline(), [], ci_status=_CI_LOADING)
    panel.update_ci(CiStatus(workflow="CI", status="completed", conclusion="success"))
    assert "✓" in panel._text
    assert "CI" in panel._text


def test_pipeline_panel_ci_failure(minimal_change) -> None:
    """REQ-CI06: completed+failure → '✗ CI'."""
    panel = PipelinePanel(_full_pipeline(), [], ci_status=_CI_LOADING)
    panel.update_ci(CiStatus(workflow="CI", status="completed", conclusion="failure"))
    assert "✗" in panel._text
    assert "CI" in panel._text


def test_pipeline_panel_ci_in_progress(minimal_change) -> None:
    """REQ-CI07: in_progress → '⟳ CI'."""
    panel = PipelinePanel(_full_pipeline(), [], ci_status=_CI_LOADING)
    panel.update_ci(CiStatus(workflow="CI", status="in_progress", conclusion=None))
    assert "⟳" in panel._text
    assert "CI" in panel._text


async def test_ship_binding_copies_command(openspec_with_change: Path) -> None:
    """REQ-SH01/SH02: W copies gh pr create command to clipboard."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)
            screen = app.screen
            copied: list[str] = []
            app.copy_to_clipboard = lambda t: copied.append(t)  # type: ignore[method-assign]
            with patch.object(screen, "notify"):
                await pilot.press("shift+w")
            assert len(copied) == 1
            assert "gh pr create" in copied[0]
            assert "my-change" in copied[0]


# --- next_command unit tests (REQ-NA-02, REQ-NA-06) ---


def _pipeline(**kwargs) -> Pipeline:
    defaults = dict(
        propose=PhaseState.DONE,
        spec=PhaseState.DONE,
        design=PhaseState.DONE,
        tasks=PhaseState.DONE,
        apply=PhaseState.DONE,
        verify=PhaseState.DONE,
    )
    defaults.update(kwargs)
    return Pipeline(**defaults)


def test_next_command_propose_pending() -> None:
    """REQ-NA-02: propose PENDING → /sdd-propose."""
    p = _pipeline(propose=PhaseState.PENDING)
    assert next_command(p, [], "foo") == '/sdd-propose "foo"'


def test_next_command_spec_pending() -> None:
    """REQ-NA-02: spec PENDING → /sdd-spec."""
    p = _pipeline(spec=PhaseState.PENDING)
    assert next_command(p, [], "foo") == "/sdd-spec foo"


def test_next_command_design_pending() -> None:
    """REQ-NA-02: design PENDING → /sdd-design."""
    p = _pipeline(design=PhaseState.PENDING)
    assert next_command(p, [], "foo") == "/sdd-design foo"


def test_next_command_tasks_pending() -> None:
    """REQ-NA-02: tasks PENDING → /sdd-tasks."""
    p = _pipeline(tasks=PhaseState.PENDING)
    assert next_command(p, [], "foo") == "/sdd-tasks foo"


def test_next_command_apply_pending_with_task(minimal_change) -> None:
    """REQ-NA-06: apply PENDING with a pending task → /sdd-apply {task_id}."""
    from sdd_tui.core.models import Task, TaskGitState

    p = _pipeline(apply=PhaseState.PENDING, verify=PhaseState.PENDING)
    tasks = [
        Task(id="T01", description="done", done=True, git_state=TaskGitState.PENDING),
        Task(id="T02", description="pending", done=False, git_state=TaskGitState.PENDING),
    ]
    assert next_command(p, tasks, "foo") == "/sdd-apply T02"


def test_next_command_apply_pending_no_task() -> None:
    """REQ-NA-06: apply PENDING with no tasks → /sdd-apply {name}."""
    p = _pipeline(apply=PhaseState.PENDING, verify=PhaseState.PENDING)
    assert next_command(p, [], "foo") == "/sdd-apply foo"


def test_next_command_verify_pending() -> None:
    """REQ-NA-02: verify PENDING → /sdd-verify."""
    p = _pipeline(verify=PhaseState.PENDING)
    assert next_command(p, [], "foo") == "/sdd-verify foo"


def test_next_command_all_done() -> None:
    """REQ-NA-05: all phases DONE → /sdd-archive."""
    p = _pipeline()
    assert next_command(p, [], "foo") == "/sdd-archive foo"


# --- PipelinePanel NEXT line tests (REQ-NA-01, REQ-NA-03, REQ-NA-04, REQ-NA-08) ---


def test_pipeline_panel_shows_next_line(minimal_change) -> None:
    """REQ-NA-01: PipelinePanel._text contains 'NEXT'."""
    pipeline = _pipeline(spec=PhaseState.PENDING)
    panel = PipelinePanel(pipeline, [], name="foo")
    assert "NEXT" in panel._text


def test_pipeline_panel_next_shows_correct_command(minimal_change) -> None:
    """REQ-NA-04: NEXT line contains the resolved command."""
    pipeline = _pipeline(spec=PhaseState.PENDING)
    panel = PipelinePanel(pipeline, [], name="foo")
    assert "/sdd-spec foo" in panel._text


def test_pipeline_panel_next_not_updated_on_pr(minimal_change) -> None:
    """REQ-NA-08: NEXT line does not change after update_pr()."""
    pipeline = _pipeline(spec=PhaseState.PENDING)
    panel = PipelinePanel(pipeline, [], name="foo", pr_status=_PR_LOADING)
    next_before = [line for line in panel._text.splitlines() if "NEXT" in line]
    panel.update_pr(None)
    next_after = [line for line in panel._text.splitlines() if "NEXT" in line]
    assert next_before == next_after


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
