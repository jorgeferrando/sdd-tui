# Tasks: View 5 — Transport adapters

## Metadata
- **Change:** view-5-transports
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/transports.py` — `Transport` Protocol + `TmuxTransport` + `ZellijTransport` + `detect_transport()`
  - Commit: `[view-5] Add Transport protocol with TmuxTransport and ZellijTransport adapters`

- [x] **T02** Crear `tests/test_transports.py` — 16 tests cubriendo los tres componentes
  - Commit: `[view-5] Add tests for TmuxTransport, ZellijTransport and detect_transport`

## Bugs detectados en verify

- [x] **BUG01** `src/sdd_tui/core/transports.py` — `ZellijTransport.find_pane()` retorna `"focused"` como sentinel en lugar de `None`
  - Detectado: review post-implementación — el contrato de `find_pane()` es retornar `None` cuando no puede targetear un pane específico; `"focused"` es un hack semántico
  - Fix: cambiar `return "focused"` por `return None`; actualizar test correspondiente
  - Commit: `[view-5] Fix ZellijTransport.find_pane to return None when targeting unsupported`

## Quality Gate Final

- [x] **QG** `uv run pytest` — todos los tests en verde tras BUG01
