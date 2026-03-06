from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import Static

from sdd_tui.core.models import Change, Pipeline, Task
from sdd_tui.core.progress import ChangeProgress, ProgressReport
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.progress import ProgressDashboard, _build_content, _build_markdown_report


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


def _make_change(
    name: str = "my-change",
    pipeline: Pipeline | None = None,
    tasks: list[Task] | None = None,
) -> Change:
    return Change(
        name=name,
        path=Path("/tmp/fake"),
        pipeline=pipeline or Pipeline(),
        tasks=tasks or [],
    )


# --- Unit tests for _build_content ---


def test_build_content_empty_report_shows_message() -> None:
    report = ProgressReport()
    text = _build_content(report)
    assert "No changes to display" in str(text)


def test_build_content_shows_global_section() -> None:
    report = ProgressReport(
        changes=[ChangeProgress(name="a", tasks_done=2, tasks_total=4, furthest_phase="spec")],
        total_done=2,
        total_tasks=4,
        percent=50,
        pipeline_distribution={
            "propose": 0, "spec": 1, "design": 0, "tasks": 0, "apply": 0, "verify": 0
        },
    )
    content = str(_build_content(report))
    assert "GLOBAL" in content
    assert "50%" in content


def test_build_content_shows_by_change_section() -> None:
    report = ProgressReport(
        changes=[
            ChangeProgress(name="my-change", tasks_done=1, tasks_total=3, furthest_phase="design")
        ],
        total_done=1,
        total_tasks=3,
        percent=33,
        pipeline_distribution={
            "propose": 0, "spec": 0, "design": 1, "tasks": 0, "apply": 0, "verify": 0
        },
    )
    content = str(_build_content(report))
    assert "BY CHANGE" in content
    assert "my-change" in content


def test_build_content_shows_pipeline_distribution() -> None:
    report = ProgressReport(
        changes=[ChangeProgress(name="a", tasks_done=0, tasks_total=0, furthest_phase="tasks")],
        total_done=0,
        total_tasks=0,
        percent=0,
        pipeline_distribution={
            "propose": 0, "spec": 0, "design": 0, "tasks": 1, "apply": 0, "verify": 0
        },
    )
    content = str(_build_content(report))
    assert "PIPELINE" in content
    assert "tasks" in content


# --- Unit tests for _build_markdown_report ---


def test_build_markdown_report_contains_header() -> None:
    report = ProgressReport()
    md = _build_markdown_report(report)
    assert "Progress Dashboard" in md


def test_build_markdown_report_with_data() -> None:
    report = ProgressReport(
        changes=[ChangeProgress(name="foo", tasks_done=3, tasks_total=5, furthest_phase="apply")],
        total_done=3,
        total_tasks=5,
        percent=60,
        pipeline_distribution={
            "propose": 0, "spec": 0, "design": 0, "tasks": 0, "apply": 1, "verify": 0
        },
    )
    md = _build_markdown_report(report)
    assert "60%" in md
    assert "foo" in md


# --- TUI integration tests ---


async def test_progress_dashboard_mounts(openspec_with_change: Path) -> None:
    """ProgressDashboard opens from EpicsView via P binding."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("P")
            assert isinstance(app.screen, ProgressDashboard)


async def test_progress_dashboard_empty_shows_message(openspec_with_change: Path) -> None:
    """ProgressDashboard shows 'No changes to display' when no changes."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        with patch("sdd_tui.tui.app.load_all_changes", return_value=[]):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await pilot.press("P")
                content = app.screen.query_one("#progress-content", Static)
                assert "No changes to display" in str(content.render())


async def test_progress_dashboard_esc_returns_to_view1(openspec_with_change: Path) -> None:
    """Esc in ProgressDashboard pops back to main screen."""
    from sdd_tui.tui.epics import EpicsView

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("P")
            assert isinstance(app.screen, ProgressDashboard)
            await pilot.press("escape")
            assert app.screen.query_one(EpicsView) is not None
