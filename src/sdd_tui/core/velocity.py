from __future__ import annotations

import statistics
import subprocess
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path


@dataclass
class ChangeVelocity:
    name: str
    project: str
    start_date: date | None
    end_date: date | None
    lead_time_days: int | None


@dataclass
class VelocityReport:
    changes: list[ChangeVelocity] = field(default_factory=list)
    weekly_throughput: list[tuple[date, int]] = field(default_factory=list)
    median_lead_time: float | None = None
    p90_lead_time: float | None = None
    slowest_change: ChangeVelocity | None = None


def compute_velocity(archive_dirs: list[Path], cwd: Path) -> VelocityReport:
    """Aggregate throughput and lead time from archived changes across all projects."""
    changes: list[ChangeVelocity] = []

    for archive_dir in archive_dirs:
        if not archive_dir.exists():
            continue
        # archive_dir = repo/openspec/changes/archive → parent×3 = repo root
        project_path = archive_dir.resolve().parent.parent.parent

        for entry in sorted(archive_dir.iterdir()):
            if not entry.is_dir():
                continue
            parts = entry.name.split("-", 3)
            if len(parts) < 4:
                continue
            try:
                date.fromisoformat(f"{parts[0]}-{parts[1]}-{parts[2]}")
            except ValueError:
                continue
            change_name = parts[3]
            start, end = _get_change_dates(change_name, project_path)
            lead_time = (end - start).days if start and end else None
            changes.append(
                ChangeVelocity(
                    name=change_name,
                    project=project_path.name,
                    start_date=start,
                    end_date=end,
                    lead_time_days=lead_time,
                )
            )

    weekly_throughput = _compute_throughput(changes)
    lead_times = [c.lead_time_days for c in changes if c.lead_time_days is not None]

    if len(lead_times) < 2:
        median_lt: float | None = None
        p90_lt: float | None = None
    else:
        median_lt = float(statistics.median(lead_times))
        sorted_lts = sorted(lead_times)
        p90_lt = float(sorted_lts[int(0.9 * len(sorted_lts))])

    slowest = max(
        (c for c in changes if c.lead_time_days is not None),
        key=lambda c: c.lead_time_days or 0,
        default=None,
    )

    return VelocityReport(
        changes=changes,
        weekly_throughput=weekly_throughput,
        median_lead_time=median_lt,
        p90_lead_time=p90_lt,
        slowest_change=slowest,
    )


def _compute_throughput(changes: list[ChangeVelocity]) -> list[tuple[date, int]]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday of current week
    weeks = [week_start - timedelta(weeks=7 - i) for i in range(8)]

    result = []
    for ws in weeks:
        we = ws + timedelta(days=6)
        count = sum(
            1 for c in changes if c.end_date is not None and ws <= c.end_date <= we
        )
        result.append((ws, count))
    return result


def _get_change_dates(
    change_name: str, project_path: Path
) -> tuple[date | None, date | None]:
    """Return (start_date, end_date) for a change from git log, or (None, None) on failure."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--format=%ad",
                "--date=short",
                "-F",
                f"--grep=[{change_name}]",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None, None

    if result.returncode != 0 or not result.stdout.strip():
        return None, None

    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    try:
        end_date = date.fromisoformat(lines[0])   # newest first in git log
        start_date = date.fromisoformat(lines[-1])  # oldest last
    except (ValueError, IndexError):
        return None, None

    return start_date, end_date
