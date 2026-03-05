# Proposal: Tooling — Python Linting con Ruff

## Metadata
- **Change:** tooling-python-lint
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

El proyecto no tiene ningún linter ni formateador configurado. Esto significa:

- No hay garantía de estilo consistente entre archivos
- Los type hints existen pero nunca se verifican (sin mypy ni ruff check)
- En `/sdd-verify` no se puede ejecutar un quality gate de Python — solo tests
- Los errores de tipo se descubren en runtime, no en development

## Solución Propuesta

Añadir **ruff** como linter + formateador:

- Reemplaza flake8, isort y black en un solo binario
- Integración nativa con uv (`uv add --dev ruff`)
- Configuración en `pyproject.toml` (no archivo extra)
- Velocidad muy alta — no añade fricción al flujo

### Configuración mínima (no dogmática)

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I"]   # pycodestyle errors, pyflakes, isort
ignore = []
```

No se activan reglas agresivas (no `ANN` para annotations obligatorias,
no `D` para docstrings) — el objetivo es coherencia, no perfeccionismo.

### Script de quality gate

Crear `~/.claude/scripts/sdd-tui-lint.sh`:

```bash
#!/bin/bash
uv run ruff check "$@"
uv run ruff format --check "$@"
```

Esto permite usar el mismo patrón que otros proyectos en `/sdd-verify`.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| flake8 + black + isort | Maduros, bien conocidos | Tres herramientas separadas | Descartada |
| mypy | Type checking real | Más configuración, más lento | Como paso 2 futuro |
| **ruff** | Todo en uno, ultra rápido | Relativamente nuevo | **Elegida** |

## Impacto Estimado

- **Archivos modificados:** `pyproject.toml`
- **Archivos nuevos:** `~/.claude/scripts/sdd-tui-lint.sh`
- **Breaking changes:** Si ruff detecta errores en el código actual → corregirlos en el mismo PR
- **Tests afectados:** Ninguno

## Criterios de Éxito

- [ ] `uv run ruff check src/ tests/` pasa sin errores
- [ ] `uv run ruff format --check src/ tests/` pasa sin errores
- [ ] Script `~/.claude/scripts/sdd-tui-lint.sh` ejecutable
- [ ] Configuración en `pyproject.toml` (sin archivos extra)
