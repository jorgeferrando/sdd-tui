from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TodoItem:
    text: str
    done: bool


@dataclass
class TodoFile:
    title: str
    items: list[TodoItem] = field(default_factory=list)


def load_todos(openspec_path: Path) -> list[TodoFile]:
    todos_dir = openspec_path / "todos"
    if not todos_dir.exists():
        return []
    result = []
    for md_file in sorted(todos_dir.glob("*.md")):
        try:
            text = md_file.read_text(errors="replace")
            result.append(_parse_todo_file(text, md_file.stem))
        except Exception:
            continue
    return result


def _parse_todo_file(text: str, stem: str) -> TodoFile:
    title = stem
    items: list[TodoItem] = []
    for line in text.splitlines():
        stripped = line.strip()
        m_title = re.match(r"^#\s+(.+)$", stripped)
        if m_title and title == stem:
            title = m_title.group(1).strip()
            continue
        m_item = re.match(r"^- \[([ x])\] (.+)$", stripped)
        if m_item:
            items.append(TodoItem(text=m_item.group(2), done=m_item.group(1) == "x"))
    return TodoFile(title=title, items=items)
