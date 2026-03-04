# Proposal: View 7 — Mostrar/ocultar archivados en View 1

## Metadata
- **Change:** view-7-show-archived
- **Jira:** N/A
- **Fecha:** 2026-03-03

## Problema

View 1 (EpicsView) solo muestra changes activos. No hay forma de consultar los
archivados sin salir del TUI. El directorio `archive/` existe y tiene el mismo
formato que los changes activos, por lo que consultarlo desde la UI añade valor.

## Solución Propuesta

Binding `a` en View 1 que alterna entre mostrar solo activos y mostrar activos +
archivados. Los archivados aparecen debajo de los activos, separados por una fila
`── archived ──`. La selección de un archivado abre View 2 en modo read-only
(mismo comportamiento que para activos).

## Alternativas Descartadas

| Alternativa | Razón |
|-------------|-------|
| Vista separada para archivados | Over-engineering; una sola lista con toggle es más simple |
| Siempre mostrar archivados | La lista puede ser muy larga; mejor opt-in |
| Columna extra "status" | Ocupa espacio; el separador de sección es más limpio |

## Impacto

- **Archivos:** 4 (`models.py`, `reader.py`, `app.py`, `epics.py`)
- **Dominio:** tui, core
- **Tests:** actualizar tests del reader si los hay
