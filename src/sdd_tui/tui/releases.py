from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from sdd_tui.core.github import get_releases


class ReleasesScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row", show_header=True)
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — releases"
        table = self.query_one(DataTable)
        table.add_columns("TAG", "NAME", "DATE", "LATEST")
        releases = get_releases(Path.cwd())
        if not releases:
            table.add_row("", "No releases found", "", "")
            return
        for r in releases:
            date_short = r.published_at[:10] if r.published_at else ""
            latest = "✓" if r.is_latest else "·"
            table.add_row(r.tag_name, r.name, date_short, latest)
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())
