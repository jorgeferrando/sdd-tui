# Tasks: View 7 — Mostrar/ocultar archivados

## Metadata
- **Change:** view-7-show-archived
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/models.py` — añadir `archived: bool = False` a `Change`
  - Commit: `[view-7] Add archived flag to Change model`

- [x] **T02** Modificar `src/sdd_tui/core/reader.py` — `load(include_archived=False)` carga también `archive/`
  - Commit: `[view-7] Load archived changes from archive/ when requested`
  - Depende de: T01

- [x] **T03** Modificar `tests/test_reader.py` — añadir tests para `include_archived=True`
  - Commit: `[view-7] Add tests for include_archived in OpenspecReader`
  - Depende de: T02

- [x] **T04** Modificar `src/sdd_tui/tui/app.py` — propagar `include_archived` a través de `refresh_changes` y `_load_changes`
  - Commit: `[view-7] Propagate include_archived flag through app layer`
  - Depende de: T02

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — toggle `a`, `_show_archived`, `_change_map`, `row_key`, separator
  - Commit: `[view-7] Add archived toggle and key-based row selection to EpicsView`
  - Depende de: T04

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test
  - `uv run pytest`
  - `uv run sdd-tui` → pulsar `a` → ver archivados → pulsar `a` → ocultar → Enter en un archivado → View 2

## Notas

- T03 y T04 son independientes entre sí (ambos dependen de T02), pueden hacerse en cualquier orden
- El separador `── archived ──` no tiene key → Enter sobre él no hace nada (comportamiento natural de DataTable)
