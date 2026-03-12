from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable

from sdd_tui.core.models import Change
from sdd_tui.tui.epics import EpicsView


class _MilestoneApp(App):
    """Minimal app with _openspec_path for milestone grouping tests."""

    def __init__(self, changes: list[Change], openspec_path: Path) -> None:
        super().__init__()
        self._changes = changes
        self._openspec_path = openspec_path

    def compose(self) -> ComposeResult:
        yield EpicsView(self._changes)


def _change(name: str) -> Change:
    return Change(name=name, path=Path("/tmp"), project="myproject", project_path=Path("/tmp"))


def _write_milestones(openspec_path: Path, content: str) -> None:
    openspec_path.mkdir(parents=True, exist_ok=True)
    (openspec_path / "milestones.yaml").write_text(content)


BASIC_YAML = """\
milestones:
  - name: "v1.0 — Bootstrap"
    changes:
      - change-a
      - change-b
  - name: "v1.1 — UX"
    changes:
      - change-c
"""


async def test_milestone_grouping_adds_separator_rows(tmp_path: Path) -> None:
    """REQ-MG-01: milestone separators are added between change rows."""
    _write_milestones(tmp_path, BASIC_YAML)
    changes = [_change("change-a"), _change("change-b"), _change("change-c")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        table = app.query_one(DataTable)
        # 3 changes + 2 milestone separators
        assert table.row_count == 5


async def test_milestone_grouping_separator_not_navigable(tmp_path: Path) -> None:
    """REQ-MG-02: separator rows are not registered in _change_map."""
    _write_milestones(tmp_path, BASIC_YAML)
    changes = [_change("change-a"), _change("change-b"), _change("change-c")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        assert "v1.0 — Bootstrap" not in epics._change_map
        assert "v1.1 — UX" not in epics._change_map


async def test_unassigned_section_shows_for_missing_changes(tmp_path: Path) -> None:
    """REQ-MG-03: changes not in any milestone appear under '── unassigned ──'."""
    _write_milestones(tmp_path, BASIC_YAML)
    changes = [_change("change-a"), _change("orphan")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        table = app.query_one(DataTable)
        # change-a in v1.0 separator + change-a; unassigned separator + orphan = 4 rows
        assert table.row_count == 4
        assert "orphan" in epics._change_map


async def test_no_unassigned_when_all_assigned(tmp_path: Path) -> None:
    """REQ-MG-07: '── unassigned ──' is omitted when all changes are assigned."""
    _write_milestones(tmp_path, BASIC_YAML)
    changes = [_change("change-a"), _change("change-b"), _change("change-c")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        epics._populate()
        table = app.query_one(DataTable)
        # Collect all separator row texts
        row_keys = [str(k.value) for k in table.rows]
        assert not any("unassigned" in (k or "") for k in row_keys)


async def test_no_milestone_grouping_without_yaml(tmp_path: Path) -> None:
    """REQ-MG-04: without milestones.yaml the table is a flat list."""
    # No milestones.yaml written
    changes = [_change("change-a"), _change("change-b")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.row_count == 2


async def test_no_milestone_grouping_in_multiproject(tmp_path: Path) -> None:
    """REQ-MG-05: multi-project mode ignores milestones.yaml."""
    _write_milestones(tmp_path, BASIC_YAML)
    # Two changes from different projects → multi-project mode
    changes = [
        Change(
            name="change-a", path=Path("/tmp"),
            project="proj-alpha", project_path=Path("/tmp") / "alpha",
        ),
        Change(
            name="change-b", path=Path("/tmp"),
            project="proj-beta", project_path=Path("/tmp") / "beta",
        ),
    ]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        table = app.query_one(DataTable)
        # Multi-project: 2 project separators + 2 change rows = 4 rows (no milestone separators)
        assert table.row_count == 4
        row_keys = [str(k.value) for k in table.rows]
        assert not any("v1.0" in (k or "") for k in row_keys)


async def test_archived_not_grouped_by_milestone(tmp_path: Path) -> None:
    """REQ-MG-06: archived section is rendered without milestone separators."""
    _write_milestones(tmp_path, BASIC_YAML)
    active = [_change("change-a")]
    archived_change = Change(
        name="change-archived", path=Path("/tmp"), project="myproject",
        project_path=Path("/tmp"), archived=True
    )
    all_changes = active + [archived_change]
    app = _MilestoneApp(all_changes, tmp_path)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        # Simulate showing archived: update with all changes
        epics.update(all_changes)
        table = app.query_one(DataTable)
        row_keys = [str(k.value) for k in table.rows]
        # Archived section has its own separator, not a milestone one
        assert any("archived" in (k or "") for k in row_keys)
        assert not any("v1.1" in (k or "") for k in row_keys)


async def test_milestone_grouping_with_search_filter(tmp_path: Path) -> None:
    """REQ-MG-08: with search active, milestone sections with no matches are omitted."""
    _write_milestones(tmp_path, BASIC_YAML)
    changes = [_change("change-a"), _change("change-b"), _change("change-c")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        # Filter matching only change-c (in v1.1)
        epics._search_query = "change-c"
        epics._populate()
        table = app.query_one(DataTable)
        # v1.0 has no matches → omitted; v1.1 separator + change-c = 2 rows
        assert table.row_count == 2


async def test_milestone_change_not_in_active_skipped(tmp_path: Path) -> None:
    """REQ-MG-09: changes listed in YAML but not in active list are silently skipped."""
    _write_milestones(tmp_path, BASIC_YAML)
    # Only change-a is active; change-b and change-c are not (e.g., archived)
    changes = [_change("change-a")]
    app = _MilestoneApp(changes, tmp_path)
    async with app.run_test():
        table = app.query_one(DataTable)
        # v1.0 separator + change-a = 2 rows (change-b absent → no empty row)
        assert table.row_count == 2
        epics = app.query_one(EpicsView)
        assert "change-b" not in epics._change_map
