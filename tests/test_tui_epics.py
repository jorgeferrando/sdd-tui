from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input

from sdd_tui.core.models import Change
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.epics import EpicsView
from sdd_tui.tui.spec_health import SpecHealthScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_epics_loads_changes(openspec_with_change: Path) -> None:
    """REQ-04: EpicsView renders one row per active change."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as _:
            table = app.query_one(DataTable)
            assert table.row_count == 1


async def test_epics_toggle_archived_shows_archived(
    openspec_with_archive: Path,
) -> None:
    """REQ-05: pressing 'a' adds archived changes to the table."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            rows_before = table.row_count
            await pilot.press("a")
            rows_after = table.row_count
            assert rows_after > rows_before


async def test_epics_toggle_archived_hides_again(openspec_with_archive: Path) -> None:
    """REQ-05: pressing 'a' twice returns to original row count."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            rows_before = table.row_count
            await pilot.press("a")
            await pilot.press("a")
            assert table.row_count == rows_before


async def test_epics_enter_navigates_to_change_detail(
    openspec_with_change: Path,
) -> None:
    """REQ-06: Enter on a change row pushes ChangeDetailScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            assert isinstance(app.screen, ChangeDetailScreen)


async def test_epics_h_navigates_to_spec_health(openspec_with_change: Path) -> None:
    """REQ-07: pressing 'h' pushes SpecHealthScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("h")
            assert isinstance(app.screen, SpecHealthScreen)


async def test_epics_r_stays_on_epics(openspec_with_change: Path) -> None:
    """REQ-08: pressing 'r' reloads without navigating away."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("r")
            # Still on the default screen (EpicsView is a widget, not a Screen)
            assert app.query_one(EpicsView) is not None
            assert len(app.screen_stack) == 1


async def test_toggle_archived_label_changes(openspec_with_archive: Path) -> None:
    """REQ-01/02: pressing 'a' changes the binding label to 'Hide archived'."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            await pilot.press("a")
            labels = [b.description for b in epics.BINDINGS]
            assert "Hide archived" in labels
            assert "Show archived" not in labels


async def test_toggle_archived_label_reverts(openspec_with_archive: Path) -> None:
    """REQ-01/02: pressing 'a' twice reverts the binding label to 'Show archived'."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            await pilot.press("a")
            await pilot.press("a")
            labels = [b.description for b in epics.BINDINGS]
            assert "Show archived" in labels
            assert "Hide archived" not in labels


async def test_refresh_emits_notify(openspec_with_archive: Path) -> None:
    """REQ-04: pressing 'r' emits a notify with change count."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            epics = app.query_one(EpicsView)
            with patch.object(epics, "notify") as mock_notify:
                await pilot.press("r")
                mock_notify.assert_called_once()
                message = mock_notify.call_args[0][0]
                assert "changes loaded" in message
                assert "archived" in message


# ── Search & Filter ───────────────────────────────────────────────────────────


@pytest.fixture
def openspec_with_two_changes(tmp_path: Path) -> Path:
    """openspec/ with 2 active changes: 'view-search-filter' and 'perf-async-diffs'."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    for name in ("view-search-filter", "perf-async-diffs"):
        change = openspec / "changes" / name
        change.mkdir()
        (change / "proposal.md").write_text("# Proposal\n")
    return openspec


# Unit tests — pure helpers, no Textual app needed


def test_filter_changes_case_insensitive() -> None:
    """_filter_changes returns changes whose name contains query (case-insensitive)."""
    view = EpicsView([])
    changes = [
        Change(name="view-search-filter", path=Path("/tmp")),
        Change(name="perf-async-diffs", path=Path("/tmp")),
        Change(name="VIEW-HELP", path=Path("/tmp")),
    ]
    result = view._filter_changes(changes, "view")
    assert [c.name for c in result] == ["view-search-filter", "VIEW-HELP"]


def test_filter_changes_no_match() -> None:
    """_filter_changes returns empty list when no match."""
    view = EpicsView([])
    changes = [Change(name="perf-async-diffs", path=Path("/tmp"))]
    assert view._filter_changes(changes, "xyz") == []


def test_highlight_match_returns_text_with_bold_cyan() -> None:
    """REQ-13: _highlight_match wraps matching substring in bold cyan."""
    view = EpicsView([])
    result = view._highlight_match("view-search-filter", "search")
    assert isinstance(result, Text)
    plain = result.plain
    assert plain == "view-search-filter"
    # The span covering "search" should have bold cyan style
    spans = [(s.start, s.end, str(s.style)) for s in result._spans]
    match_span = next((s for s in spans if "cyan" in s[2]), None)
    assert match_span is not None
    assert plain[match_span[0] : match_span[1]] == "search"


def test_highlight_match_no_match_returns_plain_text() -> None:
    """_highlight_match returns plain Text when query not found in name."""
    view = EpicsView([])
    result = view._highlight_match("perf-async-diffs", "view")
    assert isinstance(result, Text)
    assert result.plain == "perf-async-diffs"
    assert result._spans == []


# TUI tests


async def test_search_slash_shows_input(openspec_with_change: Path) -> None:
    """REQ-01: pressing '/' makes the search Input visible."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            search_input = app.query_one("#search-input", Input)
            assert not search_input.display
            await pilot.press("/")
            assert search_input.display


async def test_search_filters_in_realtime(openspec_with_two_changes: Path) -> None:
    """REQ-03: typing in search input filters DataTable rows in real time."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_two_changes)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            assert table.row_count == 2
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "view"
            await pilot.pause()
            assert table.row_count == 1


async def test_search_escape_cancels(openspec_with_two_changes: Path) -> None:
    """REQ-04: Esc cancels search and restores full list."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_two_changes)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "view"
            await pilot.pause()
            assert table.row_count == 1
            await pilot.press("escape")
            await pilot.pause()
            assert table.row_count == 2
            assert not app.query_one("#search-input", Input).display


async def test_search_enter_confirms(openspec_with_two_changes: Path) -> None:
    """REQ-05: Enter confirms filter, hides Input, keeps filtered rows."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_two_changes)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "view"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert table.row_count == 1
            assert not app.query_one("#search-input", Input).display


async def test_search_no_results(openspec_with_two_changes: Path) -> None:
    """REQ-06: 0 results shows a 'No matches' placeholder row."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_two_changes)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "zzz-no-match"
            await pilot.pause()
            assert table.row_count == 1
            # The single row should be the "No matches" placeholder (no key)
            epics = app.query_one(EpicsView)
            assert epics._change_map == {}


async def test_refresh_clears_filter(openspec_with_two_changes: Path) -> None:
    """REQ-09: pressing 'r' clears the active filter."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_two_changes)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "view"
            await pilot.pause()
            assert table.row_count == 1
            await pilot.press("escape")  # cancel to return focus to DataTable
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert table.row_count == 2
            epics = app.query_one(EpicsView)
            assert epics._search_query == ""


# ── Multi-project separators ──────────────────────────────────────────────────


class _EpicsApp(App):
    """Minimal app that mounts EpicsView with given changes."""

    def __init__(self, changes: list[Change]) -> None:
        super().__init__()
        self._changes = changes

    def compose(self) -> ComposeResult:
        yield EpicsView(self._changes)


def _change(name: str, project: str) -> Change:
    return Change(name=name, path=Path("/tmp"), project=project, project_path=Path("/tmp") / project)


async def test_epics_multi_project_shows_separators() -> None:
    """Multi-project: one separator row per project is added to the table."""
    changes = [
        _change("change-a", "alpha"),
        _change("change-b", "beta"),
    ]
    app = _EpicsApp(changes)
    async with app.run_test():
        table = app.query_one(DataTable)
        # 2 changes + 2 separators (one per project)
        assert table.row_count == 4


async def test_epics_single_project_no_separators() -> None:
    """Single project: no separator rows, one row per change."""
    changes = [
        _change("change-a", "alpha"),
        _change("change-b", "alpha"),
    ]
    app = _EpicsApp(changes)
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.row_count == 2


async def test_epics_multi_project_no_project_field_no_separators() -> None:
    """Legacy mode (empty project field): no separators rendered."""
    changes = [
        Change(name="change-a", path=Path("/tmp")),
        Change(name="change-b", path=Path("/tmp")),
    ]
    app = _EpicsApp(changes)
    async with app.run_test():
        table = app.query_one(DataTable)
        assert table.row_count == 2


async def test_epics_multi_project_search_empty_group_shows_placeholder() -> None:
    """Multi-project search: group with no matches shows '(no active changes)' row."""
    changes = [
        _change("alpha-feature", "alpha"),
        _change("beta-work", "beta"),
    ]
    app = _EpicsApp(changes)
    async with app.run_test():
        epics = app.query_one(EpicsView)
        table = app.query_one(DataTable)
        epics._search_query = "alpha"
        epics._populate()
        # alpha: 1 separator + 1 match; beta: 1 separator + 1 placeholder = 4 rows
        assert table.row_count == 4
        assert "beta" not in epics._change_map


async def test_search_persists_on_toggle_archived(openspec_with_archive: Path) -> None:
    """REQ-10: filter persists when toggling archived changes."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_archive)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            # "my-change" matches "my", archived "old-change" does not
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "my"
            await pilot.pause()
            assert table.row_count == 1
            await pilot.press("escape")  # cancel search
            await pilot.pause()
            await pilot.press("a")  # show archived
            await pilot.pause()
            # re-activate search with same query
            await pilot.press("/")
            await pilot.pause()
            app.query_one("#search-input", Input).value = "my"
            await pilot.pause()
            # still only 1 match (archived "old-change" doesn't match "my")
            assert table.row_count == 1
