from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import Change, CommitInfo
from sdd_tui.tui.change_detail import DiffPanel


class GitLogScreen(Screen):
    DEFAULT_CSS = """
    GitLogScreen .log-panel {
        height: auto;
        min-height: 4;
        max-height: 12;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("j", "scroll_down", "Scroll down"),
        Binding("k", "scroll_up", "Scroll up"),
    ]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change
        self._commits: list[CommitInfo] = []
        self._hash_map: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield DataTable(cursor_type="row", show_header=True, classes="log-panel")
            yield DiffPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name}"
        self.sub_title = "git log"
        table = self.query_one(DataTable)
        table.add_columns("HASH", "AUTHOR", "DATE", "MESSAGE")
        cwd = self._change.project_path or Path.cwd()
        self._commits = GitReader().get_change_log(self._change.name, cwd)
        if not self._commits:
            table.add_row("", "", "", f"No commits found for [{self._change.name}]")
            self.query_one(DiffPanel).show_message("No commits found.")
            return
        for commit in self._commits:
            table.add_row(
                commit.hash,
                commit.author or "",
                commit.date_relative or "",
                commit.message,
                key=commit.hash,
            )
            self._hash_map[commit.hash] = commit.hash
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        commit_hash = event.row_key.value
        self.query_one(DiffPanel).show_message("[dim]Loading diff…[/dim]")
        self._load_diff_worker(commit_hash)

    @work(thread=True, exclusive=True)
    def _load_diff_worker(self, commit_hash: str) -> None:
        cwd = self._change.project_path or Path.cwd()
        diff = GitReader().get_diff(commit_hash, cwd)
        if diff:
            self.app.call_from_thread(self.query_one(DiffPanel).show_diff, diff)
        else:
            self.app.call_from_thread(
                self.query_one(DiffPanel).show_message, "Could not load diff."
            )

    def action_scroll_down(self) -> None:
        self.query_one(DiffPanel).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(DiffPanel).scroll_up()
