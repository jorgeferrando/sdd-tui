from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.todos import TodoFile, load_todos


class TodosScreen(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="todos-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — todos"
        todos = load_todos(self.app._openspec_path)  # type: ignore[attr-defined]
        self.query_one("#todos-content", Static).update(_build_content(todos))

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()


def _build_content(todos: list[TodoFile]) -> Text:
    if not todos:
        return Text("No todos found")

    text = Text()
    for i, tf in enumerate(todos):
        done = sum(1 for item in tf.items if item.done)
        total = len(tf.items)
        text.append(f"── {tf.title} [{done}/{total}] ──\n", style="bold cyan")
        for item in tf.items:
            if item.done:
                text.append(f"  ✓ {item.text}\n", style="dim")
            else:
                text.append(f"  · {item.text}\n")
        if i < len(todos) - 1:
            text.append("\n")
    return text
