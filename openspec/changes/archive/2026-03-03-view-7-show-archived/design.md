# Design: View 7 — Mostrar/ocultar archivados

## Metadata
- **Change:** view-7-show-archived
- **Fecha:** 2026-03-03
- **Estado:** approved

## Resumen Técnico

Se añade `archived: bool = False` a `Change`. `OpenspecReader.load()` recibe
`include_archived: bool = False`; cuando es True, también carga los subdirectorios
de `changes/archive/` marcándolos con `archived=True`. `SddTuiApp` pasa el flag
a través de `refresh_changes` y `_load_changes`. `EpicsView` guarda el estado
del toggle en `_show_archived` y usa `row_key` para la selección (en lugar de
índice) para poder intercalar la fila separadora sin romper la navegación.

## Arquitectura

```
[a] → EpicsView.action_toggle_archived()
          │
          ├── self._show_archived = not self._show_archived
          └── self.app.refresh_changes(self._show_archived)
                    │
                    └── _load_changes(include_archived)
                              │
                              └── reader.load(include_archived)
                                        ├── changes/*/   → archived=False
                                        └── changes/archive/*/ → archived=True

EpicsView._populate()
  ├── activos  → rows con key=change.name
  ├── si archived: separator row (sin key)
  └── archivados → rows con key=change.name

on_data_table_row_selected → event.row_key.value → _change_map[key]
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/models.py` | Añadir `archived: bool = False` a `Change` | Distinguir activos de archivados sin lógica de path |
| `src/sdd_tui/core/reader.py` | `load(include_archived=False)` carga también `archive/*/` | Fuente de datos para los archivados |
| `src/sdd_tui/tui/app.py` | `refresh_changes(include_archived=False)` + `_load_changes(include_archived=False)` | Propagar el flag desde EpicsView hasta el reader |
| `src/sdd_tui/tui/epics.py` | `_show_archived`, binding `a`, `_change_map`, row_key, separator | UI del toggle y selección robusta |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal

## Detalle de Implementación

### `models.py`

```python
@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline = field(default_factory=Pipeline)
    tasks: list[Task] = field(default_factory=list)
    archived: bool = False
```

### `reader.py`

```python
def load(self, openspec_path: Path, include_archived: bool = False) -> list[Change]:
    changes_path = openspec_path / "changes"
    if not openspec_path.exists() or not changes_path.exists():
        raise OpenspecNotFoundError(f"openspec/ not found at {openspec_path}")

    entries = sorted(
        entry for entry in changes_path.iterdir()
        if entry.is_dir() and entry.name != "archive"
    )
    changes = [Change(name=entry.name, path=entry) for entry in entries]

    if include_archived:
        archive_path = changes_path / "archive"
        if archive_path.exists():
            archived_entries = sorted(
                entry for entry in archive_path.iterdir()
                if entry.is_dir()
            )
            changes += [
                Change(name=entry.name, path=entry, archived=True)
                for entry in archived_entries
            ]

    return changes
```

### `app.py`

```python
def refresh_changes(self, include_archived: bool = False) -> list[Change]:
    changes = self._load_changes(include_archived)
    self.query_one(EpicsView).update(changes)
    return changes

def _load_changes(self, include_archived: bool = False) -> list[Change]:
    changes = self._reader.load(self._openspec_path, include_archived)
    for change in changes:
        change.pipeline = self._inferer.infer(change.path, self._git)
        change.tasks = self._load_tasks(change)
    return changes
```

### `epics.py`

```python
class EpicsView(Widget):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("a", "toggle_archived", "Archived"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, changes: list[Change]) -> None:
        super().__init__()
        self._changes = changes
        self._show_archived = False
        self._change_map: dict[str, Change] = {}

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("change", *PHASES)
        self._change_map = {}

        active = [c for c in self._changes if not c.archived]
        archived = [c for c in self._changes if c.archived]

        for change in active:
            self._add_change_row(table, change)

        if archived:
            table.add_row("── archived ──", "", "", "", "", "", "")
            for change in archived:
                self._add_change_row(table, change)

    def _add_change_row(self, table: DataTable, change: Change) -> None:
        pipeline = change.pipeline
        row = (
            change.name,
            _phase_symbol(pipeline.propose),
            _phase_symbol(pipeline.spec),
            _phase_symbol(pipeline.design),
            _phase_symbol(pipeline.tasks),
            _apply_display(pipeline.apply, change.tasks),
            _phase_symbol(pipeline.verify),
        )
        table.add_row(*row, key=change.name)
        self._change_map[change.name] = change

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        change = self._change_map.get(event.row_key.value)
        if change:
            self.app.push_screen(ChangeDetailScreen(change))

    def action_toggle_archived(self) -> None:
        self._show_archived = not self._show_archived
        self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]

    def action_refresh(self) -> None:
        self.app.refresh_changes(self._show_archived)  # type: ignore[attr-defined]
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `archived: bool` en `Change` | Path-based detection en EpicsView | Separa la responsabilidad; el modelo conoce su origen |
| `row_key` para selección | Índice de fila | El separador rompe la correspondencia índice→change |
| Separator sin key | Fila con key especial | Más simple; `_change_map.get()` devuelve None para rows sin key |
| Toggle en EpicsView | Toggle en App | El estado es local a la vista; App no necesita conocerlo |
| `_show_archived` pasado a `refresh_changes` | `action_refresh` llama a `app.refresh_changes(self._show_archived)` | Consistencia: `r` respeta el estado del toggle |

## Tests Planificados

- Actualizar tests de `OpenspecReader` si los hay para cubrir `include_archived=True`
- Sin tests de UI (requiere Pilot async)
