# Spec: TUI — Refresh in-place (View 6)

## Metadata
- **Dominio:** tui
- **Change:** view-6-refresh-in-place
- **Fecha:** 2026-03-03
- **Versión:** delta
- **Estado:** approved

## Comportamiento Esperado

### Caso Principal

**Dado** View 2 (ChangeDetailScreen) abierto con un change seleccionado
**Cuando** el usuario pulsa `r`
**Entonces:**
- Los datos del change se recargan desde disco y git
- TaskListPanel se actualiza con el nuevo estado de las tareas
- PipelinePanel se actualiza con el nuevo estado del pipeline
- DiffPanel muestra el placeholder `Select a task to view its diff`
- La pantalla sigue siendo View 2 (no hay pop_screen)
- View 1 (EpicsView) también se actualiza con los datos frescos

### Caso alternativo — change desaparecido

**Dado** View 2 abierto con un change que ha sido eliminado del filesystem
**Cuando** el usuario pulsa `r`
**Entonces:**
- Aparece una notificación `Change not found — returning to list`
- Se hace pop_screen y se vuelve a View 1

## Reglas de Negocio

- **RB-V6-01:** `r` recarga en sitio — no cierra View 2.
- **RB-V6-02:** El DiffPanel se resetea al placeholder tras cada refresh.
- **RB-V6-03:** View 1 se actualiza en el mismo refresh (datos consistentes).
- **RB-V6-04:** Si el change no existe tras recargar → pop_screen + notify.
- **RB-V6-05:** El DataTable recupera el foco después del refresh.
