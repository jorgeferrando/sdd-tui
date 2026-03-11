# Tasks: sdd-docs-generator

## Metadata
- **Change:** sdd-docs-generator
- **Jira:** — (no ticket — proyecto personal, commits directos a main)
- **Rama:** main
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Modificar `pyproject.toml` — añadir entry point `sdd-docs`
  - Commit: `[sdd-docs-generator] Add sdd-docs entry point to pyproject.toml`

- [x] **T02** Crear `src/sdd_tui/docs_gen.py` — CLI completo: lectura de openspec, generación de páginas, escritura controlada
  - Depende de: T01
  - Commit: `[sdd-docs-generator] Add docs_gen module with sdd-docs CLI`

- [x] **T03** Crear `tests/test_docs_gen.py` — cobertura unitaria con tmp_path (23 tests)
  - Depende de: T02
  - Commit: `[sdd-docs-generator] Add tests for docs_gen module`

- [x] **T04** Crear `skills/sdd-docs/SKILL.md` — skill para capa inteligente de relleno de placeholders
  - Independiente de T01-T03
  - Commit: `[sdd-docs-generator] Add sdd-docs skill for intelligent placeholder filling`

- [x] **T05** Modificar `Formula/sdd-tui.rb` — añadir `sdd-docs --help` al bloque test
  - Depende de: T01
  - Commit: `[sdd-docs-generator] Add sdd-docs to Homebrew formula test block`

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests + lint
  - `uv run pytest`
  - `uv run ruff check src/ tests/`
  - `uv run ruff format --check src/ tests/`

## Notas

- T01 antes que T02 — el módulo debe tener un nombre definido antes de implementarlo
- T04 es independiente — puede hacerse en cualquier momento después de T01
- T05 debe ir después de T01 (el entry point debe existir para que la formula tenga sentido)
- El skill en `skills/sdd-docs/SKILL.md` se distribuye via `sdd-setup` — no requiere cambios en setup.py
