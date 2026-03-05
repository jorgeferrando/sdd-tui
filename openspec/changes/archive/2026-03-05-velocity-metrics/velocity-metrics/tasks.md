# Tasks: velocity-metrics

## Metadata
- **Change:** velocity-metrics
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/velocity.py` — dataclasses + compute_velocity + _get_change_dates
  - Commit: `[velocity-metrics] Add compute_velocity with throughput and lead time`

- [x] **T02** Crear `tests/test_velocity.py` — unit tests para compute_velocity
  - Commit: `[velocity-metrics] Add unit tests for compute_velocity`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/velocity.py` — VelocityView con barras Unicode y export E
  - Commit: `[velocity-metrics] Add VelocityView screen`
  - Depende de: T01

- [x] **T04** Modificar `src/sdd_tui/tui/epics.py` — binding V + action_velocity
  - Commit: `[velocity-metrics] Add V binding to EpicsView`
  - Depende de: T03

- [x] **T05** Crear `tests/test_tui_velocity.py` — TUI tests para VelocityView
  - Commit: `[velocity-metrics] Add TUI tests for VelocityView`
  - Depende de: T03

- [x] **T06** Modificar `tests/test_tui_epics.py` — añadir test del binding V
  - Commit: `[velocity-metrics] Add test for V binding in EpicsView`
  - Depende de: T04

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Bugs detectados en verify

- [x] **BUG01** `core/velocity.py` — project name vacío cuando archive_dir es una ruta relativa
  - Detectado: smoke test en verify (`Path('.').name == ''`)
  - Fix: añadir `.resolve()` al calcular `project_path`
  - Commit: `[velocity-metrics] Fix empty project name with relative archive paths`

## Notas

- Orden de implementación: core → tests core → TUI → epics → tests TUI → tests epics
- T02 antes de T03: valida el core antes de construir encima
- `_build_content` y `_build_markdown_report` van en `tui/velocity.py` como funciones privadas del módulo
- `statistics.median` de stdlib — sin imports nuevos
- Test de binding V en T06: verificar que `"V"` aparece en `EpicsView.BINDINGS`
