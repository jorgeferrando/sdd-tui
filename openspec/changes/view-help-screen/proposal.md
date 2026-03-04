# Proposal: Help Screen — Keybindings Reference

## Metadata
- **Change:** view-help-screen
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

sdd-tui tiene ~20 keybindings distribuidos en 5 pantallas. El footer de
Textual solo muestra un subset de los bindings de la vista activa, y solo
los que tienen `show=True`. Los bindings de pantallas secundarias (H, X, E)
no son visibles hasta que el usuario ya está en la pantalla que los define.

El resultado: un usuario nuevo (o un usuario volviendo tras días sin usar
la herramienta) no puede descubrir los bindings disponibles sin leer el
código o el README. El README además está desactualizado.

La convención estándar en herramientas TUI es `?` para mostrar un panel
de ayuda con todos los bindings agrupados por contexto. lazygit, k9s,
ranger, tig — todos lo implementan de esta forma.

## Solución Propuesta

### Binding `?` — disponible en todas las pantallas

**Dado** cualquier pantalla con el foco activo
**Cuando** el usuario pulsa `?`
**Entonces** se abre `HelpScreen` via `push_screen`

`HelpScreen` es una pantalla de solo lectura que muestra todos los
keybindings agrupados por contexto.

### Layout de HelpScreen

```
┌──────────────────────────────────────────────────────────────┐
│ sdd-tui — keyboard reference                                  │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  VIEW 1 — Changes                                             │
│  Enter    Open change detail                                  │
│  a        Toggle archived changes                             │
│  /        Search changes                                      │
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
│  Esc      Back to changes                                     │
│                                                               │
│  VIEW 9 — Spec Evolution                                      │
│  D        Toggle delta / canonical                            │
│  Esc      Back                                                │
│                                                               │
│  GLOBAL                                                       │
│  ?        This help screen                                    │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│ [Esc] close                                                   │
└──────────────────────────────────────────────────────────────┘
```

### Implementación

`HelpScreen` es una clase nueva simple:
- `Header` con título fijo
- `ScrollableContainer` con `Static` (contenido Rich con texto organizado)
- Un único binding: `Esc` para cerrar (pop_screen)

El contenido se define como constante en el módulo — no se genera
dinámicamente desde los bindings de Textual, para tener control total
sobre el texto y la agrupación.

`?` se define como binding global en `SddTuiApp` con `priority=True`
para que esté disponible en todas las pantallas.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Generar bindings dinámicamente desde Textual | Siempre sincronizado con el código | La API de introspección de bindings en Textual no garantiza agrupación semántica | Descartada |
| Panel lateral overlay (sin push_screen) | Visible junto al contenido | Más complejo, compite con el layout de cada vista | Descartada |
| Solo mejorar el footer | Sin pantalla nueva | Footer tiene espacio muy limitado, no cabe todo | Descartada |
| **HelpScreen como pantalla dedicada** | Espacio completo, legible, patrón estándar TUI | Mantenimiento manual si cambian los bindings | **Elegida** |

## Impacto Estimado

- **Dominio:** tui
- **Archivos nuevos:**
  - `tui/help.py` — HelpScreen
- **Archivos modificados:**
  - `tui/app.py` — añadir binding `?` global con push_screen(HelpScreen)
- **Breaking changes:** Ninguno — `?` no tiene binding actual
- **Tests afectados:** `tests/test_tui_epics.py` (test que `?` abre HelpScreen)

## Criterios de Éxito

- [ ] `?` desde cualquier pantalla abre HelpScreen
- [ ] HelpScreen muestra todos los bindings actuales agrupados por vista
- [ ] `Esc` cierra HelpScreen y vuelve a la pantalla anterior con estado intacto
- [ ] El contenido es scrollable si no cabe en pantalla

## Preguntas Abiertas

- [ ] ¿Incluir en el help los bindings de las pantallas de documento (DocumentViewerScreen, SpecSelectorScreen)?
- [ ] ¿Actualizar automáticamente el README con el mismo contenido del help screen, o mantenerlos separados?
