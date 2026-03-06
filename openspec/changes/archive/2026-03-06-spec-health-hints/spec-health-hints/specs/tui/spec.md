# Spec: TUI — SpecHealthScreen HINT column

## Metadata
- **Dominio:** tui
- **Change:** spec-health-hints
- **Fecha:** 2026-03-06
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Añadir columna `HINT` a `SpecHealthScreen`. Muestra el hint más urgente
inferido por `repair_hints()` para cada change. El usuario puede ver de un
vistazo qué acción tomar sin tener que interpretar los números de REQ/EARS/ARTIFACTS.

## ADDED

### Columna HINT en SpecHealthScreen

**Dado** `SpecHealthScreen` con la tabla de changes
**Cuando** se renderiza cada fila
**Entonces** aparece una columna `HINT` al final con el primer elemento de `repair_hints(metrics, change)`

### Requisitos (EARS)

- **REQ-SH-01** `[Event]` When `SpecHealthScreen` renders a change row, the system SHALL call `repair_hints(metrics, change)` and display the first element in the `HINT` column.
- **REQ-SH-02** `[Ubiquitous]` The `HINT` column SHALL be the last column in the table.
- **REQ-SH-03** `[Ubiquitous]` Separator rows (project names, `── archived ──`) SHALL display an empty string in the `HINT` column.
- **REQ-SH-04** `[Ubiquitous]` The hint `✓` SHALL be rendered in `green`; pipeline hints (`/sdd-*`) SHALL be rendered in `cyan`; quality hints (`add ...`) SHALL be rendered in `yellow`.

### Escenarios de verificación

**REQ-SH-01** — Hint visible en tabla
**Dado** un change con `pipeline.design == PENDING`
**Cuando** se abre `SpecHealthScreen`
**Entonces** la fila del change muestra `/sdd-design {name}` en la columna HINT

**REQ-SH-04** — Color según tipo de hint
**Dado** un change con todos los pipeline DONE y calidad OK
**Cuando** se renderiza la fila
**Entonces** la celda HINT muestra `✓` en verde

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| HINT como última columna | Primera columna | Las columnas de diagnóstico (REQ, EARS%) son el contexto previo al hint |
| Solo el primer hint | Múltiples hints concatenados | Menos ruido visual; el usuario puede abrir el change para más detalle |
| Color por tipo de hint | Sin color | Diferenciación visual inmediata sin leer el texto |

## Abierto / Pendiente

Ninguno.
