# Design: View 3 — Commit diff inline

## Metadata
- **Change:** view-3-commit-diff
- **Jira:** N/A
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-03
- **Estado:** draft

## Resumen Técnico

Dos cambios independientes:

1. **Core** — `GitReader.get_diff()`: función que ejecuta `git show {hash}` y
   retorna el output como string, siguiendo el mismo patrón que `find_commit()`.

2. **TUI** — `ChangeDetailScreen` refactorizado: `TaskListPanel` pasa de
   `Static` a `DataTable` (coherente con `EpicsView`). El layout añade un
   `DiffPanel` inferior que reacciona a `DataTable.RowHighlighted`.

## Arquitectura

```
ChangeDetailScreen
├── Vertical (layout exterior)
│   ├── Horizontal (60% altura)
│   │   ├── TaskListPanel (DataTable, 2fr ancho)  ← reemplaza Static
│   │   └── PipelinePanel (Static, 1fr ancho)     ← sin cambios
│   └── DiffPanel (ScrollableContainer, 40% altura) ← nuevo
│
on DataTable.RowHighlighted
  → TaskListPanel.get_task_for_row(row_key) → Task | None
  → if task.git_state == COMMITTED:
      GitReader().get_diff(task.commit.hash, cwd) → str | None
      DiffPanel.update(diff_text)
  → if task.git_state == PENDING:
      DiffPanel.update("Not committed yet")
  → if get_diff returns None:
      DiffPanel.update("Could not load diff")
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| — | — | No hay archivos nuevos |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `tests/test_git_reader.py` | Añadir tests para `get_diff()` | TDD — RED antes de implementar |
| `src/sdd_tui/core/git_reader.py` | Añadir `get_diff(commit_hash, cwd)` | Nueva función requerida por View 3 |
| `src/sdd_tui/tui/change_detail.py` | Refactorizar layout y widgets | TaskListPanel → DataTable + DiffPanel nuevo |

## Scope

- **Total archivos:** 3
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Sin dependencias externas nuevas
- Textual ya importado — `DataTable.RowHighlighted` es evento nativo (como `RowSelected` ya usado en `EpicsView`)

## Patrones Aplicados

- **`subprocess.run` con captura de errores**: igual que `find_commit()` y `is_clean()` — mismo patrón, misma clase.
- **`DataTable` con `cursor_type="row"`**: igual que `EpicsView` — ya validado en view-2.
- **`on_data_table_row_highlighted`**: análogo a `on_data_table_row_selected` en `epics.py`, pero para hover.
- **`ScrollableContainer` + `Static` interior**: igual que el `TaskListPanel` actual (solo se mueve al `DiffPanel`).

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `RowHighlighted` (hover) | `RowSelected` (Enter) | Diff se actualiza al navegar sin requerir Enter — más fluido |
| Filas de amendment sin `key` | Filtrar separadores del DataTable | Mantiene la posición visual correcta; sin `key` no disparan eventos |
| `DiffPanel` actualizable vía método `update_diff(text)` | Recrear widget | Más eficiente — solo actualiza el `Static` interior |
| `git show --no-color` | `git show` raw | Evita códigos ANSI si el usuario tiene `color.ui=always` en git config |
| `TaskListPanel` guarda `dict[str, Task]` para lookup por row key | Buscar en lista lineal | O(1) lookup al recibir `RowHighlighted` |

## Detalle de Implementación

### `GitReader.get_diff()`

```python
def get_diff(self, commit_hash: str | None, cwd: Path) -> str | None:
    if not commit_hash:
        return None
    try:
        result = subprocess.run(
            ["git", "show", "--no-color", commit_hash],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except FileNotFoundError:
        return None
```

### `TaskListPanel` — DataTable

```python
class TaskListPanel(Widget):
    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks
        self._row_task_map: dict[str, Task] = {}  # row_key → Task

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row", show_header=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("state", "hash", "id", "desc")
        for task in self._tasks:
            if task.amendment != last_amendment:  # separador
                table.add_row("──", "amendment:", task.amendment, "──")
                # sin key → no seleccionable
            else:
                key = task.id
                self._row_task_map[key] = task
                table.add_row(state, hash_str, task.id, task.description, key=key)

    def get_task(self, row_key: str) -> Task | None:
        return self._row_task_map.get(row_key)
```

### `DiffPanel`

```python
class DiffPanel(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield Static("", id="diff-content")

    def update_diff(self, text: str) -> None:
        self.query_one("#diff-content", Static).update(text)
```

### `ChangeDetailScreen` — event handler

```python
def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    if event.row_key is None or event.row_key.value is None:
        return
    task = self.query_one(TaskListPanel).get_task(event.row_key.value)
    if task is None:  # separador de amendment
        return
    diff_panel = self.query_one(DiffPanel)
    if task.git_state == TaskGitState.COMMITTED and task.commit:
        diff = GitReader().get_diff(task.commit.hash, Path.cwd())
        diff_panel.update_diff(diff or "Could not load diff")
    else:
        diff_panel.update_diff("Not committed yet")
```

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_get_diff_returns_none_for_none_hash` | `test_git_reader.py` | `get_diff(None, path)` → `None` |
| `test_get_diff_returns_output_on_success` | `test_git_reader.py` | mock subprocess → retorna stdout |
| `test_get_diff_returns_none_on_error` | `test_git_reader.py` | returncode != 0 → `None` |
| `test_get_diff_returns_none_when_git_missing` | `test_git_reader.py` | `FileNotFoundError` → `None` |

## Notas de Implementación

- El `cwd` para `get_diff()` en la TUI: usar `Path.cwd()` (el repo donde corre sdd-tui). La app ya usa esta convención en `_load_tasks()`.
- El `row_key.value` en Textual es el string key pasado a `add_row(key=...)`. Si la fila no tiene key, `row_key` puede ser `None` o tener un valor generado — verificar con `row_key.value` antes de buscar en el map.
- Los separadores de amendment en el DataTable: añadirlos con `add_row(...)` sin argumento `key` para que no sean seleccionables desde el map. El cursor puede posicionarse en ellos, pero `get_task()` retornará `None` (safe).
