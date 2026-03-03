# Tasks: Cleanup — Remove transport adapters

## Metadata
- **Change:** cleanup-remove-transports
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [ ] **T01** Eliminar `src/sdd_tui/core/transports.py` y `tests/test_transports.py`
  - Commit: `[cleanup] Remove transport adapters — replaced by clipboard approach`

## Quality Gate Final

- [ ] **QG** `uv run pytest` — 24 tests en verde (los 16 de transports eliminados)
