from __future__ import annotations

from pathlib import Path

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from sdd_tui.core.metrics import INACTIVE_THRESHOLD_DAYS, ChangeMetrics, parse_metrics
from sdd_tui.core.models import Change


class SpecHealthScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, changes: list[Change], include_archived: bool = False) -> None:
        super().__init__()
        self._changes = changes
        self._include_archived = include_archived
        self._change_map: dict[str, Change] = {}

    def on_mount(self) -> None:
        self.title = "sdd-tui — spec health"
        self._populate()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(cursor_type="row")
        yield Footer()

    def _populate(self) -> None:
        table = self.query_one(DataTable)

        active = [c for c in self._changes if not c.archived]
        archived = [c for c in self._changes if c.archived]

        visible = active + (archived if self._include_archived else [])

        if not visible:
            table.add_columns("info")
            table.add_row("No active changes")
            return

        all_metrics = {c.name: parse_metrics(c.path, Path.cwd()) for c in visible}
        has_research = any("research" in m.artifacts for m in all_metrics.values())
        has_requirements = any("requirements" in m.artifacts for m in all_metrics.values())

        table.add_columns("CHANGE", "REQ", "EARS%", "TASKS", "ARTIFACTS", "INACTIVE")

        for change in active:
            self._add_row(table, change, all_metrics[change.name], has_research, has_requirements)

        if self._include_archived and archived:
            table.add_row(
                "── archived ──",
                "",
                "",
                "",
                "",
                "",
            )
            for change in archived:
                self._add_row(
                    table,
                    change,
                    all_metrics[change.name],
                    has_research,
                    has_requirements,
                )

    def _add_row(
        self,
        table: DataTable,
        change: Change,
        metrics: ChangeMetrics,
        has_research: bool,
        has_requirements: bool,
    ) -> None:
        warn = metrics.req_count == 0

        name_cell = Text(change.name, style="yellow" if warn else "")
        req_cell = Text(
            "—" if metrics.req_count == 0 else str(metrics.req_count),
            style="yellow" if warn else "",
        )

        if metrics.req_count == 0:
            ears_cell = Text("—", style="yellow" if warn else "")
        else:
            pct = round(metrics.ears_count / metrics.req_count * 100)
            ears_cell = Text(f"{pct}%")

        tasks_cell = _tasks_cell(change)
        artifacts_cell = Text(_artifacts_str(metrics.artifacts, has_research, has_requirements))
        inactive_cell = _inactive_cell(metrics.inactive_days)

        table.add_row(
            name_cell,
            req_cell,
            ears_cell,
            tasks_cell,
            artifacts_cell,
            inactive_cell,
            key=change.name,
        )
        self._change_map[change.name] = change


    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        from sdd_tui.tui.change_detail import ChangeDetailScreen

        if event.row_key is None or event.row_key.value is None:
            return
        change = self._change_map.get(event.row_key.value)
        if change:
            self.app.push_screen(ChangeDetailScreen(change))


def _tasks_cell(change: Change) -> Text:
    if not change.tasks:
        return Text("—")
    total = len(change.tasks)
    done = sum(1 for t in change.tasks if t.done)
    return Text(f"{done}/{total}")


def _artifacts_str(artifacts: list[str], has_research: bool, has_requirements: bool) -> str:
    order = ["proposal", "spec"]
    if has_research:
        order.append("research")
    if has_requirements:
        order.append("requirements")
    order += ["design", "tasks"]

    _letters = {"requirements": "Q"}
    parts = []
    for name in order:
        if name in artifacts:
            parts.append(_letters.get(name, name[0].upper()))
        else:
            parts.append(".")
    return " ".join(parts)


def _inactive_cell(inactive_days: int | None) -> Text:
    if inactive_days is None:
        return Text("—")
    if inactive_days > INACTIVE_THRESHOLD_DAYS:
        return Text(f"!{inactive_days}d", style="yellow")
    return Text(f"{inactive_days}d")
