# Proposal: Document viewer — ver proposal, design, spec y tasks desde la TUI

## Metadata
- **Change:** view-4-doc-viewer
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Proyecto:** sdd-tui
- **Estado:** approved

## Problema / Motivación

View 2 muestra el estado de las tareas y el pipeline de un change, pero para
leer el contenido real del change (qué propone, cómo está diseñado, qué spec
tiene) el usuario tiene que salir de la TUI y abrir los archivos manualmente.

La TUI debería ser la ventana completa al estado de un change: no solo su
progreso sino también su documentación.

## Solución Propuesta

Añadir teclas de acceso rápido en View 2 que abren una nueva pantalla
(DocumentViewerScreen) mostrando el contenido del documento seleccionado:

- `p` → `proposal.md`
- `d` → `design.md`
- `s` → spec(s) del change (si hay varios dominios, mostrar lista primero)
- `t` → `tasks.md`

El viewer renderiza el markdown con `rich.Markdown` (ya disponible como
dependencia de Textual) y es scrollable. Se cierra con Esc, volviendo a View 2.

Si el documento no existe, mostrar mensaje apropiado en lugar de error.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Panel inline en View 2 | Sin nueva pantalla | Poco espacio, complica layout existente | Descartada |
| Nueva pantalla (push_screen) | Pantalla completa, patrón ya establecido | — | **Elegida** |
| Specs concatenados | Un solo viewer | Sin distinción de dominio | Descartada |
| Specs con lista de selección | Claridad de dominio | Un paso extra solo cuando hay varios dominios | **Elegida** |
| Syntax highlight raw | Simple | Menos legible que markdown renderizado | Descartada |
| rich.Markdown renderizado | Headers, tablas, listas formateadas | — | **Elegida** |

## Impacto Estimado

- **Dominio:** tui
- **Archivos:** < 10 → Proceder
  - `src/sdd_tui/tui/doc_viewer.py` — nuevo (DocumentViewerScreen)
  - `src/sdd_tui/tui/change_detail.py` — añadir bindings p/d/s/t
  - `tests/test_doc_viewer.py` — tests del viewer (opcional, según complejidad)
- **Tests nuevos:** 2-4
- **Breaking changes:** No
- **Ramas dependientes:** No

## Criterios de Éxito

- [ ] `p` en View 2 abre proposal.md renderizado con markdown
- [ ] `d` abre design.md; `t` abre tasks.md
- [ ] `s` abre el spec si hay uno solo; muestra lista si hay varios dominios
- [ ] Si el archivo no existe, mensaje claro (no crash)
- [ ] Esc vuelve a View 2 sin perder el estado (tarea seleccionada, diff visible)
- [ ] El contenido es scrollable con flechas

## Preguntas Abiertas

Ninguna.

## Notas

- `rich.Markdown` ya disponible via Textual — no requiere dependencias nuevas
- El patrón `push_screen` / `pop_screen` está establecido en el proyecto
- El viewer es de solo lectura — no hay edición
