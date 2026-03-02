# Proposal: Bootstrap — Project setup + openspec reader + Epics view

## Metadata
- **Change:** bootstrap
- **Jira:** N/A
- **Fecha:** 2026-03-02
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

El proyecto existe como repositorio vacío. Necesitamos el esqueleto mínimo
que entregue algo útil y ejecutable: ver la lista de epics/changes activos
en `openspec/` desde la terminal.

## Solución Propuesta

Tres capas en un único change:

1. **Infraestructura**: `uv` + `pyproject.toml` + estructura de carpetas
2. **Core domain**: lector de `openspec/` — detecta changes, infiere estado
   del pipeline desde huellas en disco. Pura Python, sin dependencias TUI.
3. **View 1**: lista de epics/changes con Textual (read-only, navegación básica)

El core domain es la unidad testable. La TUI no tiene tests propios.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Bootstrap solo (sin View 1) | Más pequeño | No entrega nada visible | Descartada |
| Bootstrap + las 4 vistas | Entrega completa | Demasiado scope para el primero | Descartada |
| **Bootstrap + core + View 1** | Ejecutable, útil, acotado | — | **Elegida** |
| poetry | Maduro | Más lento, más verboso que uv | Descartada |
| **uv** | Rápido, moderno, estándar 2025 | Menos adoptado aún | **Elegida** |

## Impacto Estimado

- **Dominio:** core (openspec reader)
- **Archivos:** < 10 → Proceder
- **Tests nuevos:** ~3-5 (solo core domain: lectura, inferencia de pipeline, estados git)
- **Breaking changes:** No (proyecto nuevo)
- **Ramas dependientes:** No
- **Dependencia externa:** `git` CLI instalado en el sistema (asumido)

### Archivos previstos

```
pyproject.toml
src/
  sdd_tui/
    __init__.py
    core/
      reader.py          ← lee openspec/, detecta changes
      pipeline.py        ← infiere estado de cada fase desde huellas en disco
    tui/
      app.py             ← Textual App
      views/
        epics.py         ← View 1: lista de changes
tests/
  test_reader.py
  test_pipeline.py
```

## Criterios de Éxito

- [ ] `uv run sdd-tui` lanza la app sin errores
- [ ] View 1 muestra los changes de `openspec/changes/` (excluye `archive/`)
- [ ] El estado del pipeline se infiere correctamente desde huellas en disco
- [ ] Tests pasan (`uv run pytest`)

## Preguntas Abiertas

- [x] ¿La View 1 muestra solo `changes/` activos o también incluye epics de Jira?
  → Solo `openspec/changes/` + estado inferido desde git. Sin issue tracker.
- [ ] ¿Nombre del comando CLI: `sdd-tui` o algo más corto?

## Notas

- `uv` para gestión de dependencias y entorno virtual
- TDD: tests solo para el core domain (reader + pipeline), no para la TUI
- Scope v1: `openspec/` + git. Sin issue tracker (agnóstico: Jira, Trello, Linear…)
- La integración con issue trackers va en changes posteriores como adaptadores opcionales
