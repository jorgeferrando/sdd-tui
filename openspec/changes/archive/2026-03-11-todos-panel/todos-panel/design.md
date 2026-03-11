# Design: todos-panel

## Metadata
- **Change:** todos-panel
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-11
- **Estado:** draft

## Resumen Técnico

Se añade soporte para `openspec/todos/*.md` en dos capas:

1. **`core/todos.py`** — módulo puro con `load_todos(openspec_path)`. Sigue exactamente el patrón de `milestones.py`: escanea un subdirectorio de `openspec/`, parsea con stdlib (regex), retorna lista de dataclasses, degradación silenciosa si el directorio no existe.

2. **`tui/todos.py`** — pantalla `TodosScreen`. Sigue exactamente el patrón de `ProgressDashboard`: `Screen` + `ScrollableContainer(Static)` + función pura `_build_content()` que devuelve `rich.Text`.

3. **`tui/epics.py`** — binding `T` + `action_todos()` con import lazy, siguiendo el patrón de `action_progress()`.

## Arquitectura

```
EpicsView (tui/epics.py)
  T key → action_todos()
    → push_screen(TodosScreen)

TodosScreen (tui/todos.py)
  on_mount()
    → load_todos(app._openspec_path)   [core/todos.py]
    → _build_content(todos) → rich.Text
    → Static.update(text)

load_todos(openspec_path: Path)
  → scan openspec/todos/*.md
  → _parse_todo_file(text, stem) → TodoFile
  → return list[TodoFile]
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/todos.py` | Módulo core | `TodoItem`, `TodoFile`, `load_todos()`, `_parse_todo_file()` |
| `src/sdd_tui/tui/todos.py` | Screen TUI | `TodosScreen`, `_build_content()` |
| `tests/test_core_todos.py` | Tests unitarios | Cobertura de `load_todos` y `_parse_todo_file` |
| `tests/test_tui_todos.py` | Tests integración TUI | Navegación `T`, render vacío, render con todos |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir `Binding("T", "todos", "Todos")` + `action_todos()` | Punto de entrada desde View 1 |

## Scope

- **Total archivos:** 5 (2 nuevos de código + 2 de tests + 1 modificado)
- **Resultado:** Ideal (< 10)

## Implementación detallada

### `core/todos.py`

```python
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
```

### `tui/todos.py`

```python
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sdd_tui.core.todos import TodoFile, load_todos


class TodosScreen(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="todos-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — todos"
        todos = load_todos(self.app._openspec_path)  # type: ignore[attr-defined]
        self.query_one("#todos-content", Static).update(_build_content(todos))

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()


def _build_content(todos: list[TodoFile]) -> Text:
    if not todos:
        return Text("No todos found")

    text = Text()
    for i, tf in enumerate(todos):
        done = sum(1 for item in tf.items if item.done)
        total = len(tf.items)
        text.append(f"── {tf.title} [{done}/{total}] ──\n", style="bold cyan")
        for item in tf.items:
            if item.done:
                text.append(f"  ✓ {item.text}\n", style="dim")
            else:
                text.append(f"  · {item.text}\n")
        if i < len(todos) - 1:
            text.append("\n")
    return text
```

### `tui/epics.py` — cambio mínimo

En `BINDINGS` (después de `"P"`, antes de `"/"`):
```python
Binding("T", "todos", "Todos"),
```

Nuevo método (después de `action_progress`):
```python
def action_todos(self) -> None:
    from sdd_tui.tui.todos import TodosScreen
    self.app.push_screen(TodosScreen())
```

## Patrones Aplicados

- **`milestones.py` como referencia para `core/todos.py`**: mismo patrón de `load_X` + `_parse_X` con degradación silenciosa.
- **`ProgressDashboard` como referencia para `tui/todos.py`**: `Screen` + `ScrollableContainer(Static)` + `_build_content()` puro testeable.
- **Import lazy en `action_todos()`**: consistente con todos los `action_*` que hacen `push_screen` en `epics.py`.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| `ScrollableContainer + Static` | `DataTable` | Solo lectura, sin drill-down; patrón más simple |
| `rich.Text` en `_build_content()` | Markdown | Control exacto de estilos `dim`/`bold` por ítem |
| `load_todos` en `on_mount` (no constructor) | Pasar data al constructor | Consistente con `ProgressDashboard`; la pantalla se refresca en cada push |
| `openspec/todos/` con múltiples `.md` | Un único `todos.md` | Permite categorías independientes |
| Binding `T` | Otra tecla | Semántico (Todos), libre en EpicsView |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_load_todos_missing_dir` | Unit | Retorna `[]` si `openspec/todos/` no existe |
| `test_load_todos_empty_dir` | Unit | Retorna `[]` si directorio vacío |
| `test_parse_todo_file_with_heading` | Unit | `title` = primer `# heading` |
| `test_parse_todo_file_stem_fallback` | Unit | `title` = stem si sin heading |
| `test_parse_todo_file_items` | Unit | Items `[x]` y `[ ]` parseados correctamente |
| `test_parse_todo_file_no_items` | Unit | `TodoFile(title=..., items=[])` |
| `test_build_content_empty` | Unit | "No todos found" |
| `test_build_content_with_todos` | Unit | Header con `[done/total]`, ítems con `✓`/`·` |
| `test_tui_todos_navigation` | TUI | `T` → `TodosScreen`, `Esc` → `EpicsView` |
| `test_tui_todos_no_todos` | TUI | Render muestra "No todos found" |

## Notas de Implementación

- `app._openspec_path` está disponible en la app (establecido en `SddTuiApp`) — mismo acceso que usa `ProgressDashboard`.
- Los tests TUI usan fixture `openspec_with_change` del `conftest.py`; para todos se añade un subdirectorio `todos/` con archivos `.md` de prueba.
- El archivo de ejemplo en `openspec/todos/` se crea como fixture de test — no hay que incluirlo en el repo.
