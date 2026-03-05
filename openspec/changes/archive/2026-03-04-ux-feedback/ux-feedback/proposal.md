# Proposal: UX Feedback — Estado Visual y Notificaciones

## Metadata
- **Change:** ux-feedback
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

La app ejecuta acciones sin dar ningún feedback al usuario sobre el resultado.
Esto genera tres problemas concretos:

### Problema 1 — Toggle archived sin estado visible

`a` en View 1 alterna la visibilidad de changes archivados, pero el footer
siempre muestra "Archived" — sin diferencia visual entre ON y OFF. El usuario
tiene que contar filas para saber si los archivados están visibles o no.

### Problema 2 — Acciones sin notificación de éxito

Solo existen dos `notify` en toda la app: al copiar un comando y al fallar
un refresh. Abrir un documento, completar un refresh de View 1, togglear
archived — ninguna acción confirma que ocurrió. En una TUI donde las acciones
son instantáneas y silenciosas, el usuario puede repetir una acción creyendo
que no funcionó.

### Problema 3 — Archivo no encontrado sin aviso prominente

Cuando un artefacto no existe (proposal.md, design.md, etc.), la pantalla
`DocumentViewerScreen` muestra `"[dim]filename not found[/dim]"` en el cuerpo
del documento. Este mensaje es fácil de no ver, especialmente si el usuario
asume que el documento se cargó correctamente.

### Problema 4 — `q` sin binding en SpecSelectorScreen

El selector de specs (`SpecSelectorScreen`) solo acepta `Escape` para cerrarse.
En el contexto de View 2, `q` abre requirements — el usuario que intenta `q`
para cerrar el selector no obtiene ningún resultado, rompiendo la expectativa
de que `q` tiene un efecto en cualquier pantalla.

## Solución Propuesta

### Fix 1 — Indicador de estado en toggle archived

Cambiar el label del binding `a` en `EpicsView` dinámicamente:
- Cuando archivados están ocultos: `"Show archived"`
- Cuando archivados están visibles: `"Hide archived"`

Implementación: invalidar los bindings con `self.refresh_bindings()` tras
togglear `_show_archived`, y hacer el label dependiente del estado.

### Fix 2 — Notify en acciones exitosas

Añadir `self.notify(...)` en:
- `EpicsView.action_refresh`: `"Changes refreshed"` (o con conteo: `"X changes loaded"`)
- `EpicsView.action_toggle_archived`: ya cubierto por el cambio de label del Fix 1
- `ChangeDetailScreen` al abrir cualquier doc: `"Opening {filename}"` (solo si el archivo existe)

### Fix 3 — Warning prominente para archivo no encontrado

En `DocumentViewerScreen`, cuando el archivo no existe:
- Añadir `self.app.notify("{filename} not found", severity="warning")` además del mensaje en el cuerpo.
- Esto asegura que el aviso sea visible independientemente del contenido renderizado.

### Fix 4 — Binding `q` en SpecSelectorScreen

Añadir `("q", "app.pop_screen", "Close")` a `BINDINGS` de `SpecSelectorScreen`.
Consistente con el hecho de que en esa pantalla no hay acción de "requirements"
— `q` puede simplemente cerrar.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Status bar persistente con estado global | Información siempre visible | Complejidad de layout + overhead para info efímera | Descartada |
| Color diferente en header cuando archivados visibles | Visual sin texto | Sutil, puede no notarse | Descartada |
| **Label dinámico + notify puntual** | Bajo overhead, información en contexto | Notificaciones efímeras desaparecen | **Elegida** |
| Mantener `q` distinto entre SpecSelectorScreen y View 2 | Coherencia interna de View 2 | Inconsistencia con expectativa de "q cierra" en selectores | Añadir binding es mejor |

## Impacto Estimado

- **Dominio:** tui (UI layer únicamente)
- **Archivos modificados:**
  - `tui/epics.py` — label dinámico + notify en refresh
  - `tui/change_detail.py` — notify al abrir docs
  - `tui/doc_viewer.py` — notify warning en not found + binding `q` en SpecSelectorScreen
- **Breaking changes:** Ninguno
- **Tests afectados:** Si existen tests de EpicsView que validen bindings, necesitarán actualización

## Criterios de Éxito

- [ ] El footer de View 1 muestra "Show archived" / "Hide archived" según el estado actual
- [ ] Hacer refresh en View 1 muestra una notificación de éxito
- [ ] Abrir un documento existente muestra `"Opening {filename}"`
- [ ] Intentar abrir un documento inexistente muestra una notificación `severity="warning"`
- [ ] `q` en `SpecSelectorScreen` cierra la pantalla

## Preguntas Abiertas

- [ ] ¿El notify al abrir docs debe incluir el nombre corto ("proposal") o la ruta completa?
- [ ] ¿Añadir conteo de changes al notify de refresh: `"12 changes loaded (3 archived)"`?
