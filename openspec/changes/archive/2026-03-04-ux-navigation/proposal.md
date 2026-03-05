# Proposal: UX Navigation — Scroll, Drill-down y Paths

## Metadata
- **Change:** ux-navigation
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

Tres fricciones de navegación independientes que degradan la fluidez de uso:

### Problema 1 — Sin `j/k` en viewers de texto

`DocumentViewerScreen`, `SpecEvolutionScreen` y `DecisionsTimeline` requieren
flechas o mouse para hacer scroll. Son las únicas superficies de la app que
no siguen la convención vim de `j/k`. Los usuarios técnicos (el target de
sdd-tui) esperan `j/k` en cualquier lista o contenido scrollable.

### Problema 2 — SpecHealthScreen no navega a ningún lado

`SpecHealthScreen` tiene `cursor_type="row"` en su DataTable, pero Enter
no hace nada — el cursor crea expectativa de interactividad que no se cumple.
Desde la vista de salud sería natural hacer drill-down al detalle del change
seleccionado (View 2), que es exactamente lo que el usuario quiere hacer
cuando ve un indicador de baja calidad en un change concreto.

### Problema 3 — Rutas `openspec/` hardcodeadas en EpicsView

`action_steering` y `action_decisions_timeline` en `EpicsView` construyen
la ruta como `Path.cwd() / "openspec"` en lugar de usar `self.app._openspec_path`.
Si la app se lanza desde un directorio distinto al root del repo
(o si el path de openspec se cambia en el futuro), estas acciones apuntan mal.

## Solución Propuesta

### Fix 1 — Bindings `j/k` en viewers de texto

Añadir en `DocumentViewerScreen`, `SpecEvolutionScreen` y `DecisionsTimeline`:
```python
BINDINGS = [
    ("j", "scroll_down", "Down"),
    ("k", "scroll_up", "Up"),
    ("escape", "app.pop_screen", "Back"),
]
```

`ScrollableContainer` de Textual ya expone `scroll_down` y `scroll_up` como
acciones — no requiere implementación custom. El step de scroll será el
por defecto de Textual (3 líneas).

### Fix 2 — Drill-down desde SpecHealthScreen

Añadir handler `on_data_table_row_selected` en `SpecHealthScreen`:
- Leer el change name de la fila seleccionada (columna 0)
- Buscar el objeto `Change` correspondiente en `self.app._changes`
- Hacer `push_screen(ChangeDetailScreen(change))`

Esto reutiliza exactamente el mismo flujo que `EpicsView` — el patrón ya existe.

### Fix 3 — Usar `_openspec_path` en lugar de `Path.cwd()`

En `EpicsView.action_steering`:
```python
# Antes
steering_path = Path.cwd() / "openspec" / "steering.md"
# Después
steering_path = self.app._openspec_path / "steering.md"
```

En `EpicsView.action_decisions_timeline`:
```python
# Antes
archive_path = Path.cwd() / "openspec" / "changes" / "archive"
# Después
archive_path = self.app._openspec_path / "changes" / "archive"
```

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| `j/k` solo en DocumentViewerScreen | Menor scope | Inconsistencia parcial | Descartada — aplicar en todos o en ninguno |
| SpecHealthScreen abre View 1 filtrada por change | Mantiene contexto | Requiere feature de filtrado (no existe) | Descartada — drill-down directo a View 2 es más simple |
| SpecHealthScreen sin cursor (quitar `cursor_type="row"`) | Elimina expectativa falsa | Pierde la oportunidad de navegación útil | Descartada |
| **Drill-down directo a ChangeDetailScreen** | Reutiliza patrón existente, cero código nuevo en app.py | Requiere acceder a `self.app._changes` desde SpecHealthScreen | **Elegida** |

## Impacto Estimado

- **Dominio:** tui (UI layer únicamente)
- **Archivos modificados:**
  - `tui/doc_viewer.py` — bindings `j/k` en DocumentViewerScreen
  - `tui/spec_evolution.py` — bindings `j/k` en SpecEvolutionScreen y DecisionsTimeline
  - `tui/spec_health.py` — handler drill-down + import ChangeDetailScreen
  - `tui/epics.py` — fix rutas hardcodeadas
- **Breaking changes:** Ninguno
- **Tests afectados:** Si existen tests de navegación, pueden necesitar actualización

## Criterios de Éxito

- [ ] `j` y `k` hacen scroll en DocumentViewerScreen
- [ ] `j` y `k` hacen scroll en SpecEvolutionScreen
- [ ] `j` y `k` hacen scroll en DecisionsTimeline
- [ ] Enter sobre una fila en SpecHealthScreen abre ChangeDetailScreen del change seleccionado
- [ ] `action_steering` funciona correctamente cuando la app se lanza con `sdd-tui /otro/path`
- [ ] `action_decisions_timeline` funciona correctamente cuando la app se lanza con `sdd-tui /otro/path`

## Preguntas Abiertas

- [ ] ¿El drill-down desde SpecHealthScreen debería hacer `push_screen` (pila de 3 niveles) o reemplazar la pantalla? Push es más consistente con el resto de la app.
- [ ] ¿Exponer `_changes` como propiedad pública en `SddTuiApp` antes de usarlo desde SpecHealthScreen?
