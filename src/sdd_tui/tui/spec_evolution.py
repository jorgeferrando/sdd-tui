from __future__ import annotations

from itertools import chain
from pathlib import Path

from rich.markdown import Markdown
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from sdd_tui.core.models import Change
from sdd_tui.core.spec_parser import collect_archived_decisions, parse_delta


class SpecEvolutionScreen(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("escape", "app.pop_screen", "Back"),
        Binding("d", "toggle_canonical", "Toggle canonical"),
    ]

    DEFAULT_CSS = """
    SpecEvolutionScreen .domain-panel {
        width: 20;
        border-right: solid $panel-darken-2;
    }
    SpecEvolutionScreen .diff-panel {
        width: 1fr;
    }
    """

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change
        self._domains: list[str] = self._find_domains()
        self._current_domain: str = self._domains[0] if self._domains else ""
        self._canonical_mode: bool = False

    def _find_domains(self) -> list[str]:
        specs_dir = self._change.path / "specs"
        if not specs_dir.exists():
            return []
        return sorted(
            d.name for d in specs_dir.iterdir() if d.is_dir() and (d / "spec.md").exists()
        )

    def compose(self) -> ComposeResult:
        yield Header()
        if not self._domains:
            yield Static("No specs found for this change")
        elif len(self._domains) == 1:
            yield ScrollableContainer(Static("", id="diff-content"), classes="diff-panel")
        else:
            with Horizontal():
                yield ListView(
                    *[ListItem(Label(d), id=f"domain-{d}") for d in self._domains],
                    classes="domain-panel",
                )
                yield ScrollableContainer(Static("", id="diff-content"), classes="diff-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._update_title()
        if self._current_domain:
            self._render_domain(self._current_domain)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if item_id.startswith("domain-"):
            self._current_domain = item_id[len("domain-") :]
            self._render_domain(self._current_domain)

    def action_toggle_canonical(self) -> None:
        self._canonical_mode = not self._canonical_mode
        self._update_title()
        if self._current_domain:
            self._render_domain(self._current_domain)

    def _update_title(self) -> None:
        mode = "canonical" if self._canonical_mode else "delta"
        self.title = f"sdd-tui — {self._change.name} / spec evolution [{mode}]"

    def _render_domain(self, domain: str) -> None:
        static = self.query_one("#diff-content", Static)

        if self._canonical_mode:
            canonical = self.app._openspec_path / "specs" / domain / "spec.md"
            if canonical.exists():
                static.update(Markdown(canonical.read_text()))
            else:
                static.update(f"No canonical spec found for {domain}")
            return

        spec_path = self._change.path / "specs" / domain / "spec.md"
        delta = parse_delta(spec_path)

        if delta.fallback:
            static.update(Markdown(spec_path.read_text()))
            return

        content = Text()

        if delta.added:
            content.append("ADDED\n", style="bold green")
            for line in delta.added:
                content.append(line + "\n", style="green")
            content.append("\n")

        if delta.modified:
            content.append("MODIFIED\n", style="bold yellow")
            for line in delta.modified:
                content.append(line + "\n", style="yellow")
            content.append("\n")

        if delta.removed:
            content.append("REMOVED\n", style="bold red")
            for line in delta.removed:
                content.append(line + "\n", style="red")

        static.update(content)

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()


class DecisionsTimeline(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, archive_dirs: list[Path]) -> None:
        super().__init__()
        self._archive_dirs = archive_dirs

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="timeline-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — decisions timeline"
        self._populate()

    def _populate(self) -> None:
        static = self.query_one("#timeline-content", Static)
        all_changes = sorted(
            chain.from_iterable(collect_archived_decisions(d) for d in self._archive_dirs),
            key=lambda cd: cd.archive_date,
        )
        with_decisions = [cd for cd in all_changes if cd.decisions]

        if not with_decisions:
            static.update("No archived decisions found")
            return

        content = Text()
        for cd in with_decisions:
            header = f"── {cd.change_name} ({cd.archive_date}) ──"
            content.append(header + "\n", style="bold cyan")
            for decision in cd.decisions:
                content.append(f"  • {decision.decision}\n", style="white")
                content.append(f"    vs: {decision.alternative}\n", style="dim")
                content.append(f"    why: {decision.reason}\n", style="italic")
            content.append("\n")

        static.update(content)

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()
