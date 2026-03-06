# Design: Complexity Badge

## Metadata
- **Change:** complexity-badge
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** approved

## Resumen Técnico

Dos cambios independientes y mínimos: uno en `core/metrics.py` para calcular
complejidad, otro en `tui/epics.py` para mostrarla. Sin nuevos módulos ni
dependencias. `parse_metrics` gana dos campos; `EpicsView` gana una columna.

## Arquitectura

```
EpicsView._populate()
  └── parse_metrics(change.path, change.project_path)  ← ya existía para SpecHealth
        ├── _count_reqs()               ← sin cambios
        ├── _get_artifacts()            ← sin cambios
        ├── _get_inactive_days()        ← sin cambios
        └── _get_complexity()           ← nuevo
              ├── task_count  = contar líneas [x]/[ ] en tasks.md
              ├── spec_lines  = contar líneas en specs/*/spec.md
              └── git_files   = git log --name-only --format= -F --grep=[name]
                                → set de paths distintos → len()
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/metrics.py` | Añadir `complexity_score`, `complexity_label` a `ChangeMetrics`; nueva función `_get_complexity()` | REQ-CB-01 al 07 |
| `src/sdd_tui/tui/epics.py` | Añadir columna `SIZE` en `add_columns`, `_add_change_row`, y filas separadoras | REQ-CB-10 al 15 |
| `tests/test_metrics.py` | Tests unitarios del cálculo de score y labels | Cobertura de REQ-CB-01/06 |
| `tests/test_tui_epics.py` | Test que verifica presencia de columna SIZE con label correcto | Cobertura de REQ-CB-10/12 |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal

## Implementación detallada

### core/metrics.py

**`ChangeMetrics`** — añadir dos campos con defaults para no romper código existente:
```python
@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str] = field(default_factory=list)
    inactive_days: int | None = None
    complexity_score: int = 0       # nuevo
    complexity_label: str = "XS"    # nuevo
```

**`parse_metrics`** — añadir llamada a `_get_complexity`:
```python
def parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics:
    ...
    score, label = _get_complexity(change_path, repo_cwd)
    return ChangeMetrics(..., complexity_score=score, complexity_label=label)
```

**`_get_complexity(change_path, repo_cwd) -> tuple[int, str]`** — nueva función:
```python
_COMPLEXITY_THRESHOLDS = [(41, "XL"), (25, "L"), (13, "M"), (6, "S"), (0, "XS")]

def _get_complexity(change_path: Path, repo_cwd: Path) -> tuple[int, str]:
    task_count = _count_tasks(change_path)
    spec_lines = _count_spec_lines(change_path)
    git_files  = _count_git_files(change_path.name, repo_cwd)
    score = task_count * 3 + spec_lines // 50 + git_files
    label = next(lbl for threshold, lbl in _COMPLEXITY_THRESHOLDS if score >= threshold)
    return score, label
```

**`_count_tasks(change_path)`** — cuenta líneas `- [x]` y `- [ ]` en tasks.md:
```python
_TASK_LINE = re.compile(r"^\s*-\s+\[[ x]\]")

def _count_tasks(change_path: Path) -> int:
    tasks_file = change_path / "tasks.md"
    if not tasks_file.exists():
        return 0
    return sum(1 for line in tasks_file.read_text(errors="replace").splitlines()
               if _TASK_LINE.match(line))
```

**`_count_spec_lines(change_path)`** — suma líneas de specs/*/spec.md:
```python
def _count_spec_lines(change_path: Path) -> int:
    specs_dir = change_path / "specs"
    if not specs_dir.exists():
        return 0
    total = 0
    for md in specs_dir.rglob("*.md"):
        total += len(md.read_text(errors="replace").splitlines())
    return total
```

**`_count_git_files(change_name, repo_cwd)`** — archivos únicos en commits del change:
```python
def _count_git_files(change_name: str, repo_cwd: Path) -> int:
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--format=", "-F", f"--grep=[{change_name}]"],
            cwd=repo_cwd, capture_output=True, text=True,
        )
        if result.returncode != 0:
            return 0
        files = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        return len(files)
    except FileNotFoundError:
        return 0
```

### tui/epics.py

**`_populate`** — cambiar `add_columns`:
```python
# antes:
table.add_columns("change", *PHASES)
# después:
table.add_columns("change", "SIZE", *PHASES)
```

**Filas separadoras** — añadir `""` como segundo elemento en cada `table.add_row` de separador:
```python
table.add_row(f"─── {project_name} ───", "", "", "", "", "", "", "")
table.add_row("  (no active changes)", "", "", "", "", "", "", "")
table.add_row("── archived ──", "", "", "", "", "", "", "")
```

**`_add_change_row`** — calcular métrica y añadir celda SIZE:
```python
def _add_change_row(self, table: DataTable, change: Change) -> None:
    try:
        metrics = parse_metrics(change.path, change.project_path or Path.cwd())
        label = metrics.complexity_label
        is_xl = label == "XL"
    except Exception:
        label, is_xl = "?", False

    size_cell = Text(label, style="yellow" if is_xl else "")
    pipeline = change.pipeline
    name_cell = ...  # sin cambios
    row = (name_cell, size_cell, _phase_symbol(...), ...)
    table.add_row(*row, key=change.name)
```

### Tests

**test_metrics.py** — 5 tests nuevos:
- `test_complexity_score_all_zero` → score=0, label="XS"
- `test_complexity_score_tasks_only` → 4 tareas → score=12, label="S"
- `test_complexity_score_formula` → tareas + spec_lines + git mock → verifica fórmula completa
- `test_complexity_label_xl` → score ≥ 41 → "XL"
- `test_complexity_git_files_fallback` → repo_cwd no existe → git_files=0, no excepción

**test_tui_epics.py** — 1 test nuevo (unitario, sin Textual app):
- `test_add_change_row_shows_size_column` → instancia `_EpicsApp`, verifica que la columna SIZE está en la tabla con algún label válido

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `_get_complexity` lee tasks.md directamente | Recibir `task_count` como parámetro | `parse_metrics` es autónomo — no depende del caller para datos |
| `try/except Exception` en `_add_change_row` para métricas | Fallar silenciosamente con `"?"` | REQ-CB-15: la TUI nunca se rompe por un fallo de métricas |
| Defaults en `ChangeMetrics` (`score=0, label="XS"`) | Campos obligatorios | Retrocompatibilidad: tests y código existente que crea `ChangeMetrics` directamente no necesitan cambios |
| `_COMPLEXITY_THRESHOLDS` como lista de tuplas descendente | dict | `next(... if score >= threshold)` con orden descendente es idiomático y simple |
| `parse_metrics` importado en `_add_change_row` (ya importado en epics.py) | Caché de métricas en Change | `Change` es modelo de dominio; métricas son presentación — no mezclar |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_complexity_score_all_zero` | Unit | score=0 → XS |
| `test_complexity_score_tasks_only` | Unit | solo tareas → fórmula correcta |
| `test_complexity_score_formula` | Unit | los tres inputs → score y label correctos |
| `test_complexity_label_xl` | Unit | score 41+ → XL |
| `test_complexity_git_files_fallback` | Unit | git no disponible → no excepción |
| `test_add_change_row_shows_size_column` | Unit/TUI | columna SIZE aparece en tabla |

## Notas de Implementación

- `parse_metrics` ya se importa en `epics.py` indirectamente (a través de `spec_health`). Hay que añadir el import directo: `from sdd_tui.core.metrics import parse_metrics`.
- Los separadores en `_populate` tienen actualmente 7 valores `""` — con la nueva columna pasan a 8. Hay que actualizar los 3 puntos: separador de proyecto, placeholder "no active changes", y separador "archived".
- El test `test_no_match_row` en `_populate` también pasa valores vacíos — actualizar a 8.
