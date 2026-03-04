# Spec: Core — Cleanup Spec Debt

## Metadata
- **Dominio:** core
- **Change:** cleanup-spec-debt
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 0.1
- **Estado:** draft

## Contexto

La spec canónica `openspec/specs/core/spec.md` (v0.6) contiene la sección 6
(Transport Protocol) que documenta `TmuxTransport`, `ZellijTransport` y
`detect_transport()`. Este código fue eliminado completamente en el change
`cleanup-remove-transports` (archivado 2026-03-03), pero la sección sobrevivió
en la spec canónica.

Adicionalmente, el directorio `openspec/changes/test-view2/` es un fixture
de prueba manual que sdd-tui interpreta como un change real, mostrándolo
en View 1 como si fuera parte del flujo SDD activo.

Ambas piezas de deuda minan la confianza en la spec como fuente de verdad.

## Comportamiento Actual

- La spec canónica v0.6 describe Transport Protocol (sección 6) con comportamiento
  que no existe en el código Python.
- `openspec/changes/test-view2/` existe con tareas pendientes (`[ ]`), aparece
  en la lista de changes activos de la app.

## Cambios (REMOVED)

### Sección 6 — Transport Protocol eliminada de la spec canónica

- **REQ-01** `[Ubiquitous]` `[REMOVED]` The core spec SHALL NOT document Transport Protocol, TmuxTransport, ZellijTransport, detect_transport, or rules RB-TR-01 through RB-TR-03.
- **REQ-02** `[Ubiquitous]` `[REMOVED]` The `openspec/changes/test-view2/` directory SHALL NOT exist in the repository.

### Registro histórico

La eliminación del Transport Protocol queda registrada en la tabla de Decisiones
Tomadas de la spec canónica para preservar la historia sin contaminar la spec activa.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Eliminar sección 6 completamente | Marcar como "deprecated" | Spec que describe código inexistente no es fuente de verdad |
| Añadir nota en Decisiones Tomadas de spec canónica | Eliminar sin registro | Preserva la historia de por qué se eliminó Transport |
| Eliminar test-view2 directamente | Mover a tests/fixtures/ | Sin valor real como fixture; tui-tests creará sus propios fixtures |

## Abierto / Pendiente

Ninguno.
