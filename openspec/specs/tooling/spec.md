# Spec: Tooling — Python Linting

## Metadata
- **Dominio:** tooling
- **Change:** tooling-python-lint
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

Quality gate de Python para el proyecto sdd-tui. Ruff como linter + formateador
unificado, configurado en pyproject.toml, con script de CI en ~/.claude/scripts/.

## Requisitos

- **REQ-01** `[Ubiquitous]` The proyecto SHALL tener ruff como dependencia de desarrollo.
- **REQ-02** `[Ubiquitous]` The configuración SHALL estar en `pyproject.toml` con `line-length = 100` y reglas `E`, `F`, `I`.
- **REQ-03** `[Ubiquitous]` The código en `src/` y `tests/` SHALL pasar `ruff check` y `ruff format --check` sin errores.
- **REQ-04** `[Ubiquitous]` The script `~/.claude/scripts/sdd-tui-lint.sh` SHALL ejecutar el quality gate.

## Reglas de negocio

- **RB-LINT01:** Solo se activan reglas E (pycodestyle), F (pyflakes) e I (isort) — sin reglas agresivas.
- **RB-LINT02:** `line-length = 100` (no 88 de black por defecto — el código existente usaba ~90 chars).
- **RB-LINT03:** El script acepta argumentos opcionales; sin args aplica al proyecto completo.
