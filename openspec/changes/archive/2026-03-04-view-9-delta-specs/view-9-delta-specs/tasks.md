# Tasks: View 9 — Delta Specs Viewer

## Metadata
- **Change:** view-9-delta-specs
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/spec_parser.py` — dataclasses `DeltaSpec`, `Decision`, `ChangeDecisions` + funciones `parse_delta`, `extract_decisions`, `collect_archived_decisions`
  - Commit: `[view-9-delta-specs] Add spec_parser module with delta and decisions extraction`

- [x] **T02** Crear `tests/test_spec_parser.py` — 7 tests unitarios para `parse_delta`, `extract_decisions`, `collect_archived_decisions`
  - Commit: `[view-9-delta-specs] Add unit tests for spec_parser`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/spec_evolution.py` — `SpecEvolutionScreen` (layout condicional, coloreado ADDED/MODIFIED/REMOVED, toggle D) + `DecisionsTimeline`
  - Commit: `[view-9-delta-specs] Add SpecEvolutionScreen and DecisionsTimeline`
  - Depende de: T01

- [x] **T04** Modificar `src/sdd_tui/tui/change_detail.py` — añadir binding `E` + `action_spec_evolution`
  - Commit: `[view-9-delta-specs] Add E binding to open SpecEvolutionScreen from View 2`
  - Depende de: T03

- [x] **T05** Modificar `src/sdd_tui/tui/epics.py` — añadir binding `X` + `action_decisions_timeline`
  - Commit: `[view-9-delta-specs] Add X binding to open DecisionsTimeline from View 1`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Bugs detectados en verify

- [x] **BUG01** `src/sdd_tui/core/spec_parser.py` — `extract_decisions` no reconoce `## Decisiones de Diseño`, solo `## Decisiones Tomadas`; todos los design.md archivados usan el primer formato
  - Detectado: smoke test verify — `collect_archived_decisions` devuelve 0 changes con decisiones
  - Fix: ampliar regex para reconocer ambas variantes (`Decisiones Tomadas` | `Decisiones de Diseño`)
  - Commit: `[view-9-delta-specs] Fix extract_decisions to also match Decisiones de Diseno heading`

## Mejoras post-QG

- [x] **MEJ01** `src/sdd_tui/core/git_reader.py` — `is_clean` siempre devuelve `False` porque `openspec/` está commiteado y siempre tiene cambios; `verify` nunca muestra ✓ en View 1
  - Fix: excluir `openspec/` del check con pathspec `-- . :(exclude)openspec/`
  - Commit: `[view-9-delta-specs] Fix is_clean to exclude openspec from git status check`

- [x] **BUG02** `src/sdd_tui/core/git_reader.py` — `is_clean` aún devuelve `False`; el badge verify sigue sin ✓
  - Detectado: smoke test verify — badge no muestra ✓ tras MEJ01
  - Causa raíz: `cwd=change_path` hace que los pathspecs `:(exclude)...` se resuelvan desde el change dir, no desde el repo root; además `.claude/` no estaba excluido
  - Fix: obtener git toplevel con `rev-parse --show-toplevel` y correr el status desde ahí; añadir `:(exclude).claude/`
  - Commits: `[view-9-delta-specs] Fix is_clean to also exclude .claude from git status check` + `[view-9-delta-specs] Fix is_clean to run from git toplevel so pathspecs resolve correctly`

## Notas

- T01 es la base; T02, T03 dependen de él
- T04 y T05 dependen de T03 (importan `SpecEvolutionScreen` y `DecisionsTimeline`)
- `SpecEvolutionScreen` omite panel izquierdo si el change tiene exactamente 1 dominio
- Toggle `D`: alterna entre delta (`parse_delta`) y spec canónica en `openspec/specs/{domain}/spec.md`
- `DecisionsTimeline` calcula `archive_dir = Path.cwd() / "openspec" / "changes" / "archive"`
