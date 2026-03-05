# Tasks: UX Navigation (Scroll, Drill-down, Paths)

## Metadata
- **Change:** ux-navigation
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Añadir `@property changes` en `tui/app.py`
  - Commit: `[ux-navigation] Add public changes property to SddTuiApp`

- [x] **T02** Añadir bindings `j/k` en `tui/doc_viewer.py` (DocumentViewerScreen)
  - Commit: `[ux-navigation] Add j/k scroll bindings to DocumentViewerScreen`

- [x] **T03** Añadir bindings `j/k` en `tui/spec_evolution.py` (SpecEvolutionScreen + DecisionsTimeline) y corregir path hardcodeado en `_render_domain`
  - Commit: `[ux-navigation] Add j/k bindings and fix openspec path in spec_evolution`

- [x] **T04** Añadir drill-down y `_change_map` en `tui/spec_health.py`
  - Commit: `[ux-navigation] Add drill-down from SpecHealthScreen to ChangeDetailScreen`

- [x] **T05** Corregir paths hardcodeados en `tui/epics.py` (action_steering + action_decisions_timeline)
  - Commit: `[ux-navigation] Fix hardcoded openspec paths in EpicsView`

- [x] **T06** Tests — `tests/test_tui_doc_viewer.py`: verificar bindings `j/k` en DocumentViewerScreen
  - Commit: `[ux-navigation] Tests for j/k bindings in DocumentViewerScreen`

- [x] **T07** Tests — `tests/test_tui_spec_evolution.py`: verificar bindings `j/k` en SpecEvolutionScreen y DecisionsTimeline
  - Commit: `[ux-navigation] Tests for j/k bindings in SpecEvolutionScreen and DecisionsTimeline`

- [x] **T08** Tests — `tests/test_tui_spec_health.py`: drill-down con Enter y separador sin key
  - Commit: `[ux-navigation] Tests for drill-down from SpecHealthScreen`

## Bugs detectados en verify

- [x] **BUG01** `tui/doc_viewer.py`, `tui/spec_evolution.py` — `j/k` no hacen scroll
  - Detectado: smoke test
  - Fix: `scroll_down`/`scroll_up` son acciones de `ScrollableContainer`, no de `Screen`. Añadir `action_scroll_down`/`action_scroll_up` en cada Screen que deleguen al contenedor interno.
  - Commit: `[ux-navigation] Fix j/k scroll actions to delegate to ScrollableContainer`

## Quality Gate Final

- [x] **QG** Ejecutar tests completos
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- T01 antes de T04 y T08: `app.changes` se usa en los tests de SpecHealthScreen
- T03 incluye dos pantallas en un archivo — el commit es atómico por archivo
- Los tests son TDD: escribir RED → implementar → verificar GREEN
- Rama `main` — commits directos (convención del proyecto)
