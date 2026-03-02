# Tasks: Bootstrap — Project setup + openspec reader + Epics view

## Metadata
- **Change:** bootstrap
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-02

## Tareas de Implementación

- [ ] **T01** Crear `pyproject.toml` — setup del proyecto (uv, dependencias, entrypoint CLI)
  - Commit: `[bootstrap] Add pyproject.toml`

- [ ] **T02** Crear `src/sdd_tui/core/models.py` — dataclasses y enums del dominio
  - Commit: `[bootstrap] Add core models`
  - Depende de: T01

- [ ] **T03** Crear `tests/conftest.py` — fixture `openspec_dir` con estructura mínima en tmp_path
  - Commit: `[bootstrap] Add test fixtures`
  - Depende de: T02

- [ ] **T04** Crear `tests/test_reader.py` — tests del reader (RED)
  - Commit: `[bootstrap] Add reader tests`
  - Depende de: T03

- [ ] **T05** Crear `src/sdd_tui/core/reader.py` — OpenspecReader (GREEN)
  - Commit: `[bootstrap] Add OpenspecReader`
  - Depende de: T04

- [ ] **T06** Crear `tests/test_pipeline.py` — tests de pipeline + task parser (RED)
  - Commit: `[bootstrap] Add pipeline tests`
  - Depende de: T03

- [ ] **T07** Crear `src/sdd_tui/core/git_reader.py` — GitReader vía subprocess
  - Commit: `[bootstrap] Add GitReader`
  - Depende de: T02

- [ ] **T08** Crear `src/sdd_tui/core/pipeline.py` — PipelineInferer + TaskParser (GREEN)
  - Commit: `[bootstrap] Add PipelineInferer and TaskParser`
  - Depende de: T06, T07

- [ ] **T09** Crear `src/sdd_tui/tui/app.py` — SddTuiApp + main() entrypoint
  - Commit: `[bootstrap] Add TUI app entrypoint`
  - Depende de: T05, T08

- [ ] **T10** Crear `src/sdd_tui/tui/epics.py` — EpicsView (DataTable con pipeline)
  - Commit: `[bootstrap] Add EpicsView`
  - Depende de: T09

## Quality Gate Final

- [ ] **QG** Ejecutar tests y verificar arranque
  - `uv run pytest`
  - `uv run sdd-tui` (smoke test visual)

## Notas

- Orden TDD: test (RED) → implementación (GREEN)
- T04 y T06 pueden escribirse en paralelo (ambos dependen de T03)
- T07 puede escribirse en paralelo con T04/T06 (no tiene tests propios)
- Los `__init__.py` vacíos se crean junto con el primer archivo de cada paquete
- Rama: trabajamos directamente en `main` (este change es el bootstrap del proyecto)
