# Proposal: Convención de diagramas Mermaid en SDD docs

## Metadata
- **Change:** mermaid-diagrams
- **Jira:** N/A
- **Fecha:** 2026-03-11
- **Proyecto:** sdd-tui (skills ~/.claude/skills/)
- **Estado:** draft

## Problema / Motivación

Los `design.md` actuales describen arquitectura y flujos con árboles ASCII y texto
libre. Para cambios con ≥3 componentes relacionados (ej: `provider-abstraction`,
`observatory-v1`) la sección de Arquitectura se convierte en un árbol de texto que
simula un diagrama pero sin expresar bien las relaciones (herencia, secuencia,
dependencias). No hay convención establecida sobre cuándo o qué tipo de diagrama usar.

Los archivos `.md` viven en GitHub (repo público) donde Mermaid se renderiza
natively. En el TUI (`rich.Markdown`) los bloques `mermaid` aparecen como código —
comportamiento de fallback aceptable para documentación de diseño.

## Solución Propuesta

Añadir convención de diagramas Mermaid a las skills SDD:

1. **`sdd-design` SKILL.md** — Sección explícita en el template de `design.md`:
   - Regla de activación: ≥3 componentes con relaciones entre sí
   - Tipos recomendados por situación (class, sequence, flowchart, stateDiagram)
   - El bloque de Arquitectura actual ("Diagrama ASCII o descripción") se reemplaza
     por "Diagrama Mermaid (obligatorio si ≥3 componentes, opcional si < 3)"

2. **`sdd-propose` SKILL.md** — Nota opcional en el template de `proposal.md`:
   - Solo cuando el scope implica múltiples sistemas o actores interactuando
   - Un `flowchart LR` de contexto que muestre quién hace qué

No se crea una skill nueva. No se tocan otros documentos.

## Alternativas Consideradas

| Alternativa | Desventajas | Decisión |
|------------|------------|---------|
| ASCII art UML (hand-crafted) | Verbose, difícil mantener, bajo ratio señal/ruido | Descartada |
| PlantUML | Necesita servidor externo para renderizar | Descartada |
| Skill `sdd-diagram` separada | Overhead innecesario — no requiere tool use | Descartada |
| **Mermaid integrado en skills existentes** | — | **Elegida** |

## Impacto Estimado

- **Dominio:** skills SDD (prompts, no código ejecutable)
- **Archivos:** 2 (sdd-design/SKILL.md, sdd-propose/SKILL.md) → Ideal
- **Tests nuevos:** 0 (las skills son prompt-only)
- **Breaking changes:** No — es una adición al template, no modifica behaviour existente
- **Ramas dependientes:** No

## Criterios de Éxito

- [ ] `sdd-design` SKILL.md tiene regla clara de cuándo usar diagrama y qué tipo
- [ ] Template de `design.md` en sdd-design usa `mermaid` en lugar de "ASCII o descripción"
- [ ] `sdd-propose` SKILL.md menciona diagram de contexto como opción para scopes complejos
- [ ] La regla "≥3 componentes" previene diagramas innecesarios en changes simples

## Preguntas Abiertas

_(ninguna — scope claro)_

## Notas

- Tipos de diagrama por uso: `classDiagram` para modelos/Protocols, `sequenceDiagram`
  para flujos de UI/async, `flowchart LR` para navegación y contexto, `stateDiagram-v2`
  para estados de pipeline
- Los diagramas son snapshot del diseño — no son fuente de verdad, el código lo es
- Referencia: evaluación inicial en conversación del 2026-03-11
