from __future__ import annotations

from pathlib import Path

from sdd_tui.core.todos import TodoItem, _parse_todo_file, load_todos


def test_load_todos_missing_dir(tmp_path: Path) -> None:
    """REQ-TD-02: returns [] if openspec/todos/ does not exist."""
    result = load_todos(tmp_path)
    assert result == []


def test_load_todos_empty_dir(tmp_path: Path) -> None:
    """REQ-TD-01: returns [] if todos/ exists but has no .md files."""
    (tmp_path / "todos").mkdir()
    result = load_todos(tmp_path)
    assert result == []


def test_load_todos_ignores_non_md(tmp_path: Path) -> None:
    """REQ-TD-06: non-.md files are ignored."""
    todos_dir = tmp_path / "todos"
    todos_dir.mkdir()
    (todos_dir / "notes.txt").write_text("- [ ] item")
    result = load_todos(tmp_path)
    assert result == []


def test_load_todos_single_file(tmp_path: Path) -> None:
    """REQ-TD-01: parses a single .md file."""
    todos_dir = tmp_path / "todos"
    todos_dir.mkdir()
    (todos_dir / "ideas.md").write_text("# Ideas\n\n- [ ] Write docs\n- [x] Setup CI\n")
    result = load_todos(tmp_path)
    assert len(result) == 1
    assert result[0].title == "Ideas"
    assert len(result[0].items) == 2


def test_load_todos_sorted_alphabetically(tmp_path: Path) -> None:
    """REQ-TD-01: files returned in alphabetical order."""
    todos_dir = tmp_path / "todos"
    todos_dir.mkdir()
    (todos_dir / "zzz.md").write_text("- [ ] last")
    (todos_dir / "aaa.md").write_text("- [ ] first")
    result = load_todos(tmp_path)
    assert result[0].title == "aaa"
    assert result[1].title == "zzz"


def test_parse_todo_file_heading(tmp_path: Path) -> None:
    """REQ-TD-04: title comes from first # heading."""
    tf = _parse_todo_file("# My Ideas\n\n- [ ] item one\n", "fallback")
    assert tf.title == "My Ideas"


def test_parse_todo_file_stem_fallback() -> None:
    """REQ-TD-04: title falls back to stem if no heading."""
    tf = _parse_todo_file("- [ ] item one\n", "ideas")
    assert tf.title == "ideas"


def test_parse_todo_file_items_done_and_pending() -> None:
    """REQ-TD-05: parses [x] as done=True and [ ] as done=False."""
    tf = _parse_todo_file("- [x] Done item\n- [ ] Pending item\n", "stem")
    assert len(tf.items) == 2
    assert tf.items[0] == TodoItem(text="Done item", done=True)
    assert tf.items[1] == TodoItem(text="Pending item", done=False)


def test_parse_todo_file_no_items() -> None:
    """REQ-TD-07: file with no checkbox lines yields items=[]."""
    tf = _parse_todo_file("# Title\n\nSome plain text here.\n", "stem")
    assert tf.title == "Title"
    assert tf.items == []


def test_parse_todo_file_ignores_other_lines() -> None:
    """REQ-TD-05: non-checkbox lines are ignored."""
    text = "# Title\n\nsome prose\n\n- [ ] real item\n\n## section\n"
    tf = _parse_todo_file(text, "stem")
    assert len(tf.items) == 1
    assert tf.items[0].text == "real item"


def test_parse_todo_file_multiple_headings_uses_first() -> None:
    """REQ-TD-04: only the first # heading is used as title."""
    text = "# First\n# Second\n- [ ] item\n"
    tf = _parse_todo_file(text, "stem")
    assert tf.title == "First"


def test_load_todos_file_with_no_items(tmp_path: Path) -> None:
    """REQ-TD-07: file exists but has no checkbox lines → included with items=[]."""
    todos_dir = tmp_path / "todos"
    todos_dir.mkdir()
    (todos_dir / "empty.md").write_text("# Empty list\n\nJust some notes.\n")
    result = load_todos(tmp_path)
    assert len(result) == 1
    assert result[0].title == "Empty list"
    assert result[0].items == []
