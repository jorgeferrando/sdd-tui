# Proposal: View 9 — Delta Specs Viewer

## Metadata
- **Change:** view-9-delta-specs
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

Las specs canónicas en `openspec/specs/{dominio}/spec.md` acumulan cambios
de múltiples ciclos pero no muestran su historia. Al leer una spec hoy no
sabes qué cambió en el último ciclo, qué se añadió hace tres semanas ni
por qué se eliminó un requisito.

Dos síntomas concretos:

1. **Contexto perdido**: al revisar `design.md` de un change nuevo, el lector
   no sabe qué parte de la spec canónica es prerrequisito y qué parte es
   la novedad que este change introduce.

2. **Decisiones dispersas**: cada `design.md` tiene una sección
   "Decisiones Tomadas" pero están aisladas por change. No hay vista
   cross-change de por qué el sistema tiene la forma que tiene hoy.

## Solución Propuesta

### Marcadores explícitos en delta specs

Adoptar la convención de OpenSpec para las specs dentro de
`openspec/changes/{change}/specs/`:

```markdown
## ADDED Requirements
- **REQ-01** `[Event]` When...

## MODIFIED Requirements
- **REQ-03** — Before: "..."  After: "..."

## REMOVED Requirements
- **REQ-02** — Removed because: ...
```

El archivo delta describe solo el delta, no la spec completa. Al archivar,
`sdd-archive` fusiona los marcadores en la spec canónica.

### View 9 — Spec Evolution Viewer

Nueva pantalla accesible con `E` desde View 2 (ChangeDetailScreen):

- **Panel izquierdo**: lista de dominios con specs en el change actual
- **Panel derecho**: diff visual de la spec con ADDED (verde) /
  MODIFIED (amarillo) / REMOVED (rojo)
- **Toggle `D`**: cambiar entre "delta del change" y "spec canónica completa"

### Decisions Timeline

Accesible con `X` desde View 1 (EpicsView): agrega las secciones
"Decisiones Tomadas" de todos los `design.md` archivados, ordenadas
cronológicamente. Una línea de tiempo de por qué el sistema evoluciona.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| `git diff` entre versiones de spec.md | Sin formato especial | Specs se reescriben completas, diff git es ruidoso | Descartada |
| **Marcadores ADDED/MODIFIED/REMOVED** | Explícito, semántico, parseble | Requiere disciplina al escribir specs | **Elegida** |
| Historial inline con `<!-- v0.3: ... -->` | Sin archivo extra | Contamina el contenido de la spec | Descartada |

## Impacto Estimado

- **Dominio:** tui + core
- **Archivos:** < 10
  - `core/spec_parser.py` — nuevo: parser de marcadores ADDED/MODIFIED/REMOVED
  - `tui/spec_evolution.py` — nuevo: SpecEvolutionView
  - `tui/decisions_timeline.py` — nuevo: DecisionsTimeline
  - `tui/change_detail.py` — modificado: binding `E`
  - `tui/epics.py` — modificado: binding `X`
  - `sdd-spec SKILL.md` — ya actualizado con EARS; añadir convención de marcadores
- **Tests nuevos:** unit tests para `core/spec_parser.py`
- **Breaking changes:** No. Los delta specs existentes sin marcadores se muestran tal cual.
- **Dependencias:** Se apoya en el parser de `view-8-spec-health` (reutiliza detección de REQ-XX)

## Criterios de Éxito

- [ ] `E` en View 2 abre SpecEvolutionView con el delta del change actual
- [ ] Los bloques ADDED/MODIFIED/REMOVED se colorean en verde/amarillo/rojo
- [ ] El toggle `D` alterna entre delta y spec canónica completa
- [ ] `X` en View 1 abre DecisionsTimeline con decisiones de todos los changes archivados
- [ ] Specs sin marcadores (formato libre) se muestran sin error como texto plano

## Preguntas Abiertas

- [ ] ¿`sdd-archive` debe validar que el delta tiene marcadores o solo recomendar?
- [ ] ¿La Decisions Timeline ordena por fecha de commit o por fecha en metadata?

## Notas

Este change introduce una convención nueva en el formato de los archivos
delta spec. No rompe los archivos existentes (se muestran en modo fallback),
pero los nuevos specs deben seguir el formato para obtener el diff coloreado.

La convención ADDED/MODIFIED/REMOVED está alineada con OpenSpec (27k stars),
lo que facilita la futura compatibilidad del Universal Reader (core-universal-reader).
