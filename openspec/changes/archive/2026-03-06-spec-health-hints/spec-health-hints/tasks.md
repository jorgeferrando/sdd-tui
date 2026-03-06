# Tasks: spec-health-hints

## Metadata
- **Change:** spec-health-hints
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Añadir tests RED para `repair_hints()` en `tests/test_metrics.py`
  - Commit: `[spec-health-hints] Add RED tests for repair_hints`

- [x] **T02** Implementar `repair_hints()` en `core/metrics.py` (GREEN)
  - Commit: `[spec-health-hints] Add repair_hints to core/metrics`

- [x] **T03** Añadir tests RED para columna HINT en `tests/test_tui_spec_health.py`
  - Commit: `[spec-health-hints] Add RED tests for HINT column in SpecHealthScreen`

- [x] **T04** Implementar columna HINT en `tui/spec_health.py` (GREEN)
  - Commit: `[spec-health-hints] Add HINT column to SpecHealthScreen`

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- T01 antes de T02: TDD, tests deben fallar antes de implementar
- T03 antes de T04: mismo patrón TDD para la capa TUI
- `repair_hints` necesita importar `Change` y `PhaseState` desde `core/models`
- En T04, todos los `table.add_row(separador)` necesitan un argumento `""` extra (7 columnas total)
