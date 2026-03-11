from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import Static

from sdd_tui.core.todos import TodoFile, TodoItem
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.todos import TodosScreen, _build_content


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


# --- Unit tests for _build_content ---


def test_build_content_empty_shows_message() -> None:
    """REQ-TU-06: empty todos list shows 'No todos found'."""
    text = _build_content([])
    assert "No todos found" in str(text)


def test_build_content_shows_header_with_progress() -> None:
    """REQ-TU-03: header shows title and [done/total] count."""
    todos = [
        TodoFile(
            title="Ideas",
            items=[TodoItem("item a", done=True), TodoItem("item b", done=False)],
        )
    ]
    content = str(_build_content(todos))
    assert "Ideas" in content
    assert "[1/2]" in content


def test_build_content_done_items_have_check() -> None:
    """REQ-TU-04: completed items show ✓ prefix."""
    todos = [TodoFile(title="T", items=[TodoItem("done thing", done=True)])]
    content = str(_build_content(todos))
    assert "✓" in content
    assert "done thing" in content


def test_build_content_pending_items_have_dot() -> None:
    """REQ-TU-05: pending items show · prefix."""
    todos = [TodoFile(title="T", items=[TodoItem("pending thing", done=False)])]
    content = str(_build_content(todos))
    assert "·" in content
    assert "pending thing" in content


def test_build_content_all_done_shows_full_count() -> None:
    """REQ-TU-03: all items done shows [N/N]."""
    todos = [
        TodoFile(
            title="Done",
            items=[TodoItem("a", done=True), TodoItem("b", done=True)],
        )
    ]
    content = str(_build_content(todos))
    assert "[2/2]" in content


def test_build_content_file_with_no_items() -> None:
    """REQ-TU-03: file with no items shows [0/0]."""
    todos = [TodoFile(title="Empty", items=[])]
    content = str(_build_content(todos))
    assert "Empty" in content
    assert "[0/0]" in content


def test_build_content_multiple_files() -> None:
    """REQ-TU-03: multiple files each have their own header."""
    todos = [
        TodoFile(title="File A", items=[TodoItem("x", done=False)]),
        TodoFile(title="File B", items=[TodoItem("y", done=True)]),
    ]
    content = str(_build_content(todos))
    assert "File A" in content
    assert "File B" in content


# --- TUI integration tests ---


async def test_todos_screen_opens_from_epics(openspec_with_change: Path) -> None:
    """REQ-TU-01: pressing T in EpicsView pushes TodosScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("T")
            assert isinstance(app.screen, TodosScreen)


async def test_todos_screen_no_todos_shows_message(openspec_with_change: Path) -> None:
    """REQ-TU-06: TodosScreen shows 'No todos found' when no todos/ dir."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("T")
            content = app.screen.query_one("#todos-content", Static)
            assert "No todos found" in str(content.render())


async def test_todos_screen_esc_returns_to_epics(openspec_with_change: Path) -> None:
    """REQ-TU-02: Esc in TodosScreen pops back to EpicsView."""
    from sdd_tui.tui.epics import EpicsView

    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("T")
            assert isinstance(app.screen, TodosScreen)
            await pilot.press("escape")
            assert app.screen.query_one(EpicsView) is not None
