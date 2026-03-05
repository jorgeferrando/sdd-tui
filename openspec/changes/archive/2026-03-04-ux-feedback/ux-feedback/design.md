# Design: UX Feedback — Estado Visual y Notificaciones

## Metadata
- **Change:** ux-feedback
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** draft

## Resumen Técnico

Cuatro cambios quirúrgicos sobre tres archivos TUI. Ninguno requiere cambios
en core. El más interesante es el label dinámico del binding `a`: Textual
soporta labels dinámicos asignando `self.BINDINGS` como atributo de instancia
(Python resuelve `self.BINDINGS` antes que `EpicsView.BINDINGS`) y llamando
`refresh_bindings()` para invalidar el caché del footer.

## Arquitectura

```
EpicsView.action_toggle_archived()
  → self.BINDINGS = [..., Binding("a", ..., "Hide/Show archived"), ...]
  → self.refresh_bindings()          ← footer re-lee la instancia
  → app.refresh_changes()

EpicsView.action_refresh()
  → app.refresh_changes() → list[Change]
  → self.notify(f"{n_active} changes loaded ({n_archived} archived)")

ChangeDetailScreen._open_doc(filename, label)
  → if path.exists(): self.notify(f"Opening {label}")
  → push_screen(DocumentViewerScreen(...))

ChangeDetailScreen.action_view_spec()   [single domain path]
  → if path.exists(): self.notify("Opening spec")
  → push_screen(DocumentViewerScreen(...))

DocumentViewerScreen.on_mount()
  → if not path.exists():
      self.app.notify(f"{name} not found", severity="warning")   ← nuevo
      content = "[dim]{name} not found[/dim]"                    ← ya existía

SpecSelectorScreen.BINDINGS
  → añadir Binding("q", "app.pop_screen", "Close")
```

## Archivos a Modificar

| Archivo | Cambio | REQs |
|---------|--------|------|
| `src/sdd_tui/tui/epics.py` | Label dinámico `a` + notify refresh | REQ-01..05 |
| `src/sdd_tui/tui/change_detail.py` | Notify al abrir doc | REQ-06 |
| `src/sdd_tui/tui/doc_viewer.py` | Warning not found + `q` en selector | REQ-07..09 |

## Archivos a Crear

Ninguno en el código fuente.

## Archivos de Test a Modificar

| Archivo | Cambio |
|---------|--------|
| `tests/test_tui_epics.py` | Test label dinámico + test notify refresh |
| `tests/test_tui_change_detail.py` | Test notify al abrir doc |
| `tests/test_tui_doc_viewer.py` | Test warning not found + test `q` en selector |

## Scope

- **Total archivos:** 6 (3 fuente + 3 test)
- **Resultado:** Ideal (< 10)

## Implementación por archivo

### `tui/epics.py`

**Fix 1 — Label dinámico:**

```python
# Eliminar "Archived" del BINDINGS de clase (o cambiar a "Show archived"):
BINDINGS = [
    Binding("r", "refresh", "Refresh"),
    Binding("a", "toggle_archived", "Show archived"),  # label inicial
    ...
]

def action_toggle_archived(self) -> None:
    self._show_archived = not self._show_archived
    label = "Hide archived" if self._show_archived else "Show archived"
    self.BINDINGS = [  # instancia sombrea la clase
        Binding("r", "refresh", "Refresh"),
        Binding("a", "toggle_archived", label),
        Binding("s", "steering", "Steering"),
        Binding("h", "health", "Health"),
        Binding("x", "decisions_timeline", "Decisions"),
        Binding("q", "quit", "Quit"),
    ]
    self.refresh_bindings()
    self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]
```

**Fix 2 — Notify refresh:**

```python
def action_refresh(self) -> None:
    changes = self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]
    n_active = sum(1 for c in changes if not c.archived)
    n_archived = sum(1 for c in changes if c.archived)
    self.notify(f"{n_active} changes loaded ({n_archived} archived)")
```

### `tui/change_detail.py`

**Fix 3 — Notify al abrir doc:**

```python
def _open_doc(self, filename: str, label: str) -> None:
    path = self._change.path / filename
    title = f"sdd-tui — {self._change.name} / {label}"
    if path.exists():
        self.notify(f"Opening {label}")
    self.app.push_screen(DocumentViewerScreen(path, title))
```

Para `action_view_spec` (single domain path):

```python
elif len(domains) == 1:
    path = specs_dir / domains[0] / "spec.md"
    title = f"sdd-tui — {self._change.name} / spec:{domains[0]}"
    if path.exists():
        self.notify("Opening spec")
    self.app.push_screen(DocumentViewerScreen(path, title))
```

### `tui/doc_viewer.py`

**Fix 4 — Warning not found en DocumentViewerScreen:**

```python
def on_mount(self) -> None:
    self.title = self._doc_title
    if self._path.exists():
        content: Markdown | str = Markdown(self._path.read_text())
    else:
        self.app.notify(f"{self._path.name} not found", severity="warning")
        content = f"[dim]{self._path.name} not found[/dim]"
    self.query_one("#doc-content", Static).update(content)
```

**Fix 5 — `q` en SpecSelectorScreen:**

```python
class SpecSelectorScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Close"),
    ]
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `self.BINDINGS` en instancia + `refresh_bindings()` | Método `get_binding_label()` custom | Patrón Textual documentado; mínima superficie de cambio |
| Notify solo en `_open_doc` (no en DocumentViewerScreen.on_mount para el caso "existe") | Notify en on_mount siempre | Evita doble notify cuando archivo no existe (abre + not found) |
| `q` en SpecSelectorScreen = `app.pop_screen` (igual que Esc) | Action custom | Ambos bindings hacen lo mismo — sin lógica extra |
| No notify en `action_toggle_archived` (solo refresh_bindings) | Notify + label | El cambio de label ya comunica el nuevo estado; notify sería redundante |
| Notify de refresh incluye conteo archivados aunque `_show_archived=False` | Omitir count si archivados ocultos | El usuario sabe cuántos archivados hay sin necesidad de togglear |

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_toggle_archived_label_hide` | test_tui_epics.py | Tras toggle ON, BINDINGS instancia tiene "Hide archived" |
| `test_toggle_archived_label_show` | test_tui_epics.py | Tras dos toggles, BINDINGS instancia tiene "Show archived" |
| `test_action_refresh_notify` | test_tui_epics.py | `action_refresh` emite notify con conteo correcto |
| `test_open_doc_existing_notifies` | test_tui_change_detail.py | `_open_doc` notifica "Opening proposal" si archivo existe |
| `test_open_doc_missing_no_notify` | test_tui_change_detail.py | `_open_doc` no notifica si archivo no existe |
| `test_doc_viewer_not_found_warning` | test_tui_doc_viewer.py | `on_mount` llama `notify` con `severity="warning"` si path no existe |
| `test_spec_selector_q_binding` | test_tui_doc_viewer.py | `SpecSelectorScreen.BINDINGS` contiene binding `q` con action `app.pop_screen` |

## Notas de Implementación

- `refresh_bindings()` en Textual invalida el caché del Footer y fuerza re-lectura
  de bindings. Al asignar `self.BINDINGS` (instancia), Python encuentra el
  atributo de instancia antes que el de clase — sin subclasificación adicional.
- El notify de refresh usa `self.notify()` (método del Widget), no `self.app.notify()`.
  Ambos funcionan pero `self.notify()` es más correcto cuando el origen es el widget.
- `ChangeDetailScreen._open_doc` es el punto central para p/d/t/q — un solo
  cambio cubre todos esos bindings. `action_view_spec` tiene lógica propia y
  requiere su propio `notify`.
