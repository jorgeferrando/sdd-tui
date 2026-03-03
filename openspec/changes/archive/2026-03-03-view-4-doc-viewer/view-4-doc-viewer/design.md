# Design: View 4 — Document viewer

## Metadata
- **Change:** view-4-doc-viewer
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-03
- **Estado:** approved

## Resumen Técnico

Se añaden dos nuevas `Screen` de Textual (`DocumentViewerScreen` y
`SpecSelectorScreen`) en un nuevo archivo `doc_viewer.py`, siguiendo el mismo
patrón `push_screen` / `pop_screen` ya establecido en `change_detail.py`.

`ChangeDetailScreen` recibe 4 bindings nuevos (`p`, `d`, `s`, `t`) que invocan
actions que determinan qué pantalla abrir: directo a `DocumentViewerScreen`
para documentos únicos, o `SpecSelectorScreen` cuando hay múltiples dominios de
spec.

El contenido se renderiza con `rich.Markdown` (ya disponible como dependencia
de Textual, sin imports nuevos en `pyproject.toml`).

## Arquitectura

```
ChangeDetailScreen (View 2)
  │
  ├── [p] / [d] / [t] ──────────────► DocumentViewerScreen
  │                                        rich.Markdown(path.read_text())
  │                                        Esc → pop_screen
  │
  └── [s] ──┬── 1 dominio ──────────► DocumentViewerScreen (directo)
             │
             └── N dominios ────────► SpecSelectorScreen
                                          ListView(dominios)
                                          Enter → DocumentViewerScreen
                                          Esc  → pop_screen (vuelve a View 2)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/tui/doc_viewer.py` | Module TUI | `DocumentViewerScreen` + `SpecSelectorScreen` |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | Añadir bindings `p/d/s/t` + 2 action methods + import | Conectar View 2 con las nuevas pantallas |

## Scope

- **Total archivos:** 2
- **Resultado:** Ideal

## Dependencias Técnicas

- Sin dependencias nuevas — `rich.Markdown` ya disponible via Textual
- Sin cambios en core ni en app.py

## Detalle de Implementación

### `doc_viewer.py` — `DocumentViewerScreen`

```python
class DocumentViewerScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, path: Path, title: str) -> None:
        super().__init__()
        self._path = path
        self._doc_title = title

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="doc-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = self._doc_title
        if self._path.exists():
            content = Markdown(self._path.read_text())
        else:
            content = f"[dim]{self._path.name} not found[/dim]"
        self.query_one("#doc-content", Static).update(content)
```

### `doc_viewer.py` — `SpecSelectorScreen`

```python
class SpecSelectorScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change
        self._domains: list[str] = self._find_domains()

    def _find_domains(self) -> list[str]:
        specs_dir = self._change.path / "specs"
        if not specs_dir.exists():
            return []
        return sorted(
            d.name for d in specs_dir.iterdir()
            if d.is_dir() and (d / "spec.md").exists()
        )

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(
            *[ListItem(Label(domain), id=f"domain-{domain}") for domain in self._domains]
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name} / specs"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        if not item_id.startswith("domain-"):
            return
        domain = item_id[len("domain-"):]
        path = self._change.path / "specs" / domain / "spec.md"
        title = f"sdd-tui — {self._change.name} / spec:{domain}"
        self.app.push_screen(DocumentViewerScreen(path, title))
```

### `change_detail.py` — Additions

```python
# Imports a añadir:
from sdd_tui.tui.doc_viewer import DocumentViewerScreen, SpecSelectorScreen

# BINDINGS ampliados:
BINDINGS = [
    Binding("escape", "app.pop_screen", "Back"),
    Binding("r", "refresh_view", "Refresh"),
    Binding("p", "view_proposal", "Proposal"),
    Binding("d", "view_design", "Design"),
    Binding("s", "view_spec", "Spec"),
    Binding("t", "view_tasks", "Tasks"),
]

# Actions:
def action_view_proposal(self) -> None:
    self._open_doc("proposal.md", "proposal")

def action_view_design(self) -> None:
    self._open_doc("design.md", "design")

def action_view_tasks(self) -> None:
    self._open_doc("tasks.md", "tasks")

def action_view_spec(self) -> None:
    specs_dir = self._change.path / "specs"
    domains = sorted(
        d.name for d in specs_dir.iterdir()
        if d.is_dir() and (d / "spec.md").exists()
    ) if specs_dir.exists() else []
    if not domains:
        self.notify("No specs found")
    elif len(domains) == 1:
        path = specs_dir / domains[0] / "spec.md"
        title = f"sdd-tui — {self._change.name} / spec:{domains[0]}"
        self.app.push_screen(DocumentViewerScreen(path, title))
    else:
        self.app.push_screen(SpecSelectorScreen(self._change))

def _open_doc(self, filename: str, label: str) -> None:
    path = self._change.path / filename
    title = f"sdd-tui — {self._change.name} / {label}"
    self.app.push_screen(DocumentViewerScreen(path, title))
```

## Patrones Aplicados

- **`push_screen` / `pop_screen`**: mismo patrón que `EpicsView → ChangeDetailScreen`
- **`Static.update()` con renderable**: mismo patrón que `DiffPanel.show_diff()` en `change_detail.py`
- **Actions separadas por doc**: más explícitas que actions parametrizadas; evita complejidad de Textual action params

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Actions separadas (`action_view_proposal`, etc.) | Action parametrizada `action_view_doc('proposal')` | Más explícito; Textual action params tienen edge cases |
| Helper `_open_doc` | Código repetido en cada action | DRY para los 3 documentos únicos |
| `id=f"domain-{domain}"` en ListItem | Indexar por posición | Más robusto que asumir orden en el evento |
| `self.notify()` para "no specs" | DocumentViewerScreen con mensaje | Menos overhead para caso excepcional |

## Tests Planificados

Sin tests automatizados nuevos — los tests de TUI requieren `Pilot` async y el
proyecto no tiene cobertura de TUI todavía. Cobertura via smoke test en QG.

## Notas de Implementación

- `rich.Markdown` import: `from rich.markdown import Markdown`
- `ListView` + `ListItem` + `Label`: `from textual.widgets import ListView, ListItem, Label`
- El `_doc_title` se guarda como atributo separado porque `self.title` no existe hasta `on_mount`
