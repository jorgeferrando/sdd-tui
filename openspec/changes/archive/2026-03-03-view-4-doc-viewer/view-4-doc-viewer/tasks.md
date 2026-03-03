# Tasks: View 4 — Document viewer

## Metadata
- **Change:** view-4-doc-viewer
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/tui/doc_viewer.py` — `DocumentViewerScreen` + `SpecSelectorScreen`
  - Commit: `[view-4] Add DocumentViewerScreen and SpecSelectorScreen`

- [x] **T02** Modificar `src/sdd_tui/tui/change_detail.py` — añadir bindings `p/d/s/t` + actions + import
  - Commit: `[view-4] Add doc viewer keybindings to ChangeDetailScreen`
  - Depende de: T01

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test de navegación
  - `uv run pytest`
  - `uv run sdd-tui` → Enter en un change → `p`, `d`, `s`, `t` → navegar → Esc

## Notas

- T01 primero: `change_detail.py` importa de `doc_viewer.py`
- No hay tests automatizados nuevos — el proyecto no tiene cobertura de TUI todavía
- `rich.Markdown` import: `from rich.markdown import Markdown`
- `ListView`, `ListItem`, `Label` en `from textual.widgets import ...`
