# Design: Cleanup Spec Debt

## Metadata
- **Change:** cleanup-spec-debt
- **Fecha:** 2026-03-04

## Archivos a Modificar

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `openspec/specs/core/spec.md` | Modificar | Eliminar sección 6, bump v0.6 → v0.7, añadir entrada histórica en Decisiones Tomadas |
| `openspec/changes/test-view2/` | Eliminar | `git rm -r` del directorio completo |

## Detalle de Implementación

### T01 — Editar spec canónica

**`openspec/specs/core/spec.md`**

1. Cambiar `**Versión:** 0.6` → `**Versión:** 0.7`
2. Cambiar `**Change:** openspec-enrichment` → `**Change:** cleanup-spec-debt`
3. Eliminar las líneas 273-309 completas (sección `## 6. Transport — Comunicación inter-panel`, incluyendo el separador `---` previo y la sección entera hasta el siguiente `---`)
4. Añadir en la tabla de **Decisiones Tomadas** la fila histórica:

```
| Transport Protocol eliminado (TmuxTransport, ZellijTransport, detect_transport) | Mantener como feature activa | Complejidad sin retorno: tmux/zellij targeting no fiable. Eliminado en cleanup-remove-transports (2026-03-03) |
```

### T02 — Eliminar test-view2

```bash
git rm -r openspec/changes/test-view2/
```

Elimina `proposal.md`, `design.md`, `tasks.md`, `specs/` del fixture de prueba.
El directorio desaparecerá del listing de View 1 en sdd-tui.

## Decisiones de Diseño

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Mantener registro en Decisiones Tomadas | Borrar sin rastro | La tabla de decisiones es el historial semántico del dominio |
| `git rm` para test-view2 | Borrado manual de archivo | `git rm` garantiza que el cambio queda en el índice git |
| Un commit por tarea | Commit único con ambas | Atomicidad — spec edit y fixture delete son cambios independientes |

## Verificación

- `openspec/specs/core/spec.md` no contiene "Transport", "TmuxTransport", "ZellijTransport", "detect_transport", "RB-TR"
- `openspec/changes/test-view2/` no existe en el filesystem ni en git
- View 1 del app no muestra `test-view2` en la lista de changes
