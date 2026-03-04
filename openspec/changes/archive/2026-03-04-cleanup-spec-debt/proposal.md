# Proposal: Cleanup — Spec Debt

## Metadata
- **Change:** cleanup-spec-debt
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

El proyecto tiene dos piezas de deuda que minan la confianza en las specs
canónicas como fuente de verdad:

### Deuda 1 — Sección Transport en core/spec.md

La sección 6 de `openspec/specs/core/spec.md` documenta el `Transport Protocol`
(TmuxTransport, ZellijTransport, detect_transport). El código fue eliminado
completamente en el change `cleanup-remove-transports` (archivado
`2026-03-03-cleanup-remove-transports`), pero la documentación sobrevivió
en la spec canónica.

El resultado: la spec v0.6 describe comportamiento que no existe en el código.
Un nuevo colaborador (o agente) leyendo la spec buscaría `core/transport.py`
o esperaría encontrar `TmuxTransport` — no los encontraría.

Una spec que describe código inexistente no es una fuente de verdad; es un
documento que activamente confunde.

### Deuda 2 — Fixture `test-view2` en openspec/changes/

El directorio `openspec/changes/test-view2/` es un fixture de prueba manual
creado durante el desarrollo. Contiene `proposal.md`, `design.md`, `tasks.md`
con tareas T04 y T06 pendientes.

Aparece en la lista de changes activos de la propia app (View 1). sdd-tui
muestra su propio ruido interno como si fuera un change real. El producto
se visualiza a sí mismo de forma incorrecta.

## Solución Propuesta

### Tarea 1 — Eliminar sección Transport del spec canónico

Editar `openspec/specs/core/spec.md`: eliminar la sección 6 completa
(Transport Protocol — TmuxTransport, ZellijTransport, detect_transport,
reglas RB-TR-01 a RB-TR-03) y añadir una nota en el header de la spec
que registre el cambio de versión.

La sección de Decisiones Tomadas de la spec canónica puede preservar
la decisión de eliminar transports como registro histórico.

### Tarea 2 — Eliminar test-view2

Eliminar el directorio `openspec/changes/test-view2/` del repositorio.

Si se necesitan fixtures de prueba para tests de TUI (change `tui-tests`),
deben vivir en `tests/fixtures/` como archivos de texto — no en
`openspec/changes/` donde la app los interpreta como changes reales.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Marcar Transport como "deprecated" en el spec | Conserva historia | Confusión persiste; spec sigue describiendo código inexistente | Descartada |
| Mover test-view2 a tests/fixtures/ | Reutilizable en tests | Requiere coordinar con tui-tests | Considerada — depende del timing con tui-tests |
| **Eliminar ambas piezas directamente** | Spec limpio, sin ruido | Pérdida de fixture manual (sin valor real) | **Elegida** |

## Impacto Estimado

- **Dominio:** openspec (specs canónicas) + openspec/changes/
- **Archivos modificados:**
  - `openspec/specs/core/spec.md` — eliminar sección 6 + actualizar versión a 0.7
- **Archivos eliminados:**
  - `openspec/changes/test-view2/` (directorio completo)
- **Breaking changes:** Ninguno — no toca código Python
- **Tests afectados:** Ninguno — el core spec no tiene tests que lo referencien

## Criterios de Éxito

- [ ] `openspec/specs/core/spec.md` no menciona Transport, TmuxTransport ni ZellijTransport
- [ ] `openspec/changes/test-view2/` no existe
- [ ] View 1 del app no muestra `test-view2` en la lista de changes
- [ ] La versión del spec core refleja el cambio (v0.7)

## Preguntas Abiertas

- [ ] ¿Añadir nota explícita en Decisiones Tomadas del spec core indicando cuándo y por qué se eliminaron los transports?
- [ ] ¿Coordinación con `tui-tests`: ¿debería `tui-tests` crear sus propios fixtures en `tests/fixtures/` antes de que este change elimine `test-view2`?
