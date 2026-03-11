# Spec: Convención de diagramas Mermaid en SDD docs

## Metadata
- **Change:** mermaid-diagrams
- **Dominio:** tooling (skills SDD)
- **Fecha:** 2026-03-11
- **Estado:** draft

## Requisitos

### REQ-MD-01 — Regla de activación en design.md

En la sección `## Arquitectura` de `design.md`, se incluirá un diagrama Mermaid
cuando el design involucre ≥3 componentes con relaciones entre sí. Para designs
con < 3 componentes, el diagrama es opcional.

### REQ-MD-02 — Tipos de diagrama por situación

| Situación | Tipo Mermaid |
|-----------|-------------|
| Módulos, clases, Protocols, herencia, composición | `classDiagram` |
| Flujos temporales: wizard steps, async workers, peticiones/respuestas | `sequenceDiagram` |
| Navegación de screens, contexto del sistema, dependencias entre archivos | `flowchart LR` |
| Ciclo de vida de un objeto, estados de pipeline | `stateDiagram-v2` |

### REQ-MD-03 — Posición en design.md

El diagrama forma parte de la sección `## Arquitectura`, inmediatamente tras
el resumen técnico en prosa (si existe). No sustituye al texto — lo complementa.

### REQ-MD-04 — Diagrama de contexto opcional en proposal.md

En `proposal.md`, se puede incluir un diagrama `flowchart LR` en la sección
`## Solución Propuesta` cuando el scope involucre múltiples sistemas o actores
que interactúan. Para proposals de alcance interno (un módulo), es opcional y
frecuentemente innecesario.

### REQ-MD-05 — Fallback en TUI

Los bloques Mermaid aparecen como código en el TUI (`rich.Markdown`). Esto es
comportamiento aceptable — los diagramas son para documentación de diseño,
no para runtime display. No se requiere ningún cambio en el TUI.

### REQ-MD-06 — Los diagramas son snapshot, no fuente de verdad

Los diagramas en `design.md` reflejan el diseño en el momento de redacción.
Si la implementación diverge, el código es la fuente de verdad. No es obligatorio
actualizar los diagramas post-implementación.

## Comportamiento esperado

**Dado** un `design.md` con ≥3 componentes con relaciones
**Cuando** se ejecuta `sdd-design`
**Entonces** la sección `## Arquitectura` contiene un bloque ` ```mermaid ` con el
tipo apropiado según REQ-MD-02

**Dado** un `design.md` con < 3 componentes
**Cuando** se ejecuta `sdd-design`
**Entonces** la sección `## Arquitectura` puede usar texto libre o diagrama — a
criterio del autor

**Dado** un `proposal.md` para un cambio con múltiples sistemas interactuando
**Cuando** se ejecuta `sdd-propose`
**Entonces** la sección `## Solución Propuesta` puede incluir un `flowchart LR`
de contexto (no obligatorio)

## Fuera de Scope

- Renderizado de Mermaid en el TUI
- Validación automática de diagramas
- Diagramas en `tasks.md` (innecesario — estructura de tareas ya es clara)
- Diagramas en specs canónicas (`openspec/specs/`) — no hay convención establecida,
  se puede añadir en el futuro si se necesita
