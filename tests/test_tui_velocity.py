from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import Static

from sdd_tui.core.velocity import ChangeVelocity, VelocityReport
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.velocity import VelocityView, _build_content, _build_markdown_report


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


# --- Unit tests for helpers ---


def test_build_content_empty_report() -> None:
    report = VelocityReport()
    text = _build_content(report)
    assert "No data available" in str(text)


def test_build_content_with_data() -> None:
    today = date.today()
    cv = ChangeVelocity(
        name="my-change",
        project="sdd-tui",
        start_date=date(2026, 3, 1),
        end_date=today,
        lead_time_days=4,
    )
    from sdd_tui.core.velocity import _compute_throughput

    wt = _compute_throughput([cv])
    report = VelocityReport(
        changes=[cv],
        weekly_throughput=wt,
        median_lead_time=None,
        p90_lead_time=None,
        slowest_change=None,
    )
    text = _build_content(report)
    content = str(text)
    assert "THROUGHPUT" in content
    assert "LEAD TIME" in content
    assert "Not enough data" in content


def test_build_markdown_report_empty() -> None:
    report = VelocityReport()
    md = _build_markdown_report(report)
    assert "Velocity Report" in md
    assert "Lead Time" in md


def test_build_markdown_report_with_data() -> None:
    cv = ChangeVelocity(
        name="my-change",
        project="sdd-tui",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 5),
        lead_time_days=4,
    )
    cv2 = ChangeVelocity(
        name="other-change",
        project="sdd-tui",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 9),
        lead_time_days=8,
    )
    report = VelocityReport(
        changes=[cv, cv2],
        weekly_throughput=[],
        median_lead_time=6.0,
        p90_lead_time=8.0,
        slowest_change=cv2,
    )
    md = _build_markdown_report(report)
    assert "sdd-tui" in md
    assert "Median: 6.0 days" in md
    assert "P90: 8.0 days" in md
    assert "other-change" in md


# --- TUI integration tests ---


async def test_velocity_view_mounts(openspec_with_change: Path) -> None:
    """VelocityView opens from View 1 via V binding."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        with patch("sdd_tui.tui.velocity.compute_velocity", return_value=VelocityReport()):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await pilot.press("V")
                assert isinstance(app.screen, VelocityView)


async def test_velocity_view_no_data_shows_message(openspec_with_change: Path) -> None:
    """VelocityView shows 'No data available' when report is empty."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        with patch("sdd_tui.tui.velocity.compute_velocity", return_value=VelocityReport()):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await pilot.press("V")
                content = app.screen.query_one("#velocity-content", Static)
                assert "No data available" in str(content.render())


async def test_velocity_view_esc_returns_to_view1(openspec_with_change: Path) -> None:
    """Esc in VelocityView pops back to main screen."""
    from sdd_tui.tui.epics import EpicsView

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        with patch("sdd_tui.tui.velocity.compute_velocity", return_value=VelocityReport()):
            app = SddTuiApp(openspec_with_change)
            async with app.run_test() as pilot:
                await pilot.press("V")
                assert isinstance(app.screen, VelocityView)
                await pilot.press("escape")
                assert app.screen.query_one(EpicsView) is not None
