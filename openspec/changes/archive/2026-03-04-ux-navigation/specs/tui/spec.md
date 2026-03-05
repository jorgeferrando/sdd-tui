# Spec: TUI — UX Navigation (Scroll, Drill-down, Paths)

## Metadata
- **Dominio:** tui
- **Change:** ux-navigation
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

Tres fricciones de navegación independientes que degradan la fluidez de uso:
usuarios técnicos esperan `j/k` en cualquier contenido scrollable;
`SpecHealthScreen` tiene un DataTable interactivo que no navega a ningún lado;
rutas de `openspec/` calculadas con `Path.cwd()` en lugar del path centralizado de la app.

## Comportamiento Actual

- `DocumentViewerScreen`, `SpecEvolutionScreen` y `DecisionsTimeline` solo admiten scroll con flechas o mouse.
- `SpecHealthScreen` tiene `cursor_type="row"` pero Enter no hace nada.
- `EpicsView.action_steering`, `EpicsView.action_decisions_timeline` y `DecisionsTimeline` calculan el path como `Path.cwd() / "openspec" / ...`.
- `SddTuiApp` expone los changes como `_changes` (privado).

## Requisitos (EARS)

- **REQ-01** `[Event]` When el usuario pulsa `j` en `DocumentViewerScreen`, `SpecEvolutionScreen` o `DecisionsTimeline`, la pantalla SHALL hacer scroll hacia abajo.
- **REQ-02** `[Event]` When el usuario pulsa `k` en `DocumentViewerScreen`, `SpecEvolutionScreen` o `DecisionsTimeline`, la pantalla SHALL hacer scroll hacia arriba.
- **REQ-03** `[Ubiquitous]` The bindings `j` y `k` SHALL estar disponibles en todas las pantallas de solo lectura (viewers) de la aplicación.
- **REQ-04** `[Event]` When el usuario pulsa Enter sobre una fila en `SpecHealthScreen`, la app SHALL hacer `push_screen(ChangeDetailScreen(change))` con el change de la fila seleccionada.
- **REQ-05** `[Unwanted]` If la fila seleccionada en `SpecHealthScreen` no tiene key (separador), Enter SHALL no hacer nada.
- **REQ-06** `[Event]` When se abre `ChangeDetailScreen` desde `SpecHealthScreen`, el usuario SHALL poder volver a `SpecHealthScreen` con `Esc`.
- **REQ-07** `[Ubiquitous]` The `SddTuiApp` SHALL exponer los changes como propiedad pública `changes` (sin prefijo `_`).
- **REQ-08** `[Ubiquitous]` The paths de `openspec/` en `EpicsView` y `DecisionsTimeline` SHALL calcularse a partir de `self.app._openspec_path` (EpicsView) o recibirse como parámetro/propiedad (DecisionsTimeline), no como `Path.cwd() / "openspec"`.

### Escenarios de verificación

**REQ-04** — Drill-down desde SpecHealthScreen
**Dado** `SpecHealthScreen` abierto con al menos un change listado
**Cuando** el usuario pulsa Enter sobre la fila de `my-change`
**Entonces** se abre `ChangeDetailScreen` con el change `my-change`; el stack de navegación es View1 → SpecHealthScreen → ChangeDetailScreen

**REQ-08** — Path centralizado
**Dado** la app lanzada con `sdd-tui /otro/path/openspec`
**Cuando** el usuario pulsa `s` (steering) o `X` (decisions timeline) en View 1
**Entonces** las rutas se resuelven relativas a `/otro/path/openspec`, no a `Path.cwd() / "openspec"`

## Interfaces / Contratos

### `SddTuiApp.changes` (nueva propiedad pública)

```python
@property
def changes(self) -> list[Change]:
    return self._changes
```

Reemplaza el acceso directo a `_changes` en todos los puntos de uso.

### `SpecHealthScreen` — drill-down

```python
def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    change = self._change_map.get(event.row_key.value)
    if change:
        self.app.push_screen(ChangeDetailScreen(change))
```

Reutiliza el mismo patrón de `EpicsView`.

### Bindings `j/k` en viewers

```python
BINDINGS = [
    Binding("j", "scroll_down", "Down"),
    Binding("k", "scroll_up", "Up"),
    Binding("escape", "app.pop_screen", "Back"),
]
```

`scroll_down` y `scroll_up` son acciones nativas de `ScrollableContainer` en Textual.
Sin implementación custom. El step de scroll es el por defecto de Textual.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `push_screen` para drill-down desde SpecHealthScreen | Replace screen | Consistente con el resto de la app; pila de 3 niveles es válida |
| Propiedad pública `app.changes` | Acceder a `_changes` directamente | Más limpio; contrato explícito; no depende de convención de prefijo privado |
| Fix path también en `DecisionsTimeline` | Solo EpicsView | `DecisionsTimeline` tiene exactamente el mismo bug; hacerlo a medias no aporta |
| `j/k` en los 3 viewers | Solo `DocumentViewerScreen` | Consistencia total — usuarios técnicos esperan `j/k` en cualquier contenido scrollable |
| Acciones nativas `scroll_down`/`scroll_up` | Implementación custom | Textual ya las expone en `ScrollableContainer`; cero código extra |

## Abierto / Pendiente

Ninguno.
