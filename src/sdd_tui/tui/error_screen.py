from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.deps import Dep


def _build_error_content(deps: list[Dep]) -> Text:
    content = Text()
    content.append("\n")
    for dep in deps:
        content.append(f"  Required dependency missing: {dep.name}\n", style="bold red")
        content.append("\n")
        content.append("  Install:\n")
        for platform, cmd in dep.install_hint.items():
            content.append(f"    {platform:<10} {cmd}\n")
        if dep.docs_url:
            content.append(f"    Docs:      {dep.docs_url}\n")
        content.append("\n")
    return content


class ErrorScreen(Screen):
    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self, deps: list[Dep]) -> None:
        super().__init__()
        self._deps = deps

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static(_build_error_content(self._deps)))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — dependency error"

    def action_quit(self) -> None:
        self.app.exit()
