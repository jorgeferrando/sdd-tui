# Tasks: gh-actions

## Metadata
- **Change:** gh-actions
- **Jira:** N/A (proyecto standalone)
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/github.py` — añadir `CiStatus`, `ReleaseInfo`, `get_ci_status()`, `get_releases()`
  - Commit: `[gh-actions] Add CiStatus, ReleaseInfo, get_ci_status, get_releases to github`

- [x] **T02** Modificar `tests/test_github.py` — tests para `get_ci_status` y `get_releases`
  - Depende de: T01
  - Commit: `[gh-actions] Add tests for get_ci_status and get_releases`

- [x] **T03** Modificar `src/sdd_tui/tui/change_detail.py` — sentinel `_CI_LOADING`, extender `PipelinePanel` con CI row, worker `_load_ci_status_worker`, binding `W` + `action_ship_pr`
  - Depende de: T01
  - Commit: `[gh-actions] Add CI status and ship binding to ChangeDetailScreen`

- [x] **T04** Crear `src/sdd_tui/tui/releases.py` — `ReleasesScreen` con DataTable de releases
  - Depende de: T01
  - Commit: `[gh-actions] Add ReleasesScreen`

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — binding `l` + `action_releases()`
  - Depende de: T04
  - Commit: `[gh-actions] Add L binding for ReleasesScreen in EpicsView`

- [x] **T06** Modificar `tests/test_tui_change_detail.py` — tests CI status en `PipelinePanel` + ship binding
  - Depende de: T03
  - Commit: `[gh-actions] Add tests for CI status and ship binding`

- [x] **T07** Crear `tests/test_tui_releases.py` — tests de `ReleasesScreen`
  - Depende de: T04, T05
  - Commit: `[gh-actions] Add tests for ReleasesScreen`

## Quality Gate Final

- [x] **QG** Ejecutar tests + lint
  - `uv run pytest`
  - `~/.claude/scripts/sdd-tui-lint.sh`

## Notas

- T01 primero: `CiStatus` y `ReleaseInfo` son los contratos que usan T03 y T04
- T02 y T03 y T04 son independientes entre sí — todos dependen solo de T01
- T05 antes que T07: `epics.py` importa `ReleasesScreen` y los tests de T07 necesitan el binding `l`
- T06 puede hacerse en paralelo con T04/T05 conceptualmente, en la práctica después de T03
- Binding `W` en Textual = `shift+w` en el string de binding
- `_CI_LOADING` sentinel definido en `change_detail.py` (exportado para tests igual que `_PR_LOADING`)
- Ship description: leer sección `## Descripción` de `proposal.md`, primera línea no vacía
- `get_branch()` se llama dentro del worker CI (no en `on_mount`) — thread-safe
