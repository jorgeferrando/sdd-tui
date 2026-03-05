# Tasks: Help Screen (Keybindings Reference)

## Metadata
- **Change:** view-help-screen
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Crear `tui/help.py` — HelpScreen con HELP_CONTENT estático y bindings j/k/Esc
  - Commit: `[view-help-screen] Add HelpScreen with static keybindings reference`

- [x] **T02** Modificar `tui/app.py` — añadir BINDINGS con `?` global (priority=True) y action_help
  - Commit: `[view-help-screen] Add global ? binding to open HelpScreen`
  - Depende de: T01

- [x] **T03** Modificar `README.md` — actualizar sección Keybindings con todos los bindings actuales
  - Commit: `[view-help-screen] Update README keybindings section`

- [x] **T04** Crear `tests/test_tui_help.py` — tests: open, close, j/k bindings, contenido
  - Commit: `[view-help-screen] Tests for HelpScreen`
  - Depende de: T01, T02

## Quality Gate Final

- [x] **QG** Ejecutar tests completos
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- T01 antes de T02 y T04: app.py importa HelpScreen en action_help
- `"question_mark"` es el nombre canónico de `?` en Textual (shift+/)
- Patrón scroll: `action_scroll_down/up` delegando a `ScrollableContainer` (igual que ux-navigation)
