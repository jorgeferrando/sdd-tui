from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.models import Change
from sdd_tui.core.progress import ProgressReport, compute_progress

_PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]
_BAR_WIDTH_GLOBAL = 20
_BAR_WIDTH_CHANGE = 12


class ProgressDashboard(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("e", "export", "Export"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, changes: list[Change]) -> None:
        super().__init__()
        self._changes = changes
        self._report: ProgressReport = ProgressReport()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="progress-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — progress"
        self._report = compute_progress(self._changes)
        self.query_one("#progress-content", Static).update(_build_content(self._report))

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()

    def action_export(self) -> None:
        md = _build_markdown_report(self._report)
        self.app.copy_to_clipboard(md)  # type: ignore[attr-defined]
        self.notify("Report copied to clipboard")


def _bar(done: int, total: int, width: int) -> str:
    if total == 0:
        return "░" * width
    filled = round(done / total * width)
    return "█" * filled + "░" * (width - filled)


def _build_content(report: ProgressReport) -> Text:
    if not report.changes:
        return Text("No changes to display")

    text = Text()

    # --- GLOBAL ---
    text.append("GLOBAL\n\n", style="bold")
    text.append(f"  Changes:   {len(report.changes)}\n")
    text.append(
        f"  Tasks:    {report.total_tasks}"
        f"  ({report.total_done} done / {report.total_tasks - report.total_done} pending)\n"
    )
    bar = _bar(report.total_done, report.total_tasks, _BAR_WIDTH_GLOBAL)
    text.append(f"  Progress: {report.percent}%  {bar}\n")

    # --- BY CHANGE ---
    text.append("\nBY CHANGE\n\n", style="bold")
    name_width = max((len(cp.name) for cp in report.changes), default=10)
    for cp in report.changes:
        bar = _bar(cp.tasks_done, cp.tasks_total, _BAR_WIDTH_CHANGE)
        ratio = f"{cp.tasks_done}/{cp.tasks_total}"
        phase = cp.furthest_phase or "—"
        text.append(f"  {cp.name:<{name_width}}  {bar}  {ratio:<5}  {phase}\n")

    # --- PIPELINE DISTRIBUTION ---
    text.append("\nPIPELINE DISTRIBUTION\n\n", style="bold")
    dist = report.pipeline_distribution
    max_count = max(dist.values(), default=0)
    for phase in _PHASES:
        count = dist[phase]
        if count == 0:
            bar = "·"
        else:
            bar_width = max(1, round(count / max_count * 20)) if max_count > 0 else 0
            bar = "■" * bar_width
        text.append(f"  {phase:<8}  {bar:<21}  {count}\n")

    return text


def _build_markdown_report(report: ProgressReport) -> str:
    today = date.today().isoformat()
    lines = [
        f"## Progress Dashboard — {today}",
        "",
        "### Global",
        f"- Changes: {len(report.changes)}",
        f"- Tasks: {report.total_done}/{report.total_tasks} ({report.percent}%)",
        "",
        "### By Change",
    ]

    for cp in report.changes:
        phase = cp.furthest_phase or "—"
        lines.append(f"- {cp.name}: {cp.tasks_done}/{cp.tasks_total} tasks — {phase}")

    lines += [
        "",
        "### Pipeline Distribution",
    ]

    for phase in _PHASES:
        count = report.pipeline_distribution.get(phase, 0)
        lines.append(f"- {phase}: {count}")

    return "\n".join(lines) + "\n"
