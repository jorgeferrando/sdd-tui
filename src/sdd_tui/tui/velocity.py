from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.velocity import VelocityReport, compute_velocity


class VelocityView(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("e", "export", "Export"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, archive_dirs: list[Path]) -> None:
        super().__init__()
        self._archive_dirs = archive_dirs
        self._report: VelocityReport = VelocityReport()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="velocity-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — velocity"
        self._report = compute_velocity(self._archive_dirs, Path.cwd())
        self.query_one("#velocity-content", Static).update(_build_content(self._report))

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()

    def action_export(self) -> None:
        md = _build_markdown_report(self._report)
        self.app.copy_to_clipboard(md)
        self.notify("Report copied to clipboard")


def _build_content(report: VelocityReport) -> Text:
    if not report.changes:
        return Text("No data available")

    text = Text()

    # --- Throughput ---
    text.append("THROUGHPUT (últimas 8 semanas)\n\n", style="bold")
    counts = [count for _, count in report.weekly_throughput]
    max_count = max(counts) if counts else 0

    for ws, count in report.weekly_throughput:
        week_label = _week_label(ws)
        if count == 0:
            bar = "·"
        else:
            bar_width = max(1, round(count / max_count * 20)) if max_count > 0 else 0
            bar = "█" * bar_width
        unit = "change" if count == 1 else "changes"
        text.append(f"  {week_label}   {bar}  {count} {unit}\n")

    # --- Lead time ---
    text.append("\nLEAD TIME\n\n", style="bold")

    changes_with_data = [c for c in report.changes if c.lead_time_days is not None]
    if report.median_lead_time is None:
        text.append("  Not enough data (need at least 2 archived changes with commits)\n")
    else:
        text.append(f"  Changes with data: {len(changes_with_data)}\n")
        text.append(f"  Median: {report.median_lead_time:.1f}d\n")
        if report.p90_lead_time is not None:
            text.append(f"  P90:    {report.p90_lead_time:.1f}d\n")
        if report.slowest_change is not None:
            text.append(
                f"  Slowest: {report.slowest_change.name}"
                f" ({report.slowest_change.lead_time_days}d)\n"
            )

    return text


def _build_markdown_report(report: VelocityReport) -> str:
    today = date.today().isoformat()
    projects = list(dict.fromkeys(c.project for c in report.changes))
    project_str = ", ".join(projects) if projects else "—"

    lines = [
        f"## Velocity Report — {project_str} — {today}",
        "",
        "### Throughput (últimas 8 semanas)",
    ]

    total = 0
    for ws, count in report.weekly_throughput:
        lines.append(f"- {_week_label(ws)}: {count} change{'s' if count != 1 else ''}")
        total += count

    weeks = len(report.weekly_throughput)
    avg = f"{total / weeks:.1f}" if weeks > 0 else "0"
    lines += [
        f"- Total: {total} changes (avg {avg}/week)",
        "",
        "### Lead Time",
    ]

    changes_with_data = [c for c in report.changes if c.lead_time_days is not None]
    lines.append(f"- Changes with data: {len(changes_with_data)}")

    if report.median_lead_time is not None:
        lines.append(f"- Median: {report.median_lead_time:.1f} days")
    else:
        lines.append("- Median: not enough data")

    if report.p90_lead_time is not None:
        lines.append(f"- P90: {report.p90_lead_time:.1f} days")

    if report.slowest_change is not None:
        lines.append(
            f"- Slowest: {report.slowest_change.name}"
            f" ({report.slowest_change.lead_time_days} days)"
        )

    return "\n".join(lines) + "\n"


def _week_label(week_start: date) -> str:
    iso = week_start.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"
