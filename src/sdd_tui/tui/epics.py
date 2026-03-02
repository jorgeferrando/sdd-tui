from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header
from textual.widget import Widget

from sdd_tui.core.models import Change, PhaseState
from sdd_tui.tui.change_detail import ChangeDetailScreen

PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]
DONE = "✓"
PENDING = "·"


def _phase_symbol(state: PhaseState) -> str:
    return DONE if state == PhaseState.DONE else PENDING


class EpicsView(Widget):
    BINDINGS = [
        Binding("enter", "select_change", "Detail"),
        Binding("r", "refresh", "Refresh"),
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("change", *PHASES)

        for change in self._changes:
            pipeline = change.pipeline
            row = (
                change.name,
                _phase_symbol(pipeline.propose),
                _phase_symbol(pipeline.spec),
                _phase_symbol(pipeline.design),
                _phase_symbol(pipeline.tasks),
                _phase_symbol(pipeline.apply),
                _phase_symbol(pipeline.verify),
            )
            table.add_row(*row)

    def update(self, changes: list[Change]) -> None:
        self._changes = changes
        self._populate()

    def action_select_change(self) -> None:
        row_index = self.query_one(DataTable).cursor_row
        if 0 <= row_index < len(self._changes):
            self.app.push_screen(ChangeDetailScreen(self._changes[row_index]))

    def action_refresh(self) -> None:
        self.app.refresh_changes()  # type: ignore[attr-defined]

    def action_quit(self) -> None:
        self.app.exit()
