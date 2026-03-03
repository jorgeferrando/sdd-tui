from __future__ import annotations

from pathlib import Path

from rich.syntax import Syntax
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
            self.styles.height = 3
            return

        last_amendment: str | None = None
        row_count = 0
        for task in self._tasks:
            if task.amendment != last_amendment and task.amendment is not None:
                table.add_row("", f"── amendment: {task.amendment} ──", "", "")
                last_amendment = task.amendment
                row_count += 1

            state = DONE if task.git_state == TaskGitState.COMMITTED else PENDING
            hash_str = task.commit.hash if task.commit else " " * 7
            table.add_row(state, hash_str, task.id, task.description, key=task.id)
            self._row_task_map[task.id] = task
            row_count += 1

        screen_h = self.app.size.height
        self.styles.height = min(row_count + 1, max(6, screen_h * 2 // 5))

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
        height: 1fr;
        padding: 1 2;
        border-top: solid $panel-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Select a task to view its diff", id="diff-content")

    def show_diff(self, text: str) -> None:
        content = Syntax(text, "diff", theme="monokai", word_wrap=False)
        self.query_one("#diff-content", Static).update(content)
        self.scroll_home(animate=False)

    def show_message(self, text: str) -> None:
        self.query_one("#diff-content", Static).update(text)
        self.scroll_home(animate=False)


class ChangeDetailScreen(Screen):
    DEFAULT_CSS = """
    ChangeDetailScreen .top-panel {
        height: auto;
        min-height: 6;
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
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        task = self.query_one(TaskListPanel).get_task(event.row_key.value)
        if task is None:
            return
        try:
            diff_panel = self.query_one(DiffPanel)
        except Exception:
            return
        if task.git_state == TaskGitState.COMMITTED and task.commit:
            diff = GitReader().get_diff(task.commit.hash, Path.cwd())
            if diff:
                diff_panel.show_diff(diff)
            else:
                diff_panel.show_message("Could not load diff")
        else:
            diff = GitReader().get_working_diff(Path.cwd())
            if diff:
                diff_panel.show_diff(diff)
            else:
                diff_panel.show_message("No uncommitted changes")

    def action_refresh_view(self) -> None:
        self.app.refresh_changes()  # type: ignore[attr-defined]
        self.app.pop_screen()
