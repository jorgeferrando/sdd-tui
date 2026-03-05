# Spec: TUI — Help Screen (Keybindings Reference)

## Metadata
- **Dominio:** tui
- **Change:** view-help-screen
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved


## Contexto

sdd-tui tiene ~20 keybindings distribuidos en 6 pantallas. El footer de Textual
muestra solo el subset de la vista activa. Los bindings de pantallas secundarias
(H, X, E, j/k) son invisibles hasta llegar a ellas. La convención estándar en
herramientas TUI (lazygit, k9s, ranger) es `?` para mostrar una referencia
completa de keybindings agrupados por contexto.

## Comportamiento Actual

No existe pantalla de ayuda. El usuario debe recordar los bindings de memoria
o leer el código/README (desactualizado).

## Requisitos (EARS)

- **REQ-01** `[Event]` When el usuario pulsa `?` en cualquier pantalla, la app SHALL hacer `push_screen(HelpScreen)`.
- **REQ-02** `[Ubiquitous]` The binding `?` SHALL estar disponible en todas las pantallas de la aplicación.
- **REQ-03** `[Event]` When el usuario pulsa `Esc` en `HelpScreen`, la app SHALL hacer `pop_screen` volviendo a la pantalla anterior con su estado intacto.
- **REQ-04** `[Ubiquitous]` The `HelpScreen` SHALL mostrar todos los keybindings de la aplicación agrupados por contexto de pantalla.
- **REQ-05** `[Ubiquitous]` The contenido de `HelpScreen` SHALL incluir los grupos: View 1, View 2, View 8 (Spec Health), View 9 (Spec Evolution), Viewers (DocumentViewerScreen / SpecSelectorScreen), Global.
- **REQ-06** `[State]` While el contenido de `HelpScreen` supera la altura de la pantalla, the usuario SHALL poder hacer scroll con `j`/`k` o flechas.

### Escenarios de verificación

**REQ-01/02** — `?` global
**Dado** View 1 (EpicsView) con el foco activo
**Cuando** el usuario pulsa `?`
**Entonces** se abre `HelpScreen`; al pulsar `Esc` se vuelve a View 1

**REQ-01/02** — `?` desde pantalla anidada
**Dado** `HelpScreen` ya abierto (vía `push_screen`)
**Cuando** el usuario vuelve a View 2 y pulsa `?`
**Entonces** se abre `HelpScreen` de nuevo (stack: View1 → View2 → HelpScreen)

**REQ-04/05** — Contenido completo
**Dado** `HelpScreen` abierto
**Cuando** el usuario lo revisa
**Entonces** ve los bindings de las 6 secciones con descripción legible

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│ sdd-tui — keyboard reference                                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  VIEW 1 — Changes                                             │
│  Enter    Open change detail                                  │
│  a        Toggle archived changes                             │
│  r        Refresh                                             │
│  s        Open steering.md                                    │
│  H        Spec health dashboard                               │
│  X        Decisions timeline                                  │
│  q        Quit                                                │
│                                                               │
│  VIEW 2 — Change detail                                       │
│  p        Open proposal.md                                    │
│  d        Open design.md                                      │
│  s        Open spec(s)                                        │
│  t        Open tasks.md                                       │
│  q        Open requirements.md                                │
│  Space    Copy next SDD command                               │
│  E        Spec evolution viewer                               │
│  r        Refresh in place                                    │
│  Esc      Back to changes                                     │
│                                                               │
│  VIEW 8 — Spec Health                                         │
│  Enter    Open change detail                                  │
│  Esc      Back to changes                                     │
│                                                               │
│  VIEW 9 — Spec Evolution                                      │
│  D        Toggle delta / canonical                            │
│  j / k    Scroll down / up                                    │
│  Esc      Back                                                │
│                                                               │
│  VIEWERS — Document / Spec Selector                           │
│  j / k    Scroll down / up                                    │
│  q / Esc  Close                                               │
│                                                               │
│  GLOBAL                                                       │
│  ?        This help screen                                    │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│ [j] down   [k] up   [Esc] close                              │
└──────────────────────────────────────────────────────────────┘
```

## Contratos

### `HelpScreen`

- **Clase:** `HelpScreen(Screen)`
- **Archivo:** `tui/help.py`
- **BINDINGS:** `j` → `scroll_down`, `k` → `scroll_up`, `escape` → `app.pop_screen`
- **`action_scroll_down`/`action_scroll_up`:** delegan a `ScrollableContainer` (patrón establecido en `ux-navigation`)
- **Contenido:** constante `HELP_TEXT` definida en el módulo como `Text` de Rich con grupos separados por línea en blanco
- **Título:** `"sdd-tui — keyboard reference"`

### Binding global `?` en `SddTuiApp`

```python
BINDINGS = [Binding("question_mark", "push_screen('help')", "Help", priority=True)]
```

O equivalente vía `action_help` + `push_screen(HelpScreen())`.

- **`priority=True`:** capturado antes que cualquier widget/screen hijo

### README

El README se actualiza en el mismo change con la tabla de keybindings extraída de `HelpScreen`. Mantenimiento manual — sin sincronización automática.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Contenido estático (`HELP_TEXT` constante) | Generado dinámicamente desde BINDINGS de Textual | La introspección no garantiza agrupación semántica; control total del texto |
| `push_screen` (pantalla dedicada) | Panel overlay / sidebar | Patrón estándar TUI; espacio completo; consistente con el resto de la app |
| `priority=True` en binding `?` | Sin priority | Garantiza captura desde cualquier pantalla, incluidas las que consumen teclas |
| Incluir viewers (DocumentViewerScreen, SpecSelectorScreen) | Omitirlos | Más completo; el usuario puede descubrir `j/k` en esas pantallas |
| Actualizar README en el mismo change | README independiente | Los bindings del README deben reflejar el estado actual; mejor sincronizarlos |

## Abierto / Pendiente

Ninguno.
