# Proposal: View 6 — Refresh in-place

## Metadata
- **Change:** view-6-refresh-in-place
- **Jira:** N/A
- **Fecha:** 2026-03-03

## Problema

Al pulsar `r` en View 2 (ChangeDetailScreen), la app recarga los datos pero regresa
a View 1 (pop_screen). El usuario pierde el contexto visual — tiene que volver a
seleccionar el mismo change para seguir trabajando.

## Solución Propuesta

Modificar `action_refresh_view` para que reemplace los widgets del panel superior
(TaskListPanel + PipelinePanel) con instancias frescas sin cerrar la pantalla.
El DiffPanel se resetea al placeholder inicial. View 1 (EpicsView) también se actualiza
para que al volver con Esc los datos sean consistentes.

## Alternativas Descartadas

| Alternativa | Razón de descarte |
|-------------|-------------------|
| `pop_screen` + re-push inmediato | Produce parpadeo visible; el cursor de View 1 se pierde un frame |
| Reactive data con `watch_*` | Over-engineering — los datos del change no son reactivos en la arquitectura actual |
| Re-compose completa de la pantalla | Textual no expone recompose en pantallas montadas de forma limpia |

## Impacto

- **Archivos:** 2 (`app.py`, `change_detail.py`)
- **Dominio:** tui
- **Tests:** sin tests automatizados nuevos (misma razón que view-5: requiere Pilot async)
