# Tasks: provider-abstraction

## Metadata
- **Change:** provider-abstraction
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/providers/__init__.py` — package init con re-exports públicos
  - Commit: `[provider-abstraction] Add core/providers package`

- [x] **T02** Crear `src/sdd_tui/core/providers/protocol.py` — dataclasses + Protocols + factories
  - Incluye: `Issue`, `PrInfo`, `GitWorkflowConfig`, `IssueTracker`, `GitHost`, `make_git_host`, `make_issue_tracker`
  - Incluye también: `PrStatus`, `CiStatus`, `ReleaseInfo` (migrados desde `core/github.py`)
  - Commit: `[provider-abstraction] Add provider protocols and GitWorkflowConfig`

- [x] **T03** Crear `src/sdd_tui/core/providers/github.py` — GitHubHost + GitHubIssueTracker + compat functions
  - `GitHubHost`: migra lógica de `get_pr_status`, `get_ci_status`, `get_releases` de `core/github.py`
  - `GitHubIssueTracker`: nueva, implementa `get_issues` y `get_issue`
  - Module-level compat: `get_pr_status`, `get_ci_status`, `get_releases` via `_default_host`
  - Commit: `[provider-abstraction] Add GitHubHost and GitHubIssueTracker`
  - Depende de: T02

- [x] **T04** Crear `src/sdd_tui/core/providers/null.py` — NullGitHost + NullIssueTracker
  - Todos los métodos retornan `None` / `[]` silenciosamente
  - `create_*` y `close_*` lanzan `NotImplementedError`
  - Commit: `[provider-abstraction] Add NullGitHost and NullIssueTracker`
  - Depende de: T02

- [x] **T05** Modificar `src/sdd_tui/core/github.py` — convertir en shim de re-exportación
  - Reemplazar todo el contenido por re-exports desde `providers/protocol.py` y `providers/github.py`
  - Actualizar `tests/test_github.py`: patch path `sdd_tui.core.github.subprocess.run` → `sdd_tui.core.providers.github.subprocess.run` (los subprocess.run reales viven en providers/github.py; el shim no importa subprocess)
  - Commit: `[provider-abstraction] Convert core/github.py to compatibility shim`
  - Depende de: T03

- [x] **T06** Modificar `src/sdd_tui/core/reader.py` — añadir `load_git_workflow_config` y `_write_git_workflow_config`
  - Parsing manual de `git_workflow:` en `openspec/config.yaml` (patrón regex del proyecto)
  - `_write_git_workflow_config`: crea / reemplaza sección sin tocar el resto del archivo
  - Commit: `[provider-abstraction] Add load/write git_workflow_config to reader`
  - Depende de: T02

- [x] **T07** Modificar `src/sdd_tui/tui/app.py` — instanciar `_git_host` y `_issue_tracker` en `__init__`
  - `load_git_workflow_config(openspec_path)` → `make_git_host/make_issue_tracker`
  - Commit: `[provider-abstraction] Instantiate provider singletons in App`
  - Depende de: T02, T06

- [x] **T08** Crear `src/sdd_tui/tui/setup.py` — `GitWorkflowSetupScreen` (wizard de 5 pasos)
  - `OptionList` + `Input` (custom prefix), opciones "próximamente" no seleccionables
  - Esc = descartar sin guardar; completar 5 pasos = `_write_git_workflow_config` + notify + pop
  - Commit: `[provider-abstraction] Add GitWorkflowSetupScreen wizard`
  - Depende de: T06

- [x] **T09** Modificar `src/sdd_tui/tui/epics.py` — añadir binding `S` → `GitWorkflowSetupScreen`
  - Commit: `[provider-abstraction] Add S binding for git workflow setup in EpicsView`
  - Depende de: T08

- [x] **T10** Crear `tests/test_providers_github.py` — tests de GitHubHost y GitHubIssueTracker
  - Migrar/adaptar los 18 tests de `test_github.py` al path `sdd_tui.core.providers.github`
  - Añadir tests de `GitHubIssueTracker.get_issues` (open/closed, error, empty)
  - Commit: `[provider-abstraction] Add tests for GitHubHost and GitHubIssueTracker`
  - Depende de: T03

- [x] **T11** Crear `tests/test_providers_null.py` — tests de NullGitHost y NullIssueTracker
  - Verifica que todos los métodos retornan vacío sin excepciones
  - Verifica que `create_*` lanza `NotImplementedError`
  - Commit: `[provider-abstraction] Add tests for NullGitHost and NullIssueTracker`
  - Depende de: T04

- [x] **T12** Crear `tests/test_git_workflow_config.py` — tests de parsing y escritura de config
  - Config completa, config parcial (defaults), archivo inexistente, sección ausente
  - `_write_git_workflow_config`: crea nuevo, reemplaza sección, añade a existente
  - Commit: `[provider-abstraction] Add tests for git_workflow_config parsing and writing`
  - Depende de: T06

- [x] **T13** Crear `tests/test_tui_setup.py` — tests de `GitWorkflowSetupScreen`
  - Avance entre pasos, opción "próximamente" no avanza, Esc no guarda
  - Completar wizard escribe config, opción "personalizado" muestra Input
  - Commit: `[provider-abstraction] Add TUI tests for GitWorkflowSetupScreen`
  - Depende de: T08

## Bugs detectados en verify

- [x] **BUG01** `tui/setup.py` — opciones de change_prefix incorrectas vs REQ-WZ02
  - Detectado: verify spec compliance
  - Fix: cambiar `feature` → `#` y añadir `none` (sin prefijo); renombrar `custom` → `personalizado`
  - Commit: `[provider-abstraction] Fix change_prefix options in wizard (REQ-WZ02)`

- [x] **BUG02** `core/reader.py` — comentario incorrecto al crear config.yaml nuevo vs REQ-WZ07
  - Detectado: verify spec compliance
  - Fix: `# openspec config` → `# Añadir jira_prefix: si usas SDD`
  - Commit: `[provider-abstraction] Fix new config.yaml comment (REQ-WZ07)`

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`
  - Target: todos los tests en verde (sin romper los 358 existentes)

## Notas

- **T05 es el momento de verdad del shim:** correr `uv run pytest tests/test_github.py`
  inmediatamente después para verificar que los 18 tests siguen en verde.
- **T02 es la tarea más crítica:** `protocol.py` define el contrato del que dependen
  T03, T04, T06, T07 y T08. Debe estar completo antes de continuar.
- **TDD sugerido:** escribir T10–T13 con RED antes de T03/T04/T06/T08 si se prefiere,
  pero el orden del design (implementación → tests) es igualmente válido.
- **`test_github.py` no se toca:** es el validador del shim de compatibilidad.
