from __future__ import annotations

from pathlib import Path

from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from sdd_tui.core.models import Change


class DocumentViewerScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, path: Path, title: str) -> None:
        super().__init__()
        self._path = path
        self._doc_title = title

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="doc-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = self._doc_title
        if self._path.exists():
            content: Markdown | str = Markdown(self._path.read_text())
        else:
            content = f"[dim]{self._path.name} not found[/dim]"
        self.query_one("#doc-content", Static).update(content)


class SpecSelectorScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change
        self._domains: list[str] = self._find_domains()

    def _find_domains(self) -> list[str]:
        specs_dir = self._change.path / "specs"
        if not specs_dir.exists():
            return []
        return sorted(
            d.name for d in specs_dir.iterdir()
            if d.is_dir() and (d / "spec.md").exists()
        )

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(
            *[ListItem(Label(domain), id=f"domain-{domain}") for domain in self._domains]
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name} / specs"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if not item_id.startswith("domain-"):
            return
        domain = item_id[len("domain-"):]
        path = self._change.path / "specs" / domain / "spec.md"
        title = f"sdd-tui — {self._change.name} / spec:{domain}"
        self.app.push_screen(DocumentViewerScreen(path, title))
