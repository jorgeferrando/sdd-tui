# Design: UX Navigation (Scroll, Drill-down, Paths)

## Metadata
- **Change:** ux-navigation
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

Tres fixes quirúrgicos en la capa TUI. Ninguno requiere cambios en `core/`.
El patrón de `_change_map` + `on_data_table_row_selected` ya existe en `EpicsView`
y se replica tal cual en `SpecHealthScreen`. Los bindings `j/k` son acciones nativas
de `ScrollableContainer` — cero implementación custom. Los paths hardcodeados se
corrigen usando `self.app._openspec_path` que ya existe en `SddTuiApp`.

## Arquitectura

```
Fix 1 — j/k scroll
  DocumentViewerScreen.BINDINGS += j/k → scroll_down / scroll_up (nativo Textual)
  SpecEvolutionScreen.BINDINGS  += j/k
  DecisionsTimeline.BINDINGS    += j/k

Fix 2 — Drill-down SpecHealthScreen
  SpecHealthScreen._populate()           → build _change_map {name: Change}
  SpecHealthScreen.on_data_table_row_selected → _change_map.get(key) → push_screen(ChangeDetailScreen)

Fix 3 — Paths
  EpicsView.action_steering              Path.cwd()/"openspec" → self.app._openspec_path
  EpicsView.action_decisions_timeline    Path.cwd()/"openspec" → self.app._openspec_path
  SpecEvolutionScreen._render_domain     Path.cwd()/"openspec" → self.app._openspec_path

Fix 4 — app.changes propiedad pública
  SddTuiApp.changes @property → return self._changes
```

## Archivos a Modificar

| Archivo | Cambio | REQ |
|---------|--------|-----|
| `tui/app.py` | Añadir `@property changes` que retorna `self._changes` | REQ-07 |
| `tui/doc_viewer.py` | `DocumentViewerScreen.BINDINGS` + `j`/`k` | REQ-01/02/03 |
| `tui/spec_evolution.py` | `SpecEvolutionScreen.BINDINGS` + `j`/`k`; `DecisionsTimeline.BINDINGS` + `j`/`k`; `_render_domain` canonical path fix | REQ-01/02/03/08 |
| `tui/spec_health.py` | `_change_map` en `__init__` + `_populate()`; `on_data_table_row_selected`; import `ChangeDetailScreen` | REQ-04/05/06 |
| `tui/epics.py` | `action_steering` y `action_decisions_timeline` path fix | REQ-08 |

## Scope

- **Total archivos:** 5
- **Resultado:** Ideal (< 10)

## Detalles de Implementación

### `tui/app.py` — propiedad `changes`

```python
@property
def changes(self) -> list[Change]:
    return self._changes
```

Añadir después de `__init__`. El atributo `_changes` no existe actualmente como atributo de instancia directo — `_load_changes()` retorna la lista cada vez. Revisar si `EpicsView` guarda la lista internamente o si hay que introducir `self._changes` en `SddTuiApp`.

> **Nota:** Inspeccionando `app.py`, `SddTuiApp` no almacena `_changes` — la lista vive en `EpicsView._changes`. La propiedad pública debería delegar a `EpicsView`: `return self.query_one(EpicsView)._changes`. Esto es lo que ya hace `action_health` de `EpicsView` cuando pasa `self._changes` a `SpecHealthScreen`. La propiedad en `app.py` queda así:

```python
@property
def changes(self) -> list[Change]:
    from sdd_tui.tui.epics import EpicsView
    return self.query_one(EpicsView)._changes
```

### `tui/doc_viewer.py` — bindings `j/k`

```python
# DocumentViewerScreen
BINDINGS = [
    Binding("j", "scroll_down", "Down"),
    Binding("k", "scroll_up", "Up"),
    Binding("escape", "app.pop_screen", "Back"),
]
```

`scroll_down` y `scroll_up` son acciones heredadas de `ScrollableContainer`
(el widget raíz de `DocumentViewerScreen`). Sin override.

### `tui/spec_evolution.py` — bindings `j/k` y path fix

```python
# SpecEvolutionScreen
BINDINGS = [
    Binding("j", "scroll_down", "Down"),
    Binding("k", "scroll_up", "Up"),
    Binding("escape", "app.pop_screen", "Back"),
    Binding("d", "toggle_canonical", "Toggle canonical"),
]

# DecisionsTimeline
BINDINGS = [
    Binding("j", "scroll_down", "Down"),
    Binding("k", "scroll_up", "Up"),
    Binding("escape", "app.pop_screen", "Back"),
]
```

Path fix en `_render_domain`:
```python
# Antes (línea 88)
canonical = Path.cwd() / "openspec" / "specs" / domain / "spec.md"
# Después
canonical = self.app._openspec_path / "specs" / domain / "spec.md"
```

### `tui/spec_health.py` — drill-down

```python
# En __init__
self._change_map: dict[str, Change] = {}

# En _populate() — tras add_row de cada change (activo y archivado)
self._change_map[change.name] = change

# Nuevo handler
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    from sdd_tui.tui.change_detail import ChangeDetailScreen
    if event.row_key is None or event.row_key.value is None:
        return
    change = self._change_map.get(event.row_key.value)
    if change:
        self.app.push_screen(ChangeDetailScreen(change))
```

Patrón idéntico al de `EpicsView.on_data_table_row_selected` (líneas 100-105).
El separador `── archived ──` no tiene `key` → `get()` devuelve `None` → no hace nada.

### `tui/epics.py` — path fix

```python
# action_steering — línea 133
# Antes:
steering_path = Path.cwd() / "openspec" / "steering.md"
# Después:
steering_path = self.app._openspec_path / "steering.md"

# action_decisions_timeline — línea 137
# Antes:
archive_dir = Path.cwd() / "openspec" / "changes" / "archive"
# Después:
archive_dir = self.app._openspec_path / "changes" / "archive"
```

En ambos casos, eliminar el `import Path` si queda sin uso (verificar).

## Dependencias Técnicas

- Sin dependencias externas ni migraciones.
- `ChangeDetailScreen` ya importado en `epics.py` — solo necesita importarse en `spec_health.py` (import local dentro del método para evitar circular).
- `self.app._openspec_path` disponible en tiempo de acción (post-mount) — no hay riesgo de acceso anticipado.

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_document_viewer_jk_bindings` | `tests/tui/test_doc_viewer.py` | `j`/`k` están en BINDINGS de `DocumentViewerScreen` |
| `test_spec_evolution_jk_bindings` | `tests/tui/test_spec_evolution.py` | `j`/`k` están en BINDINGS de `SpecEvolutionScreen` |
| `test_decisions_timeline_jk_bindings` | `tests/tui/test_spec_evolution.py` | `j`/`k` están en BINDINGS de `DecisionsTimeline` |
| `test_spec_health_drill_down` | `tests/tui/test_spec_health.py` | Enter en fila → `push_screen(ChangeDetailScreen)` |
| `test_spec_health_separator_no_drill_down` | `tests/tui/test_spec_health.py` | Fila sin key → no push_screen |
| `test_app_changes_property` | `tests/tui/test_app.py` | `app.changes` retorna la lista de changes de `EpicsView` |

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `app.changes` delega a `EpicsView._changes` | Almacenar `_changes` en `SddTuiApp` | `SddTuiApp` no tiene estado propio de changes — vive en `EpicsView`; duplicar sería inconsistente |
| Import local de `ChangeDetailScreen` en `spec_health.py` | Import en módulo | Evita importación circular (spec_health ← change_detail ← spec_health no existe, pero por consistencia con el patrón de epics.py) |
| `self.app._openspec_path` (prefijo `_`) | Nueva propiedad pública `app.openspec_path` | Fuera de scope de este change; `_openspec_path` ya es accesible en Python y suficiente aquí |
