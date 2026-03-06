from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Key
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input

from sdd_tui.core.skills import _CONTEXT_AWARE, load_skills


class SkillPaletteScreen(Screen):
    BINDINGS = [
        Binding("/", "search", "Filter"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    DEFAULT_CSS = """
    #search-input {
        display: none;
    }
    """

    def __init__(self, change_name: str | None = None) -> None:
        super().__init__()
        self._change_name = change_name
        self._search_mode = False
        self._search_query = ""
        self._skills = load_skills(Path.home() / ".claude" / "skills")

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row", show_header=True)
        yield Input(placeholder="/ filter...", id="search-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — skill palette"
        self._populate()
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("COMMAND", "DESCRIPTION")

        skills = self._skills
        if self._search_query:
            q = self._search_query.lower()
            skills = [
                s for s in skills
                if q in s.name.lower() or q in s.description.lower()
            ]

        if not skills:
            if self._search_query:
                table.add_row(f'No matches for "{self._search_query}"', "")
            else:
                table.add_row("No skills found", "")
            return

        for skill in skills:
            cmd_cell: str | Text = (
                self._highlight_match(f"/{skill.name}", self._search_query)
                if self._search_query
                else f"/{skill.name}"
            )
            table.add_row(cmd_cell, skill.description, key=skill.name)

    def _highlight_match(self, text: str, query: str) -> Text:
        result = Text()
        lower_text = text.lower()
        lower_query = query.lower()
        idx = lower_text.find(lower_query)
        if idx == -1:
            return Text(text)
        result.append(text[:idx])
        result.append(text[idx: idx + len(query)], style="bold cyan")
        result.append(text[idx + len(query):])
        return result

    def _build_command(self, skill_name: str) -> str:
        if self._change_name and skill_name in _CONTEXT_AWARE:
            return f"/{skill_name} {self._change_name}"
        return f"/{skill_name}"

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        cmd = self._build_command(event.row_key.value)
        self.app.copy_to_clipboard(cmd)
        self.notify(f"Copied: {cmd}")

    def on_key(self, event: Key) -> None:
        if self._search_mode and event.key == "escape":
            event.stop()
            self.action_cancel_search()

    def action_search(self) -> None:
        self._search_mode = True
        search_input = self.query_one("#search-input", Input)
        search_input.display = True
        search_input.focus()

    def action_cancel_search(self) -> None:
        self._search_query = ""
        self._search_mode = False
        search_input = self.query_one("#search-input", Input)
        search_input.clear()
        search_input.display = False
        self._populate()
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def on_input_changed(self, event: Input.Changed) -> None:
        if not self._search_mode:
            return
        self._search_query = event.value
        self._populate()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._search_query = event.value
        self._search_mode = False
        search_input = self.query_one("#search-input", Input)
        search_input.display = False
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())
