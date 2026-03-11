# Spec: TUI — TodosScreen

## Metadata
- **Dominio:** tui
- **Change:** todos-panel
- **Fecha:** 2026-03-11
- **Versión:** 0.1
- **Estado:** draft

## Contexto

`TodosScreen` es una pantalla de solo lectura accesible desde `EpicsView` (View 1)
mediante la tecla `T`. Muestra el contenido de `openspec/todos/*.md` agrupado por archivo,
con indicador de progreso por grupo y estilo diferenciado para ítems completados.

Sigue el mismo patrón que `ProgressDashboard` y `VelocityView`:
`Screen` + `ScrollableContainer` + `Static` + función pura `_build_content()`.

## Layout

```
┌─────────────────────────────────────────────────┐
│ sdd-tui — Todos                                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ── ideas [1/3] ──                               │
│  ✓ Ítem completado                    (dim)      │
│  · Ítem pendiente A                              │
│  · Ítem pendiente B                              │
│                                                  │
│  ── deuda-tecnica [0/2] ──                       │
│  · Refactorizar reader                           │
│  · Añadir tipos en todos los módulos             │
│                                                  │
├─────────────────────────────────────────────────┤
│ [esc] back  [j/k] scroll                        │
└─────────────────────────────────────────────────┘
```

## Requisitos (EARS)

- **REQ-TU-01** `[Event]` When the user presses `T` in EpicsView, the system SHALL push `TodosScreen` onto the screen stack.
- **REQ-TU-02** `[Event]` When the user presses `Escape` in TodosScreen, the system SHALL pop the screen and return to EpicsView.
- **REQ-TU-03** `[Ubiquitous]` TodosScreen SHALL display todos grouped by `TodoFile`, with a header showing `── {title} [{done}/{total}] ──`.
- **REQ-TU-04** `[Ubiquitous]` Completed items (`done=True`) SHALL be displayed with `dim` style and a `✓` prefix.
- **REQ-TU-05** `[Ubiquitous]` Pending items (`done=False`) SHALL be displayed with a `·` prefix and default style.
- **REQ-TU-06** `[Unwanted]` If `load_todos()` returns `[]` (no todos directory or empty), the system SHALL display a "No todos found" message.
- **REQ-TU-07** `[Ubiquitous]` TodosScreen SHALL support scroll via `j`/`k` bindings and arrow keys, delegating to the inner `ScrollableContainer`.
- **REQ-TU-08** `[Ubiquitous]` The screen title SHALL be "Todos".

## Escenarios de verificación

**REQ-TU-01** — Navegación a TodosScreen
**Dado** EpicsView con al menos un change visible
**Cuando** el usuario pulsa `T`
**Entonces** la pantalla activa es `TodosScreen`

**REQ-TU-03** — Agrupación con progreso
**Dado** un archivo `openspec/todos/ideas.md` con 1 ítem `[x]` y 2 `[ ]`
**Cuando** se renderiza `TodosScreen`
**Entonces** la cabecera muestra `── ideas [1/3] ──`

**REQ-TU-06** — Vacío
**Dado** que `openspec/todos/` no existe
**Cuando** se renderiza `TodosScreen`
**Entonces** se muestra `No todos found`

## Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin directorio `todos/` | `load_todos` retorna `[]` | Mensaje "No todos found" |
| Archivo con solo ítems completados | `done=True` para todos | Header `[N/N]`, todos dim |
| Archivo sin ítems | `items=[]` | Header `[0/0]`, sin filas adicionales |
| Múltiples archivos | N `TodoFile` | N grupos separados por línea en blanco |

## Implementación

Sigue exactamente el patrón de `ProgressDashboard`:

```python
class TodosScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
    ]

    def compose(self):
        yield Header()
        yield ScrollableContainer(Static("", id="content"))
        yield Footer()

    def on_mount(self):
        self.title = "Todos"
        todos = load_todos(self.app._openspec_path)
        content = _build_content(todos)
        self.query_one("#content", Static).update(content)

    def action_scroll_down(self):
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self):
        self.query_one(ScrollableContainer).scroll_up()
```

La función pura `_build_content(todos: list[TodoFile]) -> Text` construye el `rich.Text`
testeable independientemente de la TUI.

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| `ScrollableContainer + Static` (texto plano) | `DataTable` interactivo | Solo lectura; no hay drill-down; patrón más simple |
| `rich.Text` en `_build_content()` | Markdown | Control exacto sobre estilos dim/bold por ítem |
| Binding `T` en EpicsView | Otro binding | Semántico (Todos), está libre |
| Degradación a "No todos found" | No mostrar pantalla | Consistente con otras pantallas del sistema |
