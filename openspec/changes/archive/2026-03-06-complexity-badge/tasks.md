# Tasks: Complexity Badge

## Metadata
- **Change:** complexity-badge
- **Rama:** main
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Extender `core/metrics.py` — añadir `complexity_score`/`complexity_label` a `ChangeMetrics` y funciones `_get_complexity`, `_count_tasks`, `_count_spec_lines`, `_count_git_files`
  - Commit: `[complexity-badge] Add complexity score to ChangeMetrics`

- [x] **T02** Añadir tests unitarios en `tests/test_metrics.py` — cubrir cálculo de score, cada rango de label, y fallback git
  - Commit: `[complexity-badge] Add tests for complexity score calculation`
  - Depende de: T01

- [x] **T03** Extender `tui/epics.py` — añadir columna SIZE y actualizar todas las filas separadoras
  - Commit: `[complexity-badge] Add SIZE column to EpicsView`
  - Depende de: T01

- [x] **T04** Añadir test TUI en `tests/test_tui_epics.py` — verificar que columna SIZE aparece con label válido
  - Commit: `[complexity-badge] Add TUI test for SIZE column in EpicsView`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar suite completa
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- T01 antes que T02 y T03 — ambos dependen de los nuevos campos en `ChangeMetrics`
- T02 y T03 son independientes entre sí, pueden ejecutarse en cualquier orden
- T04 requiere T03 (necesita la columna SIZE para verificar)
- Los defaults en `ChangeMetrics` (`complexity_score=0`, `complexity_label="XS"`) garantizan que no hay que tocar tests existentes
- En `_populate` hay 3 puntos con filas separadoras que necesitan un `""` extra — no olvidar el placeholder "No matches for..." también
