# Tasks: TUI Tests

## Metadata
- **Change:** tui-tests
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** `pyproject.toml` — añadir pytest-asyncio y asyncio_mode = "auto"
  - Commit: `[tui-tests] Add pytest-asyncio with asyncio_mode=auto`

- [x] **T02** `tests/conftest.py` — añadir fixtures TUI (openspec_with_change, openspec_with_archive)
  - Commit: `[tui-tests] Add TUI fixtures to conftest`
  - Depende de: T01

- [x] **T03** `tests/test_tui_epics.py` — tests de EpicsView (REQ-04..08)
  - Commit: `[tui-tests] Add EpicsView integration tests`
  - Depende de: T02

- [x] **T04** `tests/test_tui_change_detail.py` — tests de ChangeDetailScreen (REQ-09..12)
  - Commit: `[tui-tests] Add ChangeDetailScreen integration tests`
  - Depende de: T02

- [x] **T05** `tests/test_tui_spec_health.py` — tests de SpecHealthScreen (REQ-13..15)
  - Commit: `[tui-tests] Add SpecHealthScreen integration tests`
  - Depende de: T02

- [x] **T06** `tests/test_tui_spec_evolution.py` — tests de SpecEvolutionScreen (REQ-16..18)
  - Commit: `[tui-tests] Add SpecEvolutionScreen integration tests`
  - Depende de: T02

- [x] **T07** `tests/test_tui_doc_viewer.py` — tests de DocumentViewerScreen (REQ-19..21)
  - Commit: `[tui-tests] Add DocumentViewerScreen integration tests`
  - Depende de: T02

## Notas

- Orden obligatorio: T01 y T02 antes de cualquier test (T03..T07 pueden ir en paralelo lógico)
- `ChangeDetailScreen.__init__` recibe `Change` object — construirlo desde fixture con `TaskParser` + `PipelineInferer`
- `SpecHealthScreen.__init__` recibe `openspec_path: Path` — puede construirse directamente
- `DocumentViewerScreen.__init__` recibe `file_path: Path` y `title: str` — puede construirse directamente sin nav
- Mock de GitReader: `patch("sdd_tui.tui.app.GitReader")` para todos los tests que lancen `SddTuiApp`
- Si un test falla por `Path.cwd()` en actions → parchear también `Path.cwd` o ignorar ese assert
