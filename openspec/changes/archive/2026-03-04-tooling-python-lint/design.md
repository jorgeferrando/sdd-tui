# Design: Tooling — Python Linting con Ruff

## Metadata
- **Change:** tooling-python-lint
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

Añadir ruff como dependencia de desarrollo vía `uv add --dev ruff`, configurarlo
en `pyproject.toml`, corregir cualquier violación en el código existente, y crear
el script de lint para `/sdd-verify`.

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `pyproject.toml` | Añadir `[tool.ruff]` y `[tool.ruff.lint]` config |

## Archivos a Crear

| Archivo | Propósito |
|---------|-----------|
| `~/.claude/scripts/sdd-tui-lint.sh` | Script quality gate para `/sdd-verify` |

## Archivos a Corregir (si ruff detecta errores)

A determinar en T01 — se corrige todo en el mismo commit que la configuración.

## Scope

- **Total archivos:** 2 fijos + posibles correcciones en src/tests
- **Resultado:** Ideal

## Configuración en pyproject.toml

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I"]
```

## Script sdd-tui-lint.sh

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/../../sites/sdd-tui" 2>/dev/null || true
uv run ruff check "${@:-.}"
uv run ruff format --check "${@:-.}"
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Corregir violaciones en el commit de configuración | PR separado de correcciones | El diff de configuración + fixes es coherente y revisable en un solo commit |
| Script acepta argumentos opcionales | Solo src/ hardcodeado | Permite `sdd-tui-lint.sh src/file.py` para lint de archivos individuales |
