# Tasks: Progress Dashboard

## Metadata
- **Change:** progress-dashboard
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Crear `tests/test_progress.py` — tests RED para `compute_progress()`
  - Commit: `[progress-dashboard] Add RED tests for compute_progress`

- [x] **T02** Crear `src/sdd_tui/core/progress.py` — `ProgressReport`, `ChangeProgress`, `compute_progress()`
  - Commit: `[progress-dashboard] Add compute_progress and ProgressReport`
  - Depende de: T01

- [x] **T03** Crear `tests/test_tui_progress.py` — tests RED para `ProgressDashboard` y binding `P`
  - Commit: `[progress-dashboard] Add RED tests for ProgressDashboard and P binding`
  - Depende de: T02

- [x] **T04** Crear `src/sdd_tui/tui/progress.py` — `ProgressDashboard`, `_build_content()`, `_build_markdown_report()`
  - Commit: `[progress-dashboard] Add ProgressDashboard screen`
  - Depende de: T03

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — añadir binding `P` y `action_progress()`
  - Commit: `[progress-dashboard] Add P binding to open ProgressDashboard`
  - Depende de: T04

## Bugs post-T05

- [x] **BUG01** `tests/test_tui_progress.py` — patch incorrecto en test_progress_dashboard_empty_shows_message
  - Fix: usar `sdd_tui.tui.app.load_all_changes` en lugar de `sdd_tui.core.reader.load_all_changes`
  - Commit: `[progress-dashboard] Fix patch path in empty changes TUI test`

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- TDD: T01 y T03 escriben tests RED, T02 y T04 los ponen en GREEN
- `compute_progress` es función pura — tests sin mocks ni fixtures de disco
- Patrón de referencia: `core/velocity.py` + `tui/velocity.py`
- Tests TUI: mismo `_git_mock()` que `test_tui_velocity.py`
