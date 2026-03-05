# Tasks: pr-status — GitHub PR Status en PipelinePanel

## Metadata
- **Change:** pr-status
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/github.py` — `PrStatus` dataclass + `get_pr_status()`
  - Commit: `[pr-status] Add github.py with PrStatus and get_pr_status`

- [x] **T02** Crear `tests/test_github.py` — tests unitarios de `get_pr_status` con subprocess mock
  - Commit: `[pr-status] Add unit tests for get_pr_status`
  - Depende de: T01

- [x] **T03** Modificar `src/sdd_tui/tui/change_detail.py` — `PipelinePanel` con estado loading/none/loaded + `update_pr()`; worker en `ChangeDetailScreen`
  - Commit: `[pr-status] Integrate PR status into PipelinePanel and ChangeDetailScreen`
  - Depende de: T01

- [x] **T04** Ampliar `tests/test_tui_change_detail.py` — casos: loading row, PR loaded, no PR, review counts
  - Commit: `[pr-status] Add TUI tests for PR status in PipelinePanel`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest`

## Notas

- T01 y T02 son puros (sin TUI) — ejecutar pytest tras T02 para validar en verde
- T03 modifica `PipelinePanel` (Static) — `update_pr` llama `self.update(content)`, no remonta el widget
- Sentinel `_LOADING = object()` en `change_detail.py` — privado al módulo
- Worker en `ChangeDetailScreen.on_mount` lanza `_load_pr_status_worker()` al abrir View 2
- `action_refresh_view` no requiere cambios — los paneles se remontan y `on_mount` relanza el worker
