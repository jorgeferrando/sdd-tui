# Spec: Tooling — Python Linting

## Metadata
- **Dominio:** tooling
- **Change:** tooling-python-lint
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

El proyecto no tiene linter configurado. Se añade ruff como quality gate de Python
para detectar errores de estilo, imports desordenados y bugs comunes.

## Requisitos (EARS)

- **REQ-01** `[Ubiquitous]` The proyecto SHALL tener ruff configurado como dependencia de desarrollo.

- **REQ-02** `[Ubiquitous]` The configuración de ruff SHALL estar en `pyproject.toml` (sin archivos adicionales).

- **REQ-03** `[Ubiquitous]` The reglas activas SHALL incluir `E` (pycodestyle errors), `F` (pyflakes) e `I` (isort) — sin reglas adicionales agresivas.

- **REQ-04** `[Ubiquitous]` The `line-length` SHALL ser 100 caracteres.

- **REQ-05** `[Ubiquitous]` The código existente en `src/` y `tests/` SHALL pasar `ruff check` y `ruff format --check` sin errores tras el cambio.

- **REQ-06** `[Ubiquitous]` The script `~/.claude/scripts/sdd-tui-lint.sh` SHALL existir y ejecutar `ruff check` + `ruff format --check` sobre los archivos pasados como argumentos.

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Solo E+F+I | Añadir ANN (annotations) o D (docstrings) | Evitar over-engineering; el objetivo es consistencia, no perfeccionismo |
| line-length 100 | 88 (black default) | El código existente usa líneas de ~90 chars; 100 evita reformatear todo |
| Ruff sobre flake8+black | Múltiples herramientas | Todo en uno, ultra rápido, una sola configuración |

## Abierto / Pendiente

Ninguno.
