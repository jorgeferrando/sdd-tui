# Design: velocity-metrics

## Metadata
- **Change:** velocity-metrics
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-05
- **Estado:** approved

## Resumen Técnico

Nuevo módulo `core/velocity.py` que agrega métricas de throughput y lead time
inferidas de `git log` sobre los changes archivados. Nueva pantalla
`tui/velocity.py` (`VelocityView`) accesible con `V` desde View 1, que
muestra las métricas con barras Unicode y permite exportar un reporte Markdown
al portapapeles.

La arquitectura sigue exactamente los patrones existentes: `core/velocity.py`
replica el patrón de `core/metrics.py` (dataclasses + funciones puras +
subprocess), y `tui/velocity.py` replica el patrón de `tui/doc_viewer.py`
(`Screen` + `ScrollableContainer(Static)` + `j/k` bindings).

## Arquitectura

```
EpicsView.action_velocity()
  → construye archive_dirs (mismo patrón que action_decisions_timeline)
  → push_screen(VelocityView(archive_dirs))
       ↓ on_mount
       compute_velocity(archive_dirs, cwd)
         → itera archive_dirs / YYYY-MM-DD-* / extrae change_name
         → git log --grep=[change_name] → start_date, end_date
         → VelocityReport(changes, weekly_throughput, median, p90, slowest)
       → _build_content(report) → rich.Text
       → query_one(Static).update(text)
```

---

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/velocity.py` | Core module | `ChangeVelocity`, `VelocityReport`, `compute_velocity()` |
| `src/sdd_tui/tui/velocity.py` | TUI Screen | `VelocityView` con barras Unicode + export `E` |
| `tests/test_velocity.py` | Unit tests | Tests de `compute_velocity` con mocks de subprocess |
| `tests/test_tui_velocity.py` | TUI tests | Mount + contenido básico de `VelocityView` |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir `Binding("V", "velocity", "Velocity")` + `action_velocity()` | Entry point desde View 1 |

## Scope

- **Total archivos:** 5
- **Resultado:** Ideal (< 10)

---

## Patrones Aplicados

- **Core module sin deps externas**: igual que `core/metrics.py` y `core/github.py` — dataclasses, subprocess, stdlib solo.
- **Screen read-only con scroll**: igual que `tui/doc_viewer.py` — `Header + ScrollableContainer(Static) + Footer`, `action_scroll_down/up` delegan a `ScrollableContainer`.
- **Action con archive_dirs deduplicados**: igual que `action_decisions_timeline` en `epics.py` — deduplica por `project_path`.
- **Import local en action**: `from sdd_tui.tui.velocity import VelocityView` — patrón establecido para evitar imports circulares.
- **Tests con `patch` + `_mock_result`**: igual que `test_github.py`.

---

## Diseño Detallado — `core/velocity.py`

```python
@dataclass
class ChangeVelocity:
    name: str
    project: str
    start_date: date | None
    end_date: date | None
    lead_time_days: int | None

@dataclass
class VelocityReport:
    changes: list[ChangeVelocity]
    weekly_throughput: list[tuple[date, int]]  # (monday_of_week, count), 8 semanas
    median_lead_time: float | None
    p90_lead_time: float | None
    slowest_change: ChangeVelocity | None
```

### `compute_velocity(archive_dirs, cwd) -> VelocityReport`

1. Para cada `archive_dir` en `archive_dirs`:
   - Saltar si no existe
   - `project_path = archive_dir.parent.parent` (archive → changes → openspec → repo)
   - Iterar subdirectorios con prefijo `YYYY-MM-DD-`
   - `change_name = dir.name.split("-", 3)[3]` (4to token tras separar 3 guiones)
   - `start_date, end_date = _get_change_dates(change_name, project_path)`
   - `lead_time = (end - start).days if start and end else None`

2. Throughput: semanas ISO de las últimas 8 (lunes de cada semana)
   - `week_start = today - timedelta(days=today.weekday())` (lunes actual)
   - `weeks = [week_start - timedelta(weeks=7-i) for i in range(8)]`
   - Contar changes con `end_date` en el rango `[week_start, week_start + 6d]`

3. Lead time stats: `statistics.median()` y percentil 90 manual sobre `lead_times`

### `_get_change_dates(change_name, project_path) -> tuple[date|None, date|None]`

```python
git -C {project_path} log --format=%ad --date=short -F --grep=[{change_name}]
```

- `lines[0]` = end_date (más reciente — git log orden inverso)
- `lines[-1]` = start_date (más antiguo)
- Retorna `(None, None)` en FileNotFoundError, returncode != 0, output vacío, ValueError

---

## Diseño Detallado — `tui/velocity.py`

```python
class VelocityView(Screen):
    BINDINGS = [
        Binding("j", "scroll_down", "Down"),
        Binding("k", "scroll_up", "Up"),
        Binding("e", "export", "Export"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, archive_dirs: list[Path]) -> None: ...

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static("", id="velocity-content"))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — velocity"
        from sdd_tui.core.velocity import compute_velocity
        self._report = compute_velocity(self._archive_dirs, Path.cwd())
        self.query_one("#velocity-content", Static).update(
            _build_content(self._report)
        )

    def action_scroll_down(self) -> None:
        self.query_one(ScrollableContainer).scroll_down()

    def action_scroll_up(self) -> None:
        self.query_one(ScrollableContainer).scroll_up()

    def action_export(self) -> None:
        md = _build_markdown_report(self._report)
        self.app.copy_to_clipboard(md)
        self.notify("Report copied to clipboard")
```

### `_build_content(report) -> rich.Text`

- Si `report.changes` vacío → `Text("No data available")`
- Sección THROUGHPUT: iterar `report.weekly_throughput`
  - `bar_width = round(count / max_count * 20)` (max_count = max de las 8 semanas)
  - Semanas con 0: mostrar `.` (punto)
- Sección LEAD TIME: si `median_lead_time is None` → `"Not enough data..."`

### `_build_markdown_report(report) -> str`

String multilínea Markdown — sin dependencias.

---

## Diseño Detallado — `epics.py`

```python
# En BINDINGS (mayúscula V, consistente con H y X):
Binding("V", "velocity", "Velocity"),

# action:
def action_velocity(self) -> None:
    from sdd_tui.tui.velocity import VelocityView
    seen: set[Path] = set()
    dirs: list[Path] = []
    for change in self._changes:
        if change.project_path and change.project_path not in seen:
            seen.add(change.project_path)
            dirs.append(change.project_path / "openspec" / "changes" / "archive")
    if not dirs:
        dirs = [self.app._openspec_path / "changes" / "archive"]
    self.app.push_screen(VelocityView(dirs))
```

Patrón idéntico a `action_decisions_timeline`.

---

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_empty_archive` | test_velocity.py | archive vacío → VelocityReport vacío |
| `test_single_change_dates` | test_velocity.py | start_date/end_date/lead_time correctos |
| `test_no_commits_gives_none_dates` | test_velocity.py | git vacío → None |
| `test_git_missing_gives_none` | test_velocity.py | FileNotFoundError → VelocityReport vacío |
| `test_throughput_last_8_weeks` | test_velocity.py | cambios esta semana → count correcto |
| `test_throughput_old_change_excluded` | test_velocity.py | change > 8 semanas → no aparece |
| `test_median_with_two_changes` | test_velocity.py | median correcto con 2 valores |
| `test_p90_with_enough_data` | test_velocity.py | P90 correcto con lista |
| `test_single_change_no_median` | test_velocity.py | 1 change → median=None |
| `test_slowest_change` | test_velocity.py | slowest_change = el de mayor lead_time |
| `test_multiproject_aggregates` | test_velocity.py | 2 archive_dirs → changes de ambos |
| `test_velocity_view_mounts` | test_tui_velocity.py | VelocityView se monta sin error |
| `test_velocity_view_no_data` | test_tui_velocity.py | sin archive → muestra "No data available" |
| `test_velocity_binding_in_epics` | test_tui_epics.py | `V` registrado en EpicsView.BINDINGS |

Total estimado: ~14 tests nuevos → 150 + 14 = **164 tests**

---

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `_build_content` separada de `on_mount` | Lógica inline | Testable de forma aislada sin montar la TUI |
| `_build_markdown_report` separada | Construir en `action_export` | Testable; `action_export` queda 2 líneas |
| `compute_velocity` con import local en `on_mount` | Import top-level | Patrón establecido en `action_*` de epics.py |
| `_get_change_dates` función privada | Método en dataclass | Patrón de `core/metrics.py` — funciones privadas del módulo |
| `project_path = archive_dir.parent.parent` | Pasar project_path explícito | `archive_dir` tiene estructura fija: `.../openspec/changes/archive` |
| `statistics.median` | Cálculo manual | Stdlib; ya usada en el proyecto implícitamente |
| Sin worker async | `@work(thread=True)` | git log por change (sin diff) es O(ms); no bloquea el event loop perceptiblemente |

## Abierto / Pendiente

Ninguno.
