# Design: View 1 — Search & Filter

## Metadata
- **Change:** view-search-filter
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

El cambio añade modo búsqueda `/` a `EpicsView`. La implementación usa el widget
nativo `Input` de Textual, oculto por defecto y mostrado al activar el modo búsqueda.
El estado de filtrado vive en `EpicsView` como `_search_query: str`, y `_populate()`
lo aplica automáticamente en cada recarga, lo que hace que el filtro persista
transparentemente con el toggle de archivados.

El highlight del match usa `rich.Text` con `style="bold cyan"` en el substring coincidente.
`DataTable` acepta `rich.Text` como valor de celda de forma nativa.

## Arquitectura

```
EpicsView
  ├── state: _search_mode: bool, _search_query: str
  ├── _populate()          ← lee _search_query, filtra y hace highlight
  ├── _filter_changes()    ← substring case-insensitive
  ├── _highlight_match()   ← rich.Text con bold cyan en el match
  ├── action_search()      ← activa modo, muestra Input, lo enfoca
  ├── action_cancel_search() ← limpia query, oculta Input, restore DataTable
  ├── on_input_changed()   ← filtrado en tiempo real
  ├── on_input_submitted() ← confirma filtro, oculta Input, foco DataTable
  └── action_refresh()     ← limpia query antes de recargar (REQ-09)
```

## Flujo de interacción

```
Usuario pulsa /
  → action_search()
    → _search_mode = True
    → Input.display = True
    → Input.focus()

Usuario escribe "view"
  → on_input_changed(query="view")
    → _search_query = "view"
    → _populate()  [filtra + highlight]

Usuario pulsa Enter
  → on_input_submitted(query="view")
    → _search_mode = False
    → Input.display = False
    → app.sub_title = 'filtered: "view"'
    → DataTable.focus() via call_after_refresh

Usuario pulsa Esc (modo búsqueda activo)
  → on_key(escape) interceptado en EpicsView
    → action_cancel_search()
      → _search_query = ""
      → _search_mode = False
      → Input.display = False
      → app.sub_title = ""
      → _populate()  [lista completa]
      → DataTable.focus() via call_after_refresh

Usuario pulsa a (toggle archivados, con filtro activo)
  → action_toggle_archived()  [sin cambios en _search_query]
    → app.refresh_changes(show_archived)
      → epics.update(new_changes)
        → _populate()  [usa _search_query existente → filtro persiste]

Usuario pulsa r (refresh, con filtro activo)
  → action_refresh()
    → _search_query = ""        ← limpia filtro
    → _search_mode = False
    → app.sub_title = ""
    → app.refresh_changes(...)  → _populate()  [lista completa]
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir modo búsqueda completo | Único fichero de la feature |
| `tests/test_tui_epics.py` | Añadir tests para búsqueda | Cobertura de REQs nuevos |

## Archivos a Crear

Ninguno.

## Scope

- **Total archivos:** 2
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- `rich.Text` — ya disponible vía Textual
- `Input` widget de Textual — ya disponible, no requiere imports nuevos de terceros
- Sin breaking changes — `/` no tenía binding previo en EpicsView

## Patrones Aplicados

- **Input oculto con `display = False/True`**: mismo patrón que otros widgets condicionales en Textual; evita recompose.
- **`_populate()` lee estado interno**: mismo patrón que `_show_archived`; el filtro persiste automáticamente en `update()`.
- **`call_after_refresh` para focus**: mismo patrón que ChangeDetailScreen y SpecHealthScreen.
- **`on_key` para Esc**: más robusto que binding de `escape` en EpicsView, que puede interferir con la pila de pantallas.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `Input` nativo de Textual oculto/mostrado | Label custom + captura de teclas manual | Gestión de cursor, backspace, composición de texto — todo gratis con `Input` |
| `_search_query` en estado de `EpicsView` | Parámetro explícito a `_populate()` | `update()` ya existe y llama `_populate()` sin args — el estado interno hace el filtro transparente |
| `on_key` para Esc | `Binding("escape", ...)` en `EpicsView` | `Binding` de `escape` en widget puede interferir con `pop_screen` de Textual; `on_key` con guard es más seguro |
| `app.sub_title` para indicar filtro activo | Modificar `app.title` | `sub_title` es el campo semántico para estado transitorio; `title` es el nombre fijo de la app |
| `rich.Text` con `bold cyan` para match | Estilo `bold` solo / `reverse` | Contraste visible en terminales oscuras y claras; cyan no choca con ningún estilo existente en la TUI |
| Highlight solo en columna `change` | Highlight en todas las columnas | Las otras columnas son símbolos de fase (`✓`, `·`) — no hay texto a resaltar |

## Implementación detallada — `epics.py`

### Nuevos imports
```python
from rich.text import Text
from textual.events import Key
from textual.widgets import DataTable, Footer, Header, Input
```

### Nuevos atributos
```python
_search_mode: bool = False
_search_query: str = ""
```

### Nuevo binding
```python
Binding("/", "search", "Search"),
```

### CSS adicional
```css
#search-input {
    display: none;
}
```

### Compose (añadir `Input`)
```python
yield Header(show_clock=False)
yield DataTable(cursor_type="row")
yield Input(placeholder="/ search...", id="search-input")
yield Footer()
```

### `_populate()` modificado
```python
def _populate(self) -> None:
    table = self.query_one(DataTable)
    table.clear(columns=True)
    table.add_columns("change", *PHASES)
    self._change_map = {}

    active = [c for c in self._changes if not c.archived]
    archived = [c for c in self._changes if c.archived]

    if self._search_query:
        active = self._filter_changes(active, self._search_query)
        archived = self._filter_changes(archived, self._search_query)

    if not active and not archived and self._search_query:
        table.add_row(f'No matches for "{self._search_query}"', "", "", "", "", "", "")
        return

    for change in active:
        self._add_change_row(table, change)

    if archived:
        table.add_row("── archived ──", "", "", "", "", "", "")
        for change in archived:
            self._add_change_row(table, change)
```

### `_add_change_row()` modificado
```python
def _add_change_row(self, table: DataTable, change: Change) -> None:
    pipeline = change.pipeline
    name_cell: str | Text = (
        self._highlight_match(change.name, self._search_query)
        if self._search_query
        else change.name
    )
    row = (
        name_cell,
        _phase_symbol(pipeline.propose),
        _phase_symbol(pipeline.spec),
        _phase_symbol(pipeline.design),
        _phase_symbol(pipeline.tasks),
        _apply_display(pipeline.apply, change.tasks),
        _phase_symbol(pipeline.verify),
    )
    table.add_row(*row, key=change.name)
    self._change_map[change.name] = change
```

### Nuevos helpers
```python
def _filter_changes(self, changes: list[Change], query: str) -> list[Change]:
    q = query.lower()
    return [c for c in changes if q in c.name.lower()]

def _highlight_match(self, name: str, query: str) -> Text:
    text = Text()
    lower_name = name.lower()
    lower_query = query.lower()
    idx = lower_name.find(lower_query)
    if idx == -1:
        return Text(name)
    text.append(name[:idx])
    text.append(name[idx : idx + len(query)], style="bold cyan")
    text.append(name[idx + len(query) :])
    return text
```

### Nuevas actions
```python
def action_search(self) -> None:
    self._search_mode = True
    search_input = self.query_one("#search-input", Input)
    search_input.display = True
    search_input.focus()

def action_cancel_search(self) -> None:
    self._search_query = ""
    self._search_mode = False
    self.app.sub_title = ""
    search_input = self.query_one("#search-input", Input)
    search_input.clear()
    search_input.display = False
    self._populate()
    self.call_after_refresh(lambda: self.query_one(DataTable).focus())
```

### Handlers de Input
```python
def on_input_changed(self, event: Input.Changed) -> None:
    if not self._search_mode:
        return
    self._search_query = event.value
    self._populate()

def on_input_submitted(self, event: Input.Submitted) -> None:
    query = event.value
    self._search_query = query
    self._search_mode = False
    search_input = self.query_one("#search-input", Input)
    search_input.display = False
    if query:
        self.app.sub_title = f'filtered: "{query}"'
    else:
        self.app.sub_title = ""
    self.call_after_refresh(lambda: self.query_one(DataTable).focus())
```

### Interceptar Esc
```python
def on_key(self, event: Key) -> None:
    if self._search_mode and event.key == "escape":
        event.stop()
        self.action_cancel_search()
```

### `action_refresh()` modificado
```python
def action_refresh(self) -> None:
    self._search_query = ""
    self._search_mode = False
    self.app.sub_title = ""
    search_input = self.query_one("#search-input", Input)
    search_input.clear()
    search_input.display = False
    changes = self.app.refresh_changes(self._show_archived)
    n_active = sum(1 for c in changes if not c.archived)
    n_archived = sum(1 for c in changes if c.archived)
    self.notify(f"{n_active} changes loaded ({n_archived} archived)")
```

## Tests Planificados

| Test | Tipo | REQ | Qué verifica |
|------|------|-----|-------------|
| `test_search_activates_input` | TUI | REQ-01 | `/` muestra el Input |
| `test_search_filters_in_realtime` | TUI | REQ-03 | Escribir filtra el DataTable |
| `test_search_escape_cancels` | TUI | REQ-04 | Esc restaura lista completa |
| `test_search_enter_confirms` | TUI | REQ-05 | Enter mantiene filtro, foco a DataTable |
| `test_search_no_results` | TUI | REQ-06 | 0 resultados → fila "No matches" |
| `test_search_persists_on_toggle_archived` | TUI | REQ-10 | Toggle `a` mantiene el filtro |
| `test_refresh_clears_filter` | TUI | REQ-09 | `r` limpia el filtro |
| `test_highlight_match` | Unit | REQ-13 | `_highlight_match` retorna Text con bold cyan |
| `test_filter_changes` | Unit | REQ-03 | `_filter_changes` case-insensitive |

## Notas de Implementación

- `Input` debe tener `id="search-input"` para el `query_one` con tipado correcto.
- El `on_key` con `event.stop()` evita que Esc se propague a la pila de pantallas de Textual.
- `_populate()` siempre lee `self._search_query` — no hay riesgo de desincronización con `update()`.
- `rich.Text` importado desde `rich.text` (no desde Textual) — es la misma dependencia transitiva.
- En los tests de `_highlight_match` y `_filter_changes`, se puede instanciar `EpicsView([])` directamente sin correr la app Textual completa (son helpers puros).
