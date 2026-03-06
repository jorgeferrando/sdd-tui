from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


def _build_help_content() -> Text:
    content = Text()

    def section(title: str) -> None:
        content.append(f"\n  {title}\n", style="bold cyan")

    def row(key: str, description: str) -> None:
        content.append(f"  {key:<10} {description}\n")

    section("VIEW 1 — Changes")
    row("Enter", "Open change detail")
    row("a", "Toggle archived changes")
    row("r", "Refresh")
    row("s", "Open steering.md")
    row("H", "Spec health dashboard")
    row("X", "Decisions timeline")
    row("K", "Skill palette")
    row("q", "Quit")

    section("VIEW 2 — Change detail")
    row("p", "Open proposal.md")
    row("d", "Open design.md")
    row("s", "Open spec(s)")
    row("t", "Open tasks.md")
    row("q", "Open requirements.md")
    row("Space", "Copy next SDD command")
    row("E", "Spec evolution viewer")
    row("K", "Skill palette (with change context)")
    row("r", "Refresh in place")
    row("Esc", "Back to changes")

    section("VIEW 8 — Spec Health")
    row("Enter", "Open change detail")
    row("Esc", "Back to changes")

    section("VIEW 9 — Spec Evolution")
    row("D", "Toggle delta / canonical")
    row("j / k", "Scroll down / up")
    row("Esc", "Back")

    section("VIEWERS — Document / Spec Selector")
    row("j / k", "Scroll down / up")
    row("q / Esc", "Close")

    section("GLOBAL")
    row("?", "This help screen")
    row("ctrl+p", "Skill palette")

    content.append("\n")
    return content


HELP_CONTENT = _build_help_content()


class HelpScreen(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static(HELP_CONTENT, id="help-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — keyboard reference"

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()
