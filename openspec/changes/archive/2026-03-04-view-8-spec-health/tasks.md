# Tasks: View 8 — Spec Health Dashboard

## Metadata
- **Change:** view-8-spec-health
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Crear `tests/test_metrics.py` — tests unitarios RED para el módulo metrics
  - Commit: `[view-8-spec-health] Add unit tests for metrics module`

- [x] **T02** Crear `src/sdd_tui/core/metrics.py` — ChangeMetrics dataclass + parse_metrics()
  - Commit: `[view-8-spec-health] Add core metrics module with parse_metrics`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/spec_health.py` — SpecHealthScreen con DataTable de métricas
  - Commit: `[view-8-spec-health] Add SpecHealthScreen with health dashboard`
  - Depende de: T02

- [x] **T04** Modificar `src/sdd_tui/tui/change_detail.py` — badge REQ en PipelinePanel + compute metrics en ChangeDetailScreen
  - Commit: `[view-8-spec-health] Add REQ badge to PipelinePanel in View 2`
  - Depende de: T02

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — binding H + action_health() → SpecHealthScreen
  - Commit: `[view-8-spec-health] Add H binding to open SpecHealthScreen from View 1`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest`
  - Commit: `[view-8-spec-health] All tests green`

## Mejoras post-verify

- [x] **MEJ01** `src/sdd_tui/core/metrics.py` — `_count_reqs` cuenta ocurrencias en lugar de IDs únicos; REQ-04 en definición + escenario = 2 matches
  - Fix: usar set de IDs únicos; `ears_count` = IDs con al menos una línea EARS-tagged
  - Commit: `[view-8-spec-health] Fix req counting to use unique REQ IDs`

## Bugs detectados en verify

- [x] **BUG01** `src/sdd_tui/tui/spec_health.py` — imports y constantes no utilizados + type annotation faltante en `_add_row`
  - Detectado: self-review checklist (type hints + código muerto)
  - Fix: eliminar `Static`, `DONE`, `PENDING` sin uso; añadir `metrics: ChangeMetrics` en `_add_row`
  - Commit: `[view-8-spec-health] Fix unused imports and missing type hint in spec_health`

## Notas

- T01 antes que T02: TDD (tests RED → implementación GREEN)
- T03 y T04 son independientes entre sí (ambas dependen de T02)
- T05 es la última: no bloquea ninguna otra tarea pero necesita SpecHealthScreen (T03)
- `PipelinePanel(metrics=None)` — parámetro opcional, retrocompatible con tests existentes
