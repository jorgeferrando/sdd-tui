# Design: progress-dashboard

## Metadata
- **Change:** progress-dashboard
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** draft

## Resumen Técnico

Patrón idéntico a `velocity`: función pura en `core/progress.py` que transforma
`list[Change]` en un `ProgressReport`, y una pantalla `ProgressDashboard` en
`tui/progress.py` que renderiza ese report en un `ScrollableContainer` + `Static`
(rich.Text). Sin I/O, sin git, sin disco — todo el dato viene del modelo en memoria.

`EpicsView` pasa directamente `self._changes` al abrir la pantalla, igual que
hace con `SpecHealthScreen` y `VelocityView`.

## Arquitectura

```
EpicsView (binding P)
  → ProgressDashboard(changes: list[Change])
      → compute_progress(changes) → ProgressReport
      → _build_content(report) → rich.Text
      → ScrollableContainer(Static)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/progress.py` | Módulo core | `ProgressReport`, `ChangeProgress`, `compute_progress()` |
| `src/sdd_tui/tui/progress.py` | Screen TUI | `ProgressDashboard`, `_build_content()`, `_build_markdown_report()` |
| `tests/test_progress.py` | Tests unit | Cobertura de `compute_progress()` |
| `tests/test_tui_progress.py` | Tests TUI | Montar `ProgressDashboard`, binding `P`, export |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir `Binding("P", "progress", "Progress")` + `action_progress()` | Acceso desde View 1 |

## Scope

- **Total archivos:** 5 (4 nuevos + 1 modificado)
- **Resultado:** Ideal

## Diseño de `core/progress.py`

```python
PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]

@dataclass
class ChangeProgress:
    name: str
    tasks_done: int
    tasks_total: int
    furthest_phase: str | None  # última fase DONE, None si ninguna

@dataclass
class ProgressReport:
    changes: list[ChangeProgress]
    total_done: int
    total_tasks: int
    percent: int                          # 0 si total_tasks == 0
    pipeline_distribution: dict[str, int] # fase → nº changes con esa como furthest

def compute_progress(changes: list[Change]) -> ProgressReport:
    ...
```

**`furthest_phase`**: iterar PHASES en orden, guardar el último con `PhaseState.DONE`.
```python
furthest = None
for phase in PHASES:
    if getattr(change.pipeline, phase) == PhaseState.DONE:
        furthest = phase
```

**`pipeline_distribution`**: inicializar todas las fases a 0, incrementar solo las
que son `furthest_phase` de algún change.

## Diseño de `tui/progress.py`

```python
class ProgressDashboard(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("e", "export", "Export"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, changes: list[Change]) -> None: ...
    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="progress-content"))
        yield Footer()
    def on_mount(self) -> None:
        self.title = "sdd-tui — progress"
        report = compute_progress(self._changes)
        self.query_one("#progress-content", Static).update(_build_content(report))
    def action_scroll_down(self) -> None: ...   # delega a ScrollableContainer
    def action_scroll_up(self) -> None: ...
    def action_export(self) -> None: ...        # _build_markdown_report → clipboard
```

**`_build_content(report)`** → `rich.Text` con tres secciones:
1. `GLOBAL` — changes count, tasks done/total, percent, barra 20 chars
2. `BY CHANGE` — línea por change: nombre + barra 12 chars + ratio + furthest_phase
3. `PIPELINE DISTRIBUTION` — línea por fase + barra proporcional + count

**Barra de progreso** (función auxiliar `_bar(done, total, width)`):
```python
filled = round(done / total * width) if total > 0 else 0
return "█" * filled + "░" * (width - filled)
```

## Diseño de modificación en `epics.py`

```python
# En BINDINGS:
Binding("P", "progress", "Progress"),

# Nueva action:
def action_progress(self) -> None:
    from sdd_tui.tui.progress import ProgressDashboard
    self.app.push_screen(ProgressDashboard(self._changes))
```

## Tests Planificados

### `tests/test_progress.py` (unit, sin mocks)

| Test | Qué verifica |
|------|-------------|
| `test_empty_list` | `compute_progress([])` → `percent=0`, `total_tasks=0`, `changes=[]` |
| `test_no_tasks_no_divide_by_zero` | Changes sin tasks → `percent=0`, `total_tasks=0` |
| `test_all_done` | Todas las tasks done → `percent=100` |
| `test_partial_progress` | 3/5 done → `percent=60` |
| `test_furthest_phase_none` | Ninguna fase DONE → `furthest_phase=None` |
| `test_furthest_phase_spec` | Solo propose+spec DONE → `furthest_phase="spec"` |
| `test_furthest_phase_apply` | Hasta apply DONE → `furthest_phase="apply"` |
| `test_pipeline_distribution_single` | Un change con furthest=design → `dist["design"]==1` |
| `test_pipeline_distribution_all_phases` | Cada change en una fase distinta → distribución correcta |
| `test_pipeline_distribution_zero_phases` | Ningún change con fases DONE → todos a 0 |
| `test_change_without_tasks_shows_zero_zero` | tasks_done=0, tasks_total=0 para change sin tasks |
| `test_multiple_changes_aggregate` | Suma correcta de done/total de varios changes |

### `tests/test_tui_progress.py` (TUI, async)

| Test | Qué verifica |
|------|-------------|
| `test_progress_dashboard_mounts` | Pantalla monta sin errores con lista de changes |
| `test_progress_dashboard_empty` | Lista vacía → "No changes to display" en contenido |
| `test_binding_p_opens_progress` | `P` desde EpicsView → ProgressDashboard apilada |
| `test_escape_closes_progress` | Escape → vuelve a EpicsView |

## Patrones Aplicados

- **VelocityView** como referencia directa: misma estructura `ScrollableContainer + Static`, mismo patrón de export, mismos bindings j/k/e/Escape
- **`compute_velocity`** como referencia para `compute_progress`: función pura, recibe datos ya cargados, devuelve dataclass
- **Import diferido** en `action_progress()`: `from sdd_tui.tui.progress import ProgressDashboard` — consistente con `action_velocity`, `action_releases`, etc.

## Notas de Implementación

- `_build_content` devuelve `rich.Text` (no `str`) para poder usar `style=` en secciones
- Las barras usan `░` para el fondo vacío (más visible que espacios en terminales oscuros)
- `pipeline_distribution` se inicializa con todas las fases a 0 antes de iterar — evita `KeyError` al renderizar
- Para tests TUI: mismo patrón que `test_tui_velocity.py` — `_git_mock()` + `app.run_test()`
