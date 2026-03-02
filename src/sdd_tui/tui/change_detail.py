from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.models import Change, PhaseState, Pipeline, Task, TaskGitState

DONE = "✓"
PENDING = "·"
PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]


class TaskListPanel(ScrollableContainer):
    DEFAULT_CSS = """
    TaskListPanel {
        width: 2fr;
        height: 1fr;
        padding: 1 2;
    }
    """

    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks

    def compose(self) -> ComposeResult:
        yield Static(self._build_content())

    def _build_content(self) -> str:
        if not self._tasks:
            return "  No tasks defined yet"

        lines: list[str] = []
        last_amendment: str | None = None

        for task in self._tasks:
            if task.amendment != last_amendment and task.amendment is not None:
                lines.append(f"  ── amendment: {task.amendment} ──")
                last_amendment = task.amendment

            if task.git_state == TaskGitState.COMMITTED and task.commit:
                state = DONE
                ref = task.commit.hash
            else:
                state = PENDING
                ref = " " * 7

            lines.append(f"  {state} {ref}  {task.id}  {task.description}")

        return "\n".join(lines)


class PipelinePanel(Static):
    DEFAULT_CSS = """
    PipelinePanel {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        border-left: solid $panel-darken-2;
    }
    """

    def __init__(self, pipeline: Pipeline) -> None:
        content = self._build_content(pipeline)
        super().__init__(content)

    def _build_content(self, pipeline: Pipeline) -> str:
        lines = ["PIPELINE", ""]
        for phase in PHASES:
            state = getattr(pipeline, phase)
            symbol = DONE if state == PhaseState.DONE else PENDING
            lines.append(f"  {symbol}  {phase}")
        return "\n".join(lines)


class ChangeDetailScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh_view", "Refresh"),
    ]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield TaskListPanel(self._change.tasks)
            yield PipelinePanel(self._change.pipeline)
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name}"

    def action_refresh_view(self) -> None:
        self.app.refresh_changes()  # type: ignore[attr-defined]
        self.app.pop_screen()
