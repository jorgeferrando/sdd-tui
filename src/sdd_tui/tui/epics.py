from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header
from textual.widget import Widget

from sdd_tui.core.models import Change, PhaseState, Task
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.spec_evolution import DecisionsTimeline
from sdd_tui.tui.spec_health import SpecHealthScreen

PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]
DONE = "✓"
PENDING = "·"


def _phase_symbol(state: PhaseState) -> str:
    return DONE if state == PhaseState.DONE else PENDING


def _apply_display(state: PhaseState, tasks: list[Task]) -> str:
    if state == PhaseState.DONE:
        return DONE
    if not tasks:
        return PENDING
    done = sum(1 for t in tasks if t.done)
    if done == 0:
        return PENDING
    return f"{done}/{len(tasks)}"


class EpicsView(Widget):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("a", "toggle_archived", "Archived"),
        Binding("h", "health", "Health"),
        Binding("x", "decisions_timeline", "Decisions"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    EpicsView {
        height: 1fr;
    }
    """

    def __init__(self, changes: list[Change]) -> None:
        super().__init__()
        self._changes = changes
        self._show_archived = False
        self._change_map: dict[str, Change] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield DataTable(cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("change", *PHASES)
        self._change_map = {}

        active = [c for c in self._changes if not c.archived]
        archived = [c for c in self._changes if c.archived]

        for change in active:
            self._add_change_row(table, change)

        if archived:
            table.add_row("── archived ──", "", "", "", "", "", "")
            for change in archived:
                self._add_change_row(table, change)

    def _add_change_row(self, table: DataTable, change: Change) -> None:
        pipeline = change.pipeline
        row = (
            change.name,
            _phase_symbol(pipeline.propose),
            _phase_symbol(pipeline.spec),
            _phase_symbol(pipeline.design),
            _phase_symbol(pipeline.tasks),
            _apply_display(pipeline.apply, change.tasks),
            _phase_symbol(pipeline.verify),
        )
        table.add_row(*row, key=change.name)
        self._change_map[change.name] = change

    def update(self, changes: list[Change]) -> None:
        self._changes = changes
        self._populate()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        change = self._change_map.get(event.row_key.value)
        if change:
            self.app.push_screen(ChangeDetailScreen(change))

    def action_toggle_archived(self) -> None:
        self._show_archived = not self._show_archived
        self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]

    def action_refresh(self) -> None:
        self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]

    def action_health(self) -> None:
        self.app.push_screen(SpecHealthScreen(self._changes, self._show_archived))

    def action_decisions_timeline(self) -> None:
        archive_dir = Path.cwd() / "openspec" / "changes" / "archive"
        self.app.push_screen(DecisionsTimeline(archive_dir))

    def action_quit(self) -> None:
        self.app.exit()
