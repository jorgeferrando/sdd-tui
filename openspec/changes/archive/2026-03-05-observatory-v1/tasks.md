# Tasks: observatory-v1 — Multi-project Support

## Metadata
- **Change:** observatory-v1
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/models.py` — añadir `project: str = ""` y `project_path: Path | None = None` a `Change`
  - Commit: `[observatory-v1] Add project and project_path fields to Change model`

- [x] **T02** Crear `src/sdd_tui/core/config.py` — `AppConfig`, `ProjectConfig`, `load_config()` con parser YAML manual
  - Commit: `[observatory-v1] Add config loader for ~/.sdd-tui/config.yaml`

- [x] **T03** Crear `tests/test_config.py` — tests unitarios del config loader
  - Commit: `[observatory-v1] Add tests for config loader`
  - Depende de: T02

- [x] **T04** Modificar `src/sdd_tui/core/reader.py` — `project_path` param en `OpenspecReader.load()`; añadir `load_all_changes(config, cwd, include_archived)`
  - Commit: `[observatory-v1] Add multi-project loading to reader`
  - Depende de: T01, T02

- [x] **T05** Modificar `tests/test_reader.py` — casos para `project`/`project_path` en Change y `load_all_changes`
  - Commit: `[observatory-v1] Add multi-project tests to reader`
  - Depende de: T04

- [x] **T06** Modificar `src/sdd_tui/tui/spec_evolution.py` — `DecisionsTimeline.__init__(archive_dirs: list[Path])` + `_populate()` agrega de todos los dirs
  - Commit: `[observatory-v1] Make DecisionsTimeline aggregate multiple archive dirs`

- [x] **T07** Modificar `src/sdd_tui/tui/spec_health.py` — project separators en `_populate()`; sustituir `Path.cwd()` por `change.project_path`
  - Commit: `[observatory-v1] Add project separators and fix cwd in SpecHealthScreen`
  - Depende de: T01

- [x] **T08** Modificar `src/sdd_tui/tui/app.py` — aceptar `AppConfig` en `__init__`; adaptar `_load_changes()` a `load_all_changes()`; cargar config en `main()`
  - Commit: `[observatory-v1] Integrate AppConfig into app startup and change loading`
  - Depende de: T02, T04

- [x] **T09** Modificar `src/sdd_tui/tui/epics.py` — separadores de proyecto en `_populate()`; `action_decisions_timeline()` pasa `list[Path]`
  - Commit: `[observatory-v1] Add multi-project separators to EpicsView`
  - Depende de: T06, T08

- [x] **T10** Modificar `tests/test_tui_epics.py` — casos multi-project (separadores visibles/no visibles)
  - Commit: `[observatory-v1] Add multi-project UI tests for EpicsView`
  - Depende de: T09

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest -x`
