# Design: Help Screen (Keybindings Reference)

## Metadata
- **Change:** view-help-screen
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

Dos cambios simples: un archivo nuevo (`tui/help.py`) con `HelpScreen` y una
línea en `tui/app.py` para el binding global `?`. El contenido del help se
define como constante `rich.Text` en el módulo — mismo patrón de contenido
estático ya usado en `DecisionsTimeline._populate()`. El binding `?` va en
`SddTuiApp.BINDINGS` con `priority=True` para garantizar captura desde cualquier
pantalla. El README se actualiza para reflejar el estado completo de keybindings.

## Arquitectura

```
SddTuiApp.BINDINGS
  "question_mark" (priority=True) → action_help
    → push_screen(HelpScreen())

HelpScreen(Screen)
  Header ("sdd-tui — keyboard reference")
  ScrollableContainer
    Static (HELP_CONTENT — rich.Text)
  Footer
  BINDINGS: j/k (scroll), escape (pop)
  action_scroll_down/up → ScrollableContainer (patrón ux-navigation)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `tui/help.py` | Screen | `HelpScreen` con contenido estático HELP_CONTENT |
| `tests/test_tui_help.py` | Test | `?` abre HelpScreen, `Esc` cierra, contenido completo |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `tui/app.py` | Añadir `BINDINGS` + `action_help` | Binding `?` global con `priority=True` |
| `README.md` | Actualizar sección Keybindings | Sincronizar con el estado real de la app |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal (< 10)

## Detalles de Implementación

### `tui/help.py` — HelpScreen

```python
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


HELP_CONTENT = _build_help_content()  # función privada que construye el Text


class HelpScreen(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static(HELP_CONTENT, id="help-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — keyboard reference"

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()
```

`_build_help_content()` construye un `rich.Text` con los grupos del layout
de la spec, usando `bold` para los títulos de sección y texto plano para
las entradas `key  description`.

### `tui/app.py` — binding global

```python
from textual.binding import Binding

class SddTuiApp(App):
    BINDINGS = [Binding("question_mark", "help", "Help", priority=True)]

    def action_help(self) -> None:
        from sdd_tui.tui.help import HelpScreen
        self.push_screen(HelpScreen())
```

`"question_mark"` es el nombre canónico de `?` en Textual (shift+/).
`priority=True` garantiza que `SddTuiApp` capture la tecla antes que cualquier
Screen o Widget hijo.

### `README.md` — sección Keybindings

Reemplazar la sección `## Keybindings` con tabla completa por vista, alineada
con el contenido de `HelpScreen`. Añadir bindings que faltaban: `H`, `X`, `s`,
`q` (requirements), `E`, `j/k` en viewers, `?` global, Enter en SpecHealth.

## Dependencias Técnicas

- Sin dependencias externas.
- Import local de `HelpScreen` en `action_help` — evita circular (help.py no importa app.py).

## Patrones Aplicados

- **Contenido estático como función `_build_*`**: `DecisionsTimeline._populate()` hace lo mismo con `rich.Text`
- **`action_scroll_down/up` en Screen**: patrón establecido en `ux-navigation` para `DocumentViewerScreen`, `SpecEvolutionScreen`, `DecisionsTimeline`
- **`priority=True` en binding de App**: mismo patrón que `Space` en `ChangeDetailScreen` (captura antes que widgets hijos)
- **Import local en action**: mismo patrón que `action_steering` / `action_decisions_timeline` en `EpicsView`

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_help_screen_opens_on_question_mark` | TUI async | `?` desde View 1 → `isinstance(app.screen, HelpScreen)` |
| `test_help_screen_esc_closes` | TUI async | `Esc` en HelpScreen → vuelve a View 1 |
| `test_help_screen_jk_bindings` | Unit | `j`/`k` en `HelpScreen.BINDINGS` |
| `test_help_content_has_all_sections` | Unit | `HELP_CONTENT` contiene las 6 secciones esperadas |

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `"question_mark"` como nombre de tecla | `"?"` literal | Nombre canónico Textual para shift+/; más explícito |
| `_build_help_content()` función privada | Constante literal inline | Más legible que un bloque de `text.append()` a nivel de módulo |
| Import local en `action_help` | Import en cabecera del módulo | Evita posibles circulares; patrón consistente con epics.py |
