# Spec: TUI — Milestone Grouping en EpicsView

## Metadata
- **Dominio:** tui
- **Change:** milestone-grouping
- **Fecha:** 2026-03-06
- **Versión:** 2.5
- **Estado:** draft

## Contexto

Extensión de `EpicsView._populate()` para agrupar changes activos por milestone
cuando `openspec/milestones.yaml` está presente. Sin milestones, el comportamiento
es idéntico al actual.

## ADDED

### Comportamiento con milestones.yaml presente (single-project)

**Dado** View 1 en modo single-project
**Cuando** `openspec/milestones.yaml` existe y contiene al menos un milestone
**Entonces** los changes activos se muestran agrupados bajo cabeceras de milestone,
seguidos de una sección `── unassigned ──` para changes sin milestone asignado

**Layout ejemplo:**
```
  change              SIZE  propose  spec  design  tasks  apply  verify
  ── v1.0 — Bootstrap ──
  bootstrap             S      ✓      ✓      ✓      ✓      ✓      ✓
  view-2-change-detail  M      ✓      ✓      ✓      ✓      ✓      ✓
  ── v1.1 — UX ──
  ux-feedback           XS     ✓      ✓      ✓      ✓      ✓      ✓
  ── unassigned ──
  new-feature           XS     ✓      ·      ·      ·      ·      ·
  ── archived ──
  bootstrap             ...
```

### Requisitos (EARS)

- **REQ-MG-01** `[Optional]` Where `milestones.yaml` exists and single-project mode is active, `EpicsView` SHALL display active changes grouped under milestone header rows.
- **REQ-MG-02** `[Ubiquitous]` Each milestone header SHALL be rendered as a non-selectable separator row (no key registered in `_change_map`).
- **REQ-MG-03** `[Optional]` Where a change is not assigned to any milestone, the system SHALL display it under an `── unassigned ──` separator.
- **REQ-MG-04** `[Unwanted]` If `milestones.yaml` does not exist or returns `[]`, `EpicsView` SHALL fall back to the current flat list behavior without modification.
- **REQ-MG-05** `[Optional]` Where multi-project mode is active (`len(active_projects) > 1`), milestone grouping SHALL NOT be applied — existing project separator behavior is preserved.
- **REQ-MG-06** `[Ubiquitous]` The archived section (`── archived ──`) SHALL NOT be grouped by milestone, regardless of milestones.yaml content.
- **REQ-MG-07** `[Optional]` Where `milestones.yaml` exists and the `unassigned` section is empty (all active changes are assigned), the `── unassigned ──` separator SHALL NOT be rendered.
- **REQ-MG-08** `[Optional]` Where search filter is active, milestone grouping is preserved — only matching changes are shown within each milestone section. Empty milestone sections (no matches) are omitted.
- **REQ-MG-09** `[Ubiquitous]` A change that appears in `milestones.yaml` but has no corresponding `Change` object (e.g., archived) SHALL be silently skipped — no empty row rendered.

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin milestones.yaml | Archivo ausente | Comportamiento actual (sin separadores de milestone) |
| milestones.yaml vacío | `load_milestones()` retorna `[]` | Comportamiento actual |
| Todos asignados | Ningún change sin milestone | No se muestra `── unassigned ──` |
| Ninguno asignado | milestones.yaml existe pero ningún change coincide | Solo sección `── unassigned ──` con todos los changes activos |
| Multi-project | `len(active_projects) > 1` | Separadores por proyecto, sin milestones |
| Change en milestone no existe | Nombre en YAML sin Change object | Ignorado silenciosamente |
| Búsqueda activa | Filtro `/` aplicado | Solo changes que coincidan, agrupados por milestone; milestones vacíos omitidos |

### Reglas de negocio

- **RB-MG-01:** `load_milestones()` se llama en `_populate()` — no se cachea entre refreshes.
- **RB-MG-02:** El orden de milestones en pantalla sigue el orden declarado en `milestones.yaml`.
- **RB-MG-03:** Un change puede aparecer como máximo en un milestone (el primero que lo declara si hay duplicados).
- **RB-MG-04:** El `openspec_path` para `load_milestones()` es `self.app._openspec_path`.
- **RB-MG-05:** Las filas separadoras de milestone usan el mismo formato visual que los separadores existentes de proyecto/archive.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Milestone grouping solo en single-project | Aplicar también en multi-project | Complejidad alta: cada proyecto puede tener su propio milestones.yaml con posibles conflictos de nombres. Scope MVP. |
| No cachear `load_milestones()` entre refreshes | Cachear en `__init__` | Permite editar milestones.yaml y ver cambios con `r` sin reiniciar. |
| `── unassigned ──` oculto si vacío | Siempre mostrar | Menos ruido visual cuando todos los changes tienen milestone. |
| Milestones vacíos con búsqueda: omitidos | Mostrar con "(no matches)" | Consistente con el comportamiento actual de proyectos sin matches en multi-project. |
