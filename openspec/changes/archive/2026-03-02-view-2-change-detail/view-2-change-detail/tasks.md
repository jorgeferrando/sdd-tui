# Tasks: View 2 — Change detail con task states y git info

## Metadata
- **Change:** view-2-change-detail
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-02

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/models.py` — añadir CommitInfo, TaskGitState; extender Task y Change
  - Commit: `[view-2] Extend models with CommitInfo, TaskGitState, task git fields`

- [x] **T02** Modificar `tests/test_pipeline.py` — añadir tests para bold format y commit hints (RED)
  - Commit: `[view-2] Add tests for bold TXX format and commit hints`
  - Depende de: T01

- [x] **T03** Modificar `src/sdd_tui/core/pipeline.py` — fix regex bold, capturar commit hints (GREEN)
  - Commit: `[view-2] Fix TaskParser for bold format and capture commit hints`
  - Depende de: T02

- [x] **T04** Crear `tests/test_git_reader.py` — tests de find_commit() con mock subprocess (RED)
  - Commit: `[view-2] Add tests for GitReader.find_commit`
  - Depende de: T01

- [x] **T05** Modificar `src/sdd_tui/core/git_reader.py` — añadir find_commit() (GREEN)
  - Commit: `[view-2] Add GitReader.find_commit`
  - Depende de: T04

- [x] **T06** Modificar `src/sdd_tui/tui/app.py` — añadir _parser, _load_tasks(), importar ChangeDetailScreen
  - Commit: `[view-2] Add task loading with git states to SddTuiApp`
  - Depende de: T03, T05

- [x] **T07** Modificar `src/sdd_tui/tui/epics.py` — añadir binding Enter → action_select_change()
  - Commit: `[view-2] Add Enter navigation to change detail in EpicsView`
  - Depende de: T06

- [x] **T08** Crear `src/sdd_tui/tui/change_detail.py` — ChangeDetailScreen + TaskListPanel + PipelinePanel
  - Commit: `[view-2] Add ChangeDetailScreen with task list and pipeline panels`
  - Depende de: T07

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test de navegación
  - `uv run pytest`
  - `uv run sdd-tui` → Enter en un change → ver detalle → Esc → volver

## Bugs post-archive

- [x] **BUG01** `src/sdd_tui/tui/epics.py` — Enter no navega: DataTable consume el evento antes que EpicsView
  - Detectado: smoke test manual tras archive
  - Fix: reemplazar `Binding("enter", "select_change")` + `action_select_change()` por `on_data_table_row_selected()`
  - Commit: `[view-2] Fix Enter navigation using DataTable.RowSelected event`

## Notas

- Orden TDD: test (RED) → implementación (GREEN)
- T02 y T04 pueden escribirse en paralelo (ambos dependen solo de T01)
- T06 no puede empezar hasta que T03 y T05 estén listos (usa TaskParser y GitReader)
- T08 es el último: necesita que T07 esté listo para que la navegación funcione end-to-end
