# Tasks: Async Diff Loading

## Metadata
- **Change:** perf-async-diffs
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Añadir tests en `tests/test_tui_change_detail.py` — cobertura del flujo async (RED)
  - Tres tests: placeholder inmediato, diff tras worker, worker cancelado en nav rápida
  - Commit: `[perf-async-diffs] Add tests for async diff loading`

- [x] **T02** Refactorizar `src/sdd_tui/tui/change_detail.py` — worker async con @work(thread=True, exclusive=True) (GREEN)
  - `on_data_table_row_highlighted`: muestra placeholder + llama worker
  - `_load_diff_worker(task)`: ejecuta git en hilo, llama `call_from_thread`
  - `_update_diff_panel(content)`: actualiza DiffPanel desde el event loop
  - Commit: `[perf-async-diffs] Load diffs asynchronously with run_worker`

## Quality Gate Final

- [x] **QG** Ejecutar tests completos
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest tests/ -v`

## Notas

- Orden TDD: T01 (tests RED) → T02 (implementación GREEN)
- T01 depende de que los tests usen `pilot.pause()` para dejar que el worker complete
- El worker recibe un objeto `Task` (no `task_id`) — evita `query_one` desde el hilo
- `@work` requiere `from textual import work` — añadir al import block
- `exclusive=True` es suficiente para la cancelación; no hace falta gestión manual
