# Tasks: openspec enrichment (steering + requirements + spec.json)

## Metadata
- **Change:** openspec-enrichment
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** `tests/test_reader.py` — add tests for `load_steering` and `load_spec_json` (RED)
  - Commit: `[openspec-enrichment] Add tests for load_steering and load_spec_json`

- [x] **T02** `src/sdd_tui/core/reader.py` — implement `load_steering()` and `load_spec_json()` (GREEN)
  - Commit: `[openspec-enrichment] Add load_steering and load_spec_json to core reader`

- [x] **T03** `tests/test_metrics.py` — add tests for requirements artifact and REQ counting (RED)
  - Commit: `[openspec-enrichment] Add tests for requirements.md artifact and REQ dedup`

- [x] **T04** `src/sdd_tui/core/metrics.py` — add requirements to `_ARTIFACT_FILES`; extract `_scan_req_lines`; update `_count_reqs` (GREEN)
  - Commit: `[openspec-enrichment] Support requirements.md as artifact and REQ source in metrics`

- [x] **T05** `src/sdd_tui/tui/epics.py` — add binding `s` + `action_steering()` using `DocumentViewerScreen`
  - Commit: `[openspec-enrichment] Add S binding to open steering.md from View 1`

- [x] **T06** `src/sdd_tui/tui/change_detail.py` — add binding `q` + `action_view_requirements()`
  - Commit: `[openspec-enrichment] Add q binding to open requirements.md from View 2`

- [x] **T07** `src/sdd_tui/tui/spec_health.py` — add `has_requirements`; update `_artifacts_str` and `_add_row` with Q column
  - Commit: `[openspec-enrichment] Add Q column for requirements.md in SpecHealthScreen`

## Bugs detectados en verify

- [x] **BUG01** `src/sdd_tui/tui/spec_health.py` — `requirements` usa `R` en lugar de `Q` en `_artifacts_str`
  - Detectado: smoke test verify — `name[0].upper()` de "requirements" = "R", colisiona con "research"
  - Fix: mapeo explícito `"requirements" → "Q"` en `_artifacts_str`
  - Commit: `[openspec-enrichment] Fix requirements artifact letter Q in spec health`

## Quality Gate Final

- [x] **QG** Ejecutar tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- Orden TDD: T01 (RED) → T02 (GREEN), T03 (RED) → T04 (GREEN)
- T05–T07 son TUI — sin tests automatizados; verificar manualmente
- `action_steering` usa `Path.cwd() / "openspec" / "steering.md"` (patrón del proyecto)
- `DocumentViewerScreen` ya maneja "not found" — no se necesita nueva pantalla
