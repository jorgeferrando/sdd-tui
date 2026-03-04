# Design: View 8 — Spec Health Dashboard

## Metadata
- **Change:** view-8-spec-health
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** draft

## Resumen Técnico

Dos adiciones independientes que comparten el módulo `core/metrics.py`:

1. **`SpecHealthScreen`** — pantalla nueva accesible con `H` desde View 1. DataTable
   con una fila por change mostrando métricas de calidad (REQ count, EARS %, task
   coverage, artefactos presentes, días de inactividad).

2. **Badge REQ en `PipelinePanel`** — línea extra al final del sidebar de View 2
   (`REQ: N (M%)` o `REQ: —`) construida a partir de `ChangeMetrics`.

El módulo `core/metrics.py` es Python puro sin dependencias de la TUI, testable
de forma aislada, siguiendo el patrón de `core/git_reader.py` y `core/pipeline.py`.

## Arquitectura

```
EpicsView [H] ──────────────────────────────────────────────────► SpecHealthScreen
                                                                       │
                                                                       ▼
                                                              parse_metrics() ── loop por change
                                                                       │
                                                         ┌─────────────┤
                                                         ▼             ▼
                                                   _count_reqs    _get_artifacts
                                                   _get_inactive_days

ChangeDetailScreen (View 2)
  └─► compose() ──► parse_metrics() ──► PipelinePanel(pipeline, tasks, metrics)
                                              └─► _build_content() añade REQ line
  └─► action_refresh_view() ──► parse_metrics() (fresh) ──► nuevo PipelinePanel
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/metrics.py` | Módulo core | `ChangeMetrics` dataclass + `parse_metrics()` + helpers privados |
| `src/sdd_tui/tui/spec_health.py` | Textual Screen | `SpecHealthScreen` — DataTable de métricas por change |
| `tests/test_metrics.py` | Tests unitarios | Cobertura de `parse_metrics()`: REQ parsing, artefactos, inactive days |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Binding `H` + import `SpecHealthScreen` | Punto de entrada a View 8 |
| `src/sdd_tui/tui/change_detail.py` | `PipelinePanel` acepta `metrics: ChangeMetrics \| None`; `ChangeDetailScreen` computa metrics en `__init__` y las pasa al panel | Badge REQ en sidebar de View 2 |

## Scope

- **Total archivos:** 5 (3 nuevos, 2 modificados)
- **Resultado:** Ideal (< 10)

## Diseño Detallado por Archivo

### `core/metrics.py`

```python
INACTIVE_THRESHOLD_DAYS = 7

EARS_TAGS = frozenset({"[Event]", "[State]", "[Unwanted]", "[Optional]", "[Ubiquitous]"})

@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str]          # orden: proposal, spec, research, design, tasks
    inactive_days: int | None     # None si sin commits o git falla

def parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics: ...

# Helpers privados:
def _count_reqs(change_path: Path) -> tuple[int, int]: ...
    # Escanea todos los .md bajo specs/
    # Regex: r"\*\*REQ-\d+\*\*\s+\["
    # EARS: línea también contiene un tag de EARS_TAGS

def _get_artifacts(change_path: Path) -> list[str]: ...
    # Orden fijo: proposal.md → "proposal", specs/*/spec.md → "spec",
    # research.md → "research", design.md → "design", tasks.md → "tasks"
    # Solo incluidos si presentes

def _get_inactive_days(change_name: str, repo_cwd: Path) -> int | None: ...
    # git log --format="%ad" --date=short -1 -F --grep={change_name}
    # Parsea fecha ISO → (date.today() - commit_date).days
    # Retorna None en cualquier error o si no hay match
```

### `tui/spec_health.py`

```python
class SpecHealthScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, changes: list[Change], include_archived: bool = False) -> None: ...

    def on_mount(self) -> None:
        self.title = "sdd-tui — spec health"
        self._populate()

    def _populate(self) -> None:
        # 1. Computar metrics para todos los changes
        all_metrics = {c.name: parse_metrics(c.path, Path.cwd()) for c in self._changes}
        # 2. ¿Algún change tiene research?
        has_research = any("research" in m.artifacts for m in all_metrics.values())
        # 3. Añadir columnas + filas
        table = self.query_one(DataTable)
        table.add_columns("CHANGE", "REQ", "EARS%", "TASKS", "ARTIFACTS", "INACTIVE")
        for change in self._changes:
            m = all_metrics[change.name]
            row = self._build_row(change, m, has_research)
            table.add_row(*row, key=change.name if not change.archived else None)
        # Separador archived igual que EpicsView (si apply)
```

**Formato de celdas:**

| Celda | Fórmula |
|-------|---------|
| `REQ` | `str(req_count)` o `"—"` si 0 |
| `EARS%` | `f"{round(ears/req*100)}%"` si req > 0, else `"—"` |
| `TASKS` | `f"{done}/{total}"` usando `change.tasks`, `"—"` si sin tasks |
| `ARTIFACTS` | `"P"/"."` + `" "` + `"S"/"."` + [` "R"/"."` si has_research] + `" D"/"."` + `" T"/"."` |
| `INACTIVE` | `f"!{n}d"` si > 7, `f"{n}d"` si ≤ 7, `"—"` si None |

**Estilos de alerta:**
- `req_count == 0` → aplicar `Rich.Text` con color `"yellow"` a la fila (o usar `markup=True` con tags)
- `inactive_days > 7` → prefijo `!` ya indica la alerta visualmente (sin necesidad de color extra en la celda)

Nota: Textual `DataTable` no soporta estilos por fila directamente. Se aplica con `Text` de Rich en los valores de celda usando `Text("valor", style="yellow")`.

### `tui/epics.py` — cambios

```python
# Añadir import
from sdd_tui.tui.spec_health import SpecHealthScreen

# Añadir binding
Binding("h", "health", "Health"),

# Añadir action
def action_health(self) -> None:
    self.app.push_screen(SpecHealthScreen(self._changes, self._show_archived))
```

### `tui/change_detail.py` — cambios

**`PipelinePanel`:**
```python
def __init__(self, pipeline: Pipeline, tasks: list[Task], metrics: ChangeMetrics | None = None) -> None:
    content = self._build_content(pipeline, tasks, metrics)
    super().__init__(content)

def _build_content(self, pipeline: Pipeline, tasks: list[Task], metrics: ChangeMetrics | None) -> str:
    lines = ["PIPELINE", ""]
    # ... fases existentes ...
    if metrics is not None:
        lines.append("")
        if metrics.req_count == 0:
            req_line = "  REQ: —"
        else:
            pct = round(metrics.ears_count / metrics.req_count * 100)
            req_line = f"  REQ: {metrics.req_count} ({pct}%)"
        lines.append(req_line)
    return "\n".join(lines)
```

**`ChangeDetailScreen`:**
```python
def __init__(self, change: Change) -> None:
    super().__init__()
    self._change = change
    self._metrics = parse_metrics(change.path, Path.cwd())  # ← nuevo

def compose(self) -> ComposeResult:
    # ...
    yield PipelinePanel(self._change.pipeline, self._change.tasks, self._metrics)  # ← nuevo arg

def action_refresh_view(self) -> None:
    # ... lógica existente ...
    self._metrics = parse_metrics(self._change.path, Path.cwd())  # ← recompute
    top.mount(
        TaskListPanel(self._change.tasks),
        PipelinePanel(self._change.pipeline, self._change.tasks, self._metrics),  # ← nuevo arg
    )
```

**Nota:** `PipelinePanel` muestra `REQ: —` si spec phase es `PENDING` (no habrá specs → `metrics.req_count == 0`). El comportamiento es correcto sin lógica adicional.

### `tests/test_metrics.py`

Sigue el patrón de `tests/test_pipeline.py` con `tmp_path`:

| Test | Qué verifica |
|------|-------------|
| `test_req_count_from_spec_files` | REQ-XX detectados en specs/ |
| `test_ears_count_typed_reqs` | Solo EARS-tagged cuentan como `ears_count` |
| `test_no_specs_returns_zero` | Sin specs/ → req_count=0, ears_count=0 |
| `test_artifacts_presence` | Artefactos presentes en la lista |
| `test_artifacts_research_optional` | research solo si el archivo existe |
| `test_inactive_days_no_git` | tmp_path no es repo git → inactive_days=None |

## Dependencias Técnicas

- Sin nuevas dependencias de paquetes
- `parse_metrics` usa `subprocess` (ya en `git_reader.py`) y `datetime` (stdlib)
- `SpecHealthScreen` importa de `core.metrics` y `core.models`
- `change_detail.py` importa `ChangeMetrics` y `parse_metrics` de `core.metrics`

## Patrones Aplicados

- **Módulo core puro:** `metrics.py` sigue el mismo patrón que `git_reader.py` — sin imports de tui, testable en aislamiento
- **Screen con `push_screen`:** `SpecHealthScreen` sigue el patrón de `DocumentViewerScreen` y `ChangeDetailScreen`
- **Parámetro opcional con default `None`:** `PipelinePanel(metrics=None)` — retrocompatible con cualquier test existente que cree `PipelinePanel` sin métricas
- **Compute en `__init__`:** métricas calculadas antes de `compose()`, igual que `_change` en `ChangeDetailScreen`

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `metrics` como parámetro opcional de `PipelinePanel` | Siempre requerido | Retrocompatibilidad; tests existentes no necesitan cambiar |
| Computar metrics en `ChangeDetailScreen.__init__` | En `on_mount` | `compose()` se llama antes de `on_mount`; el panel necesita metrics al construirse |
| `Text("val", style="yellow")` para alertas en SpecHealth | CSS row styling | DataTable no expone estilos por fila vía CSS; Rich Text es el mecanismo correcto |
| `git log --format="%ad" --date=short` para fecha | `--format="%ci"` + parse ISO | `%ad` con `--date=short` da `YYYY-MM-DD` directamente, sin timezone parsing |
| `_show_archived` pasado como parámetro a `SpecHealthScreen` | Acceso a EpicsView state | Desacoplamiento; SpecHealthScreen no depende de EpicsView internals |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_req_count_from_spec_files` | Unit | REQ-XX detectados correctamente en specs/ |
| `test_ears_count_typed_reqs` | Unit | Solo tags EARS válidos incrementan ears_count |
| `test_no_specs_returns_zero` | Unit | Sin specs/ → req_count=0, ears_count=0 |
| `test_artifacts_presence` | Unit | Lista de artefactos refleja archivos presentes |
| `test_artifacts_research_optional` | Unit | research solo aparece si el archivo existe |
| `test_inactive_days_no_git` | Unit | Directorio no-git → inactive_days=None |

## Notas de Implementación

- El separador `── archived ──` en `SpecHealthScreen` se añade como fila sin key, igual que en `EpicsView._populate()`
- Si `changes` está vacío, mostrar `Static("No active changes")` en lugar del DataTable
- `INACTIVE_THRESHOLD_DAYS` se exporta desde `core/metrics.py` para que los tests lo usen sin hardcodear el valor
- `_count_reqs` escanea solo archivos `.md` bajo `{change_path}/specs/` (recursivo con `rglob("*.md")`)
