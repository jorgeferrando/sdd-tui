from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.core.velocity import (
    _get_change_dates,
    compute_velocity,
)


def _mock_result(returncode: int = 0, stdout: str = "") -> MagicMock:
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    return m


def _make_archive_entry(archive_dir: Path, date_prefix: str, change_name: str) -> Path:
    entry = archive_dir / f"{date_prefix}-{change_name}"
    entry.mkdir(parents=True)
    return entry


# --- _get_change_dates ---


def test_get_change_dates_returns_none_when_git_missing(tmp_path: Path) -> None:
    with patch("sdd_tui.core.velocity.subprocess.run", side_effect=FileNotFoundError):
        assert _get_change_dates("my-change", tmp_path) == (None, None)


def test_get_change_dates_returns_none_on_nonzero_exit(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(returncode=1),
    ):
        assert _get_change_dates("my-change", tmp_path) == (None, None)


def test_get_change_dates_returns_none_on_empty_output(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=""),
    ):
        assert _get_change_dates("my-change", tmp_path) == (None, None)


def test_get_change_dates_single_commit(tmp_path: Path) -> None:
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout="2026-03-05\n"),
    ):
        start, end = _get_change_dates("my-change", tmp_path)
    assert start == date(2026, 3, 5)
    assert end == date(2026, 3, 5)


def test_get_change_dates_multiple_commits(tmp_path: Path) -> None:
    # git log newest first → first line = end, last line = start
    stdout = "2026-03-05\n2026-03-04\n2026-03-01\n"
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=stdout),
    ):
        start, end = _get_change_dates("my-change", tmp_path)
    assert start == date(2026, 3, 1)
    assert end == date(2026, 3, 5)


# --- compute_velocity ---


def test_empty_archive_returns_empty_report(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    archive_dir.mkdir(parents=True)
    report = compute_velocity([archive_dir], tmp_path)
    assert report.changes == []
    assert report.median_lead_time is None
    assert report.p90_lead_time is None
    assert report.slowest_change is None


def test_archive_dir_not_existing_is_skipped(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    # do NOT create it
    report = compute_velocity([archive_dir], tmp_path)
    assert report.changes == []


def test_single_change_lead_time(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "my-change")

    stdout = "2026-03-05\n2026-03-01\n"
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=stdout),
    ):
        report = compute_velocity([archive_dir], tmp_path)

    assert len(report.changes) == 1
    cv = report.changes[0]
    assert cv.name == "my-change"
    assert cv.start_date == date(2026, 3, 1)
    assert cv.end_date == date(2026, 3, 5)
    assert cv.lead_time_days == 4


def test_no_commits_gives_none_dates(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "no-commits")

    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=""),
    ):
        report = compute_velocity([archive_dir], tmp_path)

    assert len(report.changes) == 1
    cv = report.changes[0]
    assert cv.start_date is None
    assert cv.end_date is None
    assert cv.lead_time_days is None


def test_single_change_no_median(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "my-change")

    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout="2026-03-05\n2026-03-01\n"),
    ):
        report = compute_velocity([archive_dir], tmp_path)

    assert report.median_lead_time is None
    assert report.p90_lead_time is None


def test_median_with_two_changes(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "alpha")
    _make_archive_entry(archive_dir, "2026-03-01", "beta")

    responses = [
        _mock_result(stdout="2026-03-03\n2026-03-01\n"),  # alpha: 2d
        _mock_result(stdout="2026-03-07\n2026-03-01\n"),  # beta: 6d
    ]
    with patch("sdd_tui.core.velocity.subprocess.run", side_effect=responses):
        report = compute_velocity([archive_dir], tmp_path)

    assert report.median_lead_time == 4.0  # median of [2, 6]


def test_slowest_change(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "alpha")
    _make_archive_entry(archive_dir, "2026-03-01", "beta")

    responses = [
        _mock_result(stdout="2026-03-03\n2026-03-01\n"),  # alpha: 2d
        _mock_result(stdout="2026-03-11\n2026-03-01\n"),  # beta: 10d
    ]
    with patch("sdd_tui.core.velocity.subprocess.run", side_effect=responses):
        report = compute_velocity([archive_dir], tmp_path)

    assert report.slowest_change is not None
    assert report.slowest_change.name == "beta"


def test_throughput_includes_current_week(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-03-01", "my-change")

    today = date.today()
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=f"{today.isoformat()}\n{today.isoformat()}\n"),
    ):
        report = compute_velocity([archive_dir], tmp_path)

    assert len(report.weekly_throughput) == 8
    last_week_start, last_count = report.weekly_throughput[-1]
    assert last_count == 1


def test_throughput_old_change_excluded(tmp_path: Path) -> None:
    archive_dir = tmp_path / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_dir, "2026-01-01", "old-change")

    old_date = date.today() - timedelta(weeks=9)
    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout=f"{old_date.isoformat()}\n{old_date.isoformat()}\n"),
    ):
        report = compute_velocity([archive_dir], tmp_path)

    total = sum(count for _, count in report.weekly_throughput)
    assert total == 0


def test_multiproject_aggregates(tmp_path: Path) -> None:
    proj_a = tmp_path / "proj-a"
    proj_b = tmp_path / "proj-b"
    archive_a = proj_a / "openspec" / "changes" / "archive"
    archive_b = proj_b / "openspec" / "changes" / "archive"
    _make_archive_entry(archive_a, "2026-03-01", "change-a")
    _make_archive_entry(archive_b, "2026-03-01", "change-b")

    with patch(
        "sdd_tui.core.velocity.subprocess.run",
        return_value=_mock_result(stdout="2026-03-05\n2026-03-01\n"),
    ):
        report = compute_velocity([archive_a, archive_b], tmp_path)

    assert len(report.changes) == 2
    projects = {c.project for c in report.changes}
    assert projects == {"proj-a", "proj-b"}
