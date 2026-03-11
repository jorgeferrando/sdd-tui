# Tasks: todos-panel

## Metadata
- **Change:** todos-panel
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/todos.py` — `TodoItem`, `TodoFile`, `load_todos()`, `_parse_todo_file()`
  - Commit: `[todos-panel] Add todos reader`

- [x] **T02** Crear `tests/test_core_todos.py` — tests unitarios de `load_todos` y `_parse_todo_file`
  - Commit: `[todos-panel] Add tests for todos reader`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/todos.py` — `TodosScreen`, `_build_content()`
  - Commit: `[todos-panel] Add TodosScreen`
  - Depende de: T01

- [x] **T04** Crear `tests/test_tui_todos.py` — tests TUI de navegación y render
  - Commit: `[todos-panel] Add TUI tests for TodosScreen`
  - Depende de: T03

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — binding `T` + `action_todos()`
  - Commit: `[todos-panel] Add T binding for TodosScreen in EpicsView`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest`

## Notas

- T01 y T02 son independientes de T03/T04/T05 — se pueden hacer primero sin tocar TUI.
- T05 debe ir después de T03 (import de `TodosScreen`).
- No hay `openspec/todos/` de ejemplo en el repo — los tests crean fixtures in-memory.
