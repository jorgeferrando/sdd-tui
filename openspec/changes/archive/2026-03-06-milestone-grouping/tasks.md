# Tasks: milestone-grouping

## Metadata
- **Change:** milestone-grouping
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/milestones.py` — `Milestone` dataclass + `load_milestones()` + `_parse_milestones()`
  - Commit: `[milestone-grouping] Add milestones reader`

- [x] **T02** Crear `tests/test_milestones.py` — 10 unit tests del parser
  - Commit: `[milestone-grouping] Add tests for milestones reader`
  - Depende de: T01

- [x] **T03** Modificar `src/sdd_tui/tui/epics.py` — añadir `_populate_by_milestone()` + rama milestone en `_populate()`
  - Commit: `[milestone-grouping] Group changes by milestone in EpicsView`
  - Depende de: T01

- [x] **T04** Crear `tests/test_tui_epics_milestones.py` — 9 TUI tests de milestone grouping
  - Commit: `[milestone-grouping] Add TUI tests for milestone grouping`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest` → 336 passed

## Notas

- T01 antes que T02 y T03 — ambos dependen del módulo core
- T03 antes que T04 — TUI tests verifican comportamiento implementado
- Sin nueva binding de teclado — activación automática por presencia de milestones.yaml
