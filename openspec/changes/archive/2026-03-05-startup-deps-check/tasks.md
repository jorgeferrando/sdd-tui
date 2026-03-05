# Tasks: startup-deps-check

## Metadata
- **Change:** startup-deps-check
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/deps.py` — `Dep`, `DEPS`, `check_deps()`, `_is_present()`
  - Commit: `[startup-deps-check] Add core deps module with Dep model and check_deps()`

- [x] **T02** Crear `tests/test_deps.py` — tests unitarios de `check_deps()` e `_is_present()`
  - Commit: `[startup-deps-check] Add tests for check_deps()`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/error_screen.py` — `ErrorScreen` con lista de deps y `[q]` quit
  - Commit: `[startup-deps-check] Add ErrorScreen for missing required dependencies`

- [x] **T04** Modificar `src/sdd_tui/tui/app.py` — añadir `on_mount` con integración de `check_deps()`
  - Commit: `[startup-deps-check] Integrate dep check on app startup`
  - Depende de: T01, T03

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `uv run pytest tests/ -q`

## Notas

- T01 y T03 son independientes entre sí — T04 depende de ambos
- `_is_present` es función module-level (no método de clase) para facilitar el patch en tests
- `on_mount` usa imports locales (patrón ya establecido en `app.py`)
- Sin Esc en `ErrorScreen` — no añadir binding por defecto de Textual que haría pop_screen
