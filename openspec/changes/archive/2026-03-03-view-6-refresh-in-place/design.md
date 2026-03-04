# Design: View 6 — Refresh in-place

## Metadata
- **Change:** view-6-refresh-in-place
- **Fecha:** 2026-03-03
- **Estado:** approved

## Resumen Técnico

`refresh_changes()` en `SddTuiApp` pasa a devolver `list[Change]` (antes `None`).
`action_refresh_view` usa esa lista para localizar el change activo, elimina
`TaskListPanel` y `PipelinePanel` del DOM con `.remove()`, monta instancias nuevas
con `.mount()`, y resetea el DiffPanel al placeholder.

## Arquitectura

```
[r] → ChangeDetailScreen.action_refresh_view()
          │
          ├── self.app.refresh_changes()  ← devuelve list[Change]
          │         └── actualiza EpicsView (View 1)
          │
          ├── fresh_change = next((c for c in changes if c.name == self._change.name), None)
          │
          ├── Si None → notify + pop_screen
          │
          ├── self._change = fresh_change
          ├── TaskListPanel.remove() + PipelinePanel.remove()
          ├── top.mount(TaskListPanel(...), PipelinePanel(...))
          ├── DiffPanel.show_message("Select a task to view its diff")
          └── call_after_refresh → DataTable.focus()
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/app.py` | `refresh_changes()` devuelve `list[Change]` | `action_refresh_view` necesita los datos frescos sin doble carga |
| `src/sdd_tui/tui/change_detail.py` | `action_refresh_view()` reemplaza widgets en sitio | Implementar refresh in-place |

## Scope

- **Total archivos:** 2
- **Resultado:** Ideal

## Detalle de Implementación

### `app.py` — `refresh_changes`

```python
def refresh_changes(self) -> list[Change]:
    changes = self._load_changes()
    self.query_one(EpicsView).update(changes)
    return changes
```

### `change_detail.py` — `action_refresh_view`

```python
def action_refresh_view(self) -> None:
    changes = self.app.refresh_changes()  # type: ignore[attr-defined]
    fresh_change = next(
        (c for c in changes if c.name == self._change.name), None
    )
    if fresh_change is None:
        self.notify("Change not found — returning to list")
        self.app.pop_screen()
        return
    self._change = fresh_change
    top = self.query_one(".top-panel", Horizontal)
    self.query_one(TaskListPanel).remove()
    self.query_one(PipelinePanel).remove()
    top.mount(
        TaskListPanel(self._change.tasks),
        PipelinePanel(self._change.pipeline, self._change.tasks),
    )
    self.query_one(DiffPanel).show_message("Select a task to view its diff")
    self.call_after_refresh(lambda: self.query_one(DataTable).focus())
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `refresh_changes()` devuelve `list[Change]` | Segunda llamada a `_load_changes()` | Evita doble carga; un solo recorrido del filesystem |
| `.remove()` + `.mount()` | Re-compose completa de la pantalla | Textual soporta mount/remove en widgets montados; más quirúrgico |
| Resetear DiffPanel al placeholder | Mantener diff actual | El diff puede estar obsoleto tras el refresh (nuevo commit, etc.) |
| `call_after_refresh` para foco | Focus inmediato | Mismo patrón que `on_mount` — el DataTable nuevo necesita un frame |

## Tests Planificados

Sin tests automatizados nuevos — requiere Pilot async (TUI testing) que el proyecto
no tiene todavía. Cobertura via smoke test en QG.
