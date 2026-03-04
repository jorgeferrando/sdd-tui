# Tasks: View 6 — Refresh in-place

## Metadata
- **Change:** view-6-refresh-in-place
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/tui/app.py` — `refresh_changes()` devuelve `list[Change]`
  - Commit: `[view-6] Make refresh_changes return list[Change]`

- [x] **T02** Modificar `src/sdd_tui/tui/change_detail.py` — `action_refresh_view` in-place
  - Commit: `[view-6] Refresh View 2 in-place without pop_screen`
  - Depende de: T01

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test
  - `uv run pytest`
  - `uv run sdd-tui` → Enter en un change → `r` → verificar que los datos se actualizan sin cerrar View 2

## Notas

- El change desaparecido es un edge case seguro — simplemente notifica + pop
- `call_after_refresh` para el foco es el mismo patrón que `on_mount`
