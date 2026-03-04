# Proposal: openspec enrichment (steering + requirements + spec.json)

## Metadata
- **Change:** openspec-enrichment
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

El formato `openspec/` es funcional pero le falta contexto global del proyecto
y metadata estructurada por change. Kiro resuelve esto con `steering.md` y
`spec.json`. En lugar de soportar Kiro como formato externo, incorporamos sus
fortalezas directamente en openspec.

Problemas concretos:
1. No hay forma de documentar el contexto del proyecto (stack, convenciones,
   arquitectura) dentro de openspec/ de forma visible para agentes y TUI.
2. Los requisitos EARS quedan mezclados con el spec técnico — difícil
   separarlos para métricas o reporting.
3. No hay metadata estructurada por change legible por máquinas sin parsear
   markdown.

## Solución Propuesta

### 1. steering.md — contexto global del proyecto

Archivo `openspec/steering.md` (raíz del openspec, no dentro de un change).
Markdown libre. Contiene lo que cualquier agente o desarrollador necesita
saber antes de hacer cambios: stack, convenciones, decisiones de arquitectura,
objetivos actuales.

La TUI lo muestra desde View 1 con binding `S` → `SteeringScreen`.

### 2. requirements.md — requisitos separados del spec

Archivo opcional en `openspec/changes/{change}/requirements.md`.
Contiene exclusivamente los requisitos EARS del change, separados del
análisis técnico en `spec.md`.

Beneficios:
- Métricas más precisas (REQs en archivo dedicado vs mezclados en spec)
- El agente SDD puede generar/actualizar solo los requirements sin tocar el spec
- SpecHealthScreen (View 8) muestra columna `Q` si existe

### 3. spec.json — metadata estructurada por change

Archivo opcional en `openspec/changes/{change}/spec.json`.
Snapshot legible por máquinas del estado del change: pipeline, tasks, REQs.

Generado por CLI (change `cli-commands`) o por el agente SDD.
Core lee spec.json si existe; no es authoritative — la TUI siempre recomputa
desde disco.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Soportar .kiro/specs/ como formato externo | Interoperabilidad con cc-sdd | Mantener 2 formatos; adapters con deuda técnica | Descartada |
| steering.md como YAML | Structured, parseable | Menos legible por humanos y agentes; markdown es más natural | Descartada |
| spec.json como fuente de verdad | Lectura rápida sin parsear markdown | Introduce estado propio; riesgo de drift con realidad en disco | Descartada |
| **Enriquecer openspec nativo** | Un solo formato; sin breaking changes | 3 artefactos nuevos a mantener | **Elegida** |

## Impacto Estimado

- **Dominio:** core + tui
- **Archivos:** 8-12
  - `core/reader.py` — añadir `load_steering()`, `load_spec_json()`
  - `core/metrics.py` — detectar `requirements.md` como artefacto, leer REQs de ahí
  - `tui/app.py` — pasar steering_content a app
  - `tui/epics.py` — binding `S` → SteeringScreen
  - `tui/steering.py` — nuevo: SteeringScreen
  - `tui/change_detail.py` — binding `q` → requirements.md viewer
  - `tui/spec_health.py` — columna Q para requirements
  - `tests/` — unit tests por función nueva
- **Breaking changes:** No. Todos los artefactos son opcionales y retrocompatibles.
- **Dependencias:** Independiente de cli-commands (que lo construye encima).

## Criterios de Éxito

- [ ] `openspec/steering.md` se muestra en TUI con `S` desde View 1
- [ ] `requirements.md` por change detectado como artefacto en SpecHealthScreen
- [ ] `load_spec_json()` retorna dict o None sin lanzar excepciones
- [ ] Proyectos sin steering.md ni requirements.md funcionan igual que antes

## Preguntas Abiertas

- [ ] ¿steering.md tiene una estructura recomendada o es completamente libre?

## Notas

Este change es la base del formato openspec v2.
El change `cli-commands` (siguiente) construye la interfaz CLI encima
de los readers definidos aquí.
