# Tasks: View 1 — Search & Filter

## Metadata
- **Change:** view-search-filter
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/tui/epics.py` — añadir modo búsqueda `/` con Input, filtrado en tiempo real y highlight
  - Commit: `[view-search-filter] Add search mode with real-time filter and match highlight`

- [x] **T02** Modificar `tests/test_tui_epics.py` — añadir tests para búsqueda, filtrado, highlight y edge cases
  - Commit: `[view-search-filter] Add tests for search filter in EpicsView`
  - Depende de: T01

## Quality Gate Final

- [x] **QG** Ejecutar tests completos — 111 passed
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest tests/ -v`

## Notas

- T01 es autocontenido: toda la lógica vive en `epics.py` (estado, helpers, actions, handlers)
- Los helpers `_filter_changes` y `_highlight_match` son métodos de `EpicsView` — testables sin correr la app Textual completa
- Gotcha: `on_key` debe llamar `event.stop()` antes de `action_cancel_search()` para evitar que Esc se propague a la pila de pantallas
- Gotcha: `Input` de Textual tiene altura mínima de 3 — no usar `height: 1` en el CSS
