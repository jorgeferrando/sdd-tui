# Tasks: decision-status-badges

## Metadata
- **Change:** decision-status-badges
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/spec_parser.py` — añadir `Decision.status` + refactor parseo a split-based
  - Commit: `[decision-status-badges] Add status field to Decision, parse 3/4-col tables`

- [x] **T02** Modificar `tests/test_spec_parser.py` — tests para parseo 4 cols, backwards compat 3 cols, valores mixed
  - Commit: `[decision-status-badges] Add tests for Decision.status parsing`
  - Depende de: T01

- [x] **T03** Modificar `src/sdd_tui/tui/spec_evolution.py` — `_status_badge()` + badges en `DecisionsTimeline._populate()`
  - Commit: `[decision-status-badges] Render status badges in DecisionsTimeline`
  - Depende de: T01

- [x] **T04** Modificar `tests/test_tui_spec_evolution.py` — tests de `_status_badge()` y render de badges
  - Commit: `[decision-status-badges] Add tests for status badge rendering`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest`

## Notas

- T02 y T03 son independientes entre sí (pueden hacerse en cualquier orden)
- Verificar con grep si `_TABLE_ROW` es importado directamente en tests antes de eliminarlo
- `Decision("X", "Y", "Z")` sigue compilando — `status` tiene default, sin cambios en tests existentes
