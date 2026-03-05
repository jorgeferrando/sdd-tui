from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Key
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Input

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
        Binding("a", "toggle_archived", "Show archived"),
        Binding("s", "steering", "Steering"),
        Binding("h", "health", "Health"),
        Binding("x", "decisions_timeline", "Decisions"),
        Binding("V", "velocity", "Velocity"),
        Binding("/", "search", "Search"),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    EpicsView {
        height: 1fr;
    }
    #search-input {
        display: none;
    }
    """

    def __init__(self, changes: list[Change]) -> None:
        super().__init__()
        self._changes = changes
        self._show_archived = False
        self._change_map: dict[str, Change] = {}
        self._search_mode = False
        self._search_query = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield DataTable(cursor_type="row")
        yield Input(placeholder="/ search...", id="search-input")
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

        active_projects = list(dict.fromkeys(c.project for c in active))
        is_multi = len(active_projects) > 1

        if not is_multi:
            if self._search_query:
                active = self._filter_changes(active, self._search_query)
                archived = self._filter_changes(archived, self._search_query)
            if not active and not archived and self._search_query:
                table.add_row(f'No matches for "{self._search_query}"', "", "", "", "", "", "")
                return
            for change in active:
                self._add_change_row(table, change)
        else:
            for project_name in active_projects:
                proj_changes = [c for c in active if c.project == project_name]
                filtered = self._filter_changes(proj_changes, self._search_query) if self._search_query else proj_changes
                table.add_row(f"─── {project_name} ───", "", "", "", "", "", "")
                if not filtered:
                    table.add_row("  (no active changes)", "", "", "", "", "", "")
                else:
                    for change in filtered:
                        self._add_change_row(table, change)
            if self._search_query:
                archived = self._filter_changes(archived, self._search_query)

        if archived:
            table.add_row("── archived ──", "", "", "", "", "", "")
            for change in archived:
                self._add_change_row(table, change)

    def _filter_changes(self, changes: list[Change], query: str) -> list[Change]:
        q = query.lower()
        return [c for c in changes if q in c.name.lower()]

    def _highlight_match(self, name: str, query: str) -> Text:
        text = Text()
        lower_name = name.lower()
        lower_query = query.lower()
        idx = lower_name.find(lower_query)
        if idx == -1:
            return Text(name)
        text.append(name[:idx])
        text.append(name[idx : idx + len(query)], style="bold cyan")
        text.append(name[idx + len(query) :])
        return text

    def _add_change_row(self, table: DataTable, change: Change) -> None:
        pipeline = change.pipeline
        name_cell: str | Text = (
            self._highlight_match(change.name, self._search_query)
            if self._search_query
            else change.name
        )
        row = (
            name_cell,
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

    def on_key(self, event: Key) -> None:
        if self._search_mode and event.key == "escape":
            event.stop()
            self.action_cancel_search()

    def action_search(self) -> None:
        self._search_mode = True
        search_input = self.query_one("#search-input", Input)
        search_input.display = True
        search_input.focus()

    def action_cancel_search(self) -> None:
        self._search_query = ""
        self._search_mode = False
        self.app.sub_title = ""  # type: ignore[attr-defined]
        search_input = self.query_one("#search-input", Input)
        search_input.clear()
        search_input.display = False
        self._populate()
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def on_input_changed(self, event: Input.Changed) -> None:
        if not self._search_mode:
            return
        self._search_query = event.value
        self._populate()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        self._search_query = query
        self._search_mode = False
        search_input = self.query_one("#search-input", Input)
        search_input.display = False
        self.app.sub_title = f'filtered: "{query}"' if query else ""  # type: ignore[attr-defined]
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def action_toggle_archived(self) -> None:
        self._show_archived = not self._show_archived
        label = "Hide archived" if self._show_archived else "Show archived"
        self.BINDINGS = [
            Binding("r", "refresh", "Refresh"),
            Binding("a", "toggle_archived", label),
            Binding("s", "steering", "Steering"),
            Binding("h", "health", "Health"),
            Binding("x", "decisions_timeline", "Decisions"),
            Binding("V", "velocity", "Velocity"),
            Binding("/", "search", "Search"),
            Binding("q", "quit", "Quit"),
        ]
        self.refresh_bindings()
        self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]

    def action_refresh(self) -> None:
        self._search_query = ""
        self._search_mode = False
        self.app.sub_title = ""  # type: ignore[attr-defined]
        search_input = self.query_one("#search-input", Input)
        search_input.clear()
        search_input.display = False
        changes = self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]
        n_active = sum(1 for c in changes if not c.archived)
        n_archived = sum(1 for c in changes if c.archived)
        self.notify(f"{n_active} changes loaded ({n_archived} archived)")

    def action_health(self) -> None:
        self.app.push_screen(SpecHealthScreen(self._changes, self._show_archived))

    def action_steering(self) -> None:
        from sdd_tui.tui.doc_viewer import DocumentViewerScreen

        steering_path = self.app._openspec_path / "steering.md"
        self.app.push_screen(DocumentViewerScreen(steering_path, "sdd-tui — steering"))

    def action_decisions_timeline(self) -> None:
        seen: set[Path] = set()
        dirs: list[Path] = []
        for change in self._changes:
            if change.project_path and change.project_path not in seen:
                seen.add(change.project_path)
                dirs.append(change.project_path / "openspec" / "changes" / "archive")
        if not dirs:
            dirs = [self.app._openspec_path / "changes" / "archive"]
        self.app.push_screen(DecisionsTimeline(dirs))

    def action_velocity(self) -> None:
        from sdd_tui.tui.velocity import VelocityView

        seen: set[Path] = set()
        dirs: list[Path] = []
        for change in self._changes:
            if change.project_path and change.project_path not in seen:
                seen.add(change.project_path)
                dirs.append(change.project_path / "openspec" / "changes" / "archive")
        if not dirs:
            dirs = [self.app._openspec_path / "changes" / "archive"]
        self.app.push_screen(VelocityView(dirs))

    def action_quit(self) -> None:
        self.app.exit()
