# Tasks: Tooling — Python Linting con Ruff

## Metadata
- **Change:** tooling-python-lint
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Modificar `pyproject.toml` — añadir ruff como dev dependency + configuración
  - `uv add --dev ruff`
  - Añadir `[tool.ruff]` con `line-length = 100`
  - Añadir `[tool.ruff.lint]` con `select = ["E", "F", "I"]`
  - Corregir cualquier violación detectada en src/ y tests/ en este mismo commit
  - Commit: `[tooling-python-lint] Add ruff linter configuration`

- [x] **T02** Crear `~/.claude/scripts/sdd-tui-lint.sh` — script de quality gate
  - Script ejecutable que corre `ruff check` + `ruff format --check`
  - Acepta argumentos opcionales (sin args → src/ y tests/)
  - Commit: `[tooling-python-lint] Add sdd-tui-lint.sh quality gate script`

## Quality Gate Final

- [x] **QG** Verificar que el lint pasa sobre todo el proyecto
  - `uv run ruff check src/ tests/`
  - `uv run ruff format --check src/ tests/`
  - `uv run pytest tests/ -q`

## Notas

- T01 instala ruff Y corrige violaciones en el mismo commit — el código debe pasar ruff tras T01
- T02 es independiente de T01 (solo crea el script, no ejecuta nada)
- Si hay muchas violaciones en T01 → corregirlas todas antes del commit (no dejar código roto)
