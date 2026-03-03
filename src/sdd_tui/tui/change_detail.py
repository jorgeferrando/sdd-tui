from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Static

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import Change, PhaseState, Pipeline, Task, TaskGitState

DONE = "✓"
PENDING = "·"
PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]


class TaskListPanel(Widget):
    DEFAULT_CSS = """
    TaskListPanel {
        width: 2fr;
        height: 1fr;
    }
    """

    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks
        self._row_task_map: dict[str, Task] = {}

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row", show_header=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("state", "hash", "id", "desc")

        if not self._tasks:
            table.add_row("", "", "", "No tasks defined yet")
            return

        last_amendment: str | None = None
        for task in self._tasks:
            if task.amendment != last_amendment and task.amendment is not None:
                table.add_row("", f"── amendment: {task.amendment} ──", "", "")
                last_amendment = task.amendment

            state = DONE if task.git_state == TaskGitState.COMMITTED else PENDING
            hash_str = task.commit.hash if task.commit else " " * 7
            table.add_row(state, hash_str, task.id, task.description, key=task.id)
            self._row_task_map[task.id] = task

    def get_task(self, row_key: str) -> Task | None:
        return self._row_task_map.get(row_key)


class PipelinePanel(Static):
    DEFAULT_CSS = """
    PipelinePanel {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        border-left: solid $panel-darken-2;
    }
    """

    def __init__(self, pipeline: Pipeline, tasks: list[Task]) -> None:
        content = self._build_content(pipeline, tasks)
        super().__init__(content)

    def _build_content(self, pipeline: Pipeline, tasks: list[Task]) -> str:
        lines = ["PIPELINE", ""]
        for phase in PHASES:
            state = getattr(pipeline, phase)
            if phase == "apply" and state != PhaseState.DONE and tasks:
                done = sum(1 for t in tasks if t.done)
                symbol = f"{done}/{len(tasks)}" if done > 0 else PENDING
            else:
                symbol = DONE if state == PhaseState.DONE else PENDING
            lines.append(f"  {symbol:<3}  {phase}")
        return "\n".join(lines)


class DiffPanel(ScrollableContainer):
    DEFAULT_CSS = """
    DiffPanel {
        height: 2fr;
        padding: 1 2;
        border-top: solid $panel-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="diff-content")

    def update_diff(self, text: str) -> None:
        self.query_one("#diff-content", Static).update(text)


class ChangeDetailScreen(Screen):
    DEFAULT_CSS = """
    ChangeDetailScreen .top-panel {
        height: 3fr;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh_view", "Refresh"),
    ]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Horizontal(classes="top-panel"):
                yield TaskListPanel(self._change.tasks)
                yield PipelinePanel(self._change.pipeline, self._change.tasks)
            yield DiffPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name}"

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        task = self.query_one(TaskListPanel).get_task(event.row_key.value)
        if task is None:
            return
        diff_panel = self.query_one(DiffPanel)
        if task.git_state == TaskGitState.COMMITTED and task.commit:
            diff = GitReader().get_diff(task.commit.hash, Path.cwd())
            diff_panel.update_diff(diff or "Could not load diff")
        else:
            diff_panel.update_diff("Not committed yet")

    def action_refresh_view(self) -> None:
        self.app.refresh_changes()  # type: ignore[attr-defined]
        self.app.pop_screen()
