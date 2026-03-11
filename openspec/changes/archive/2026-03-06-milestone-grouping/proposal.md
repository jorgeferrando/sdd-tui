# Proposal: milestone-grouping

## Descripción

Añadir soporte para agrupar changes en EpicsView por hitos (milestones) definidos en `openspec/milestones.yaml`. Cuando el archivo existe, los changes activos se organizan bajo cabeceras de milestone en lugar de mostrarse en una lista plana.

## Motivación

Con el proyecto acumulando más de 25 changes archivados y potencialmente varios activos en paralelo, la lista plana de EpicsView pierde contexto sobre el propósito o agrupación lógica de cada change. Los milestones permiten comunicar "qué bloque de trabajo" representa cada change: por versión, por feature-set, por sprint, etc.

La idea viene del roadmap GSD-inspirado documentado en MEMORY.md, que menciona `openspec/milestones.yaml` como la siguiente mejora de UX en EpicsView.

## Alternativas consideradas

1. **Etiquetas/tags inline en el change name** — Requeriría convención de naming adicional y modificar el parser. Más intrusivo.
2. **Carpetas de milestone en `openspec/changes/`** — Rompería la estructura flat actual y el reader existente. Demasiado invasivo.
3. **Sin milestones, solo ordenamiento manual** — No da contexto visual de agrupación.

## Solución propuesta

- Formato `openspec/milestones.yaml` declarativo con lista de milestones y sus changes.
- `core/milestones.py` — función pura `load_milestones(openspec_path)` que parsea el YAML sin dependencias externas (parsing manual como en `core/config.py`).
- `EpicsView._populate()` — cuando `milestones.yaml` existe, insertar separadores de milestone entre changes activos en lugar de mostrar lista plana.
- Changes activos no asignados a ningún milestone → sección `── unassigned ──`.
- Si `milestones.yaml` no existe → comportamiento actual sin cambios (retrocompatible).
- Changes archivados no se agrupan por milestone (mantienen sección `── archived ──` actual).

## Formato milestones.yaml

```yaml
milestones:
  - name: "v1.0 — Bootstrap"
    changes:
      - bootstrap
      - view-2-change-detail
  - name: "v1.1 — UX"
    changes:
      - ux-feedback
      - ux-navigation
      - view-help-screen
```

## Impacto

**Archivos afectados:**
- `src/sdd_tui/core/milestones.py` — nuevo (lógica de parsing)
- `src/sdd_tui/tui/epics.py` — modificar `_populate()` para agrupar por milestone
- `tests/test_milestones.py` — tests unitarios del parser
- `tests/test_epics_milestones.py` — tests de EpicsView con milestones

**Sin cambios en:**
- `core/models.py`, `core/reader.py`, `core/config.py`
- Resto de vistas (ChangeDetail, SpecHealth, etc.)

## Criterios de éxito

- [ ] `load_milestones()` parsea el YAML sin dependencias externas
- [ ] EpicsView agrupa por milestone cuando `milestones.yaml` existe
- [ ] Changes sin milestone aparecen en `── unassigned ──`
- [ ] Sin `milestones.yaml` → comportamiento idéntico al actual
- [ ] Multi-project + milestones coexisten correctamente (milestone > proyecto como agrupador)
- [ ] Tests pasan (>= 316 + nuevos)
