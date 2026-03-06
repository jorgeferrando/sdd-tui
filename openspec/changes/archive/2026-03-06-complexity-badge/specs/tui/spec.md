# Spec: TUI — Columna SIZE en EpicsView

## Metadata
- **Dominio:** tui
- **Change:** complexity-badge
- **Fecha:** 2026-03-06
- **Versión:** 2.0
- **Estado:** approved

## Contexto

Extensión de `EpicsView` (View 1). Añade una columna `SIZE` que muestra
el `complexity_label` de cada change, calculado por `parse_metrics`.

## Comportamiento Actual

`EpicsView` tiene 7 columnas: `change`, `propose`, `spec`, `design`, `tasks`, `apply`, `verify`.
No hay ninguna información de tamaño o complejidad.

---

## Requisitos (EARS)

- **REQ-CB-10** `[Event]` When `EpicsView` renders the change list, the system SHALL display a `SIZE` column showing `complexity_label` (XS/S/M/L/XL) for each change row.

- **REQ-CB-11** `[Ubiquitous]` The `SIZE` column SHALL be positioned between `change` and `propose`.

- **REQ-CB-12** `[State]` While `complexity_label == "XL"`, the system SHALL render the badge in yellow to signal a potential split candidate.

- **REQ-CB-13** `[Ubiquitous]` Separator rows (project headers, archived header) SHALL show an empty string in the `SIZE` column.

- **REQ-CB-14** `[Ubiquitous]` The system SHALL compute `ChangeMetrics` (including complexity) for each visible change during `_populate`.

- **REQ-CB-15** `[Unwanted]` If `parse_metrics` fails for any reason, the system SHALL show `"?"` in the `SIZE` column without crashing.

### Layout actualizado

```
change              SIZE  propose  spec  design  tasks  apply  verify
skill-palette       M     ✓        ✓     ✓       ✓      8/8    ✓
complexity-badge    XS    ✓        ✓     ✓       ✓      ·      ·
── archived ──            ──       ──    ──      ──     ──     ──
view-1-epics        S     ✓        ✓     ✓       ✓      3/3    ✓
```

### Escenarios de verificación

**REQ-CB-12** — badge XL en amarillo
**Dado** un change con `complexity_label = "XL"`
**Cuando** se renderiza en `EpicsView`
**Entonces** la celda `SIZE` muestra "XL" con `style="yellow"`

**REQ-CB-13** — separadores sin badge
**Dado** una fila de separador (`─── project ───` o `── archived ──`)
**Cuando** se añade a la tabla
**Entonces** la columna `SIZE` es `""`

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Columna entre `change` y `propose` | Al final de la tabla | Es información de contexto sobre el change, no sobre su estado de pipeline |
| Calcular métricas en `_populate` | Cachear en `Change` | `Change` es modelo de dominio — no debe llevar métricas de presentación |
| `"?"` en caso de error | `"—"` o crash | `"?"` señala problema sin romper la vista |

## Abierto / Pendiente

Ninguno.
