# Tasks: View 5 — Clipboard command launcher

## Metadata
- **Change:** view-5-clipboard
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/tui/change_detail.py` — añadir binding `Space` + `action_copy_next_command` + `_build_next_command`
  - Commit: `[view-5] Add clipboard command launcher with Space binding`

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test
  - `uv run pytest`
  - `uv run sdd-tui` → Enter en un change → Space → verificar notificación y portapapeles

## Notas

- `priority=True` en el binding es obligatorio — sin él, DataTable consume Space antes
- `PhaseState` ya está importado en `change_detail.py` — sin imports nuevos
