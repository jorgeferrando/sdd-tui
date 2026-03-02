# Design: View 2 — Change detail con task states y git info

## Metadata
- **Change:** view-2-change-detail
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-02
- **Estado:** draft

## Resumen Técnico

Dos bloques de trabajo independientes que se integran:

1. **Core extensions**: extensión de modelos (`CommitInfo`, `TaskGitState`),
   corrección del `TaskParser` (negrita + hints de commit) y nuevo
   `GitReader.find_commit()`. Todo testable en aislamiento.

2. **TUI View 2**: `ChangeDetailScreen` (Textual `Screen`) con layout
   de dos paneles estáticos. Navegación vía `push_screen` / `pop_screen`.
   La orquestación (cargar tasks + git states) vive en `SddTuiApp`.

El `DataTable` de View 1 ya tiene cursor — solo falta capturar Enter para
leer `cursor_row` y hacer push de la pantalla de detalle.

## Arquitectura

```
EpicsView
  [Enter] → app.push_screen(ChangeDetailScreen(change))
               └── TaskListPanel(change.tasks)   ← panel izq (Static scrollable)
               └── PipelinePanel(change.pipeline) ← panel der (Static fijo)
  [Esc]   → app.pop_screen()

SddTuiApp._load_changes()
  └── reader.load()          → List[Change] (sin tasks)
  └── inferer.infer()        → Pipeline por change
  └── _load_tasks(change)    → List[Task] con git states
        └── TaskParser.parse()       → List[Task] con commit_hints
        └── GitReader.find_commit()  → CommitInfo | None por task
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/models.py` | Añadir `CommitInfo`, `TaskGitState`; extender `Task` (3 campos) y `Change` (1 campo) | Nuevos modelos requeridos por View 2 |
| `src/sdd_tui/core/pipeline.py` | `TaskParser`: regex acepta `**TXX**`; capturar líneas `- Commit:` | Fix bug + hint de commit |
| `src/sdd_tui/core/git_reader.py` | Añadir `find_commit(message_fragment, cwd)` | Buscar commit por mensaje |
| `src/sdd_tui/tui/app.py` | Añadir `_parser`, `_load_tasks()`; importar `ChangeDetailScreen` | Orquestación de task git states |
| `src/sdd_tui/tui/epics.py` | Añadir binding `Enter` → `action_select_change()` | Navegación a View 2 |
| `tests/test_pipeline.py` | Añadir 3 tests: bold format, commit hint, backtick stripping | Cobertura de nuevas reglas |

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/tui/change_detail.py` | TUI | `ChangeDetailScreen` + `TaskListPanel` + `PipelinePanel` |
| `tests/test_git_reader.py` | Test | 3 tests de `find_commit()` con mock de subprocess |

## Scope

- **Total archivos:** 8
- **Resultado:** Ideal

## Detalle por Módulo

### `core/models.py`

```python
@dataclass
class CommitInfo:
    hash: str      # 7 chars
    message: str

class TaskGitState(Enum):
    COMMITTED = "committed"
    PENDING   = "pending"

@dataclass
class Task:
    id: str
    description: str
    done: bool
    amendment: str | None = None
    commit_hint: str | None = None     # NEW
    git_state: TaskGitState = TaskGitState.PENDING  # NEW
    commit: CommitInfo | None = None   # NEW

@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline = field(default_factory=Pipeline)
    tasks: list[Task] = field(default_factory=list)  # NEW
```

### `core/pipeline.py` — TaskParser

```python
# Acepta "T01" y "**T01**"
_TASK_RE = re.compile(r"^- \[(x| )\] \*{0,2}(T\d+)\*{0,2} (.+)$")
# Captura commit hint indentado
_COMMIT_HINT_RE = re.compile(r"^\s{2,}-\s+Commit:\s+`?(.+?)`?\s*$")

def parse(self, tasks_md: Path) -> list[Task]:
    tasks = []
    current_amendment = None
    last_task = None

    for line in tasks_md.read_text().splitlines():
        stripped = line.strip()

        if amendment_match := self._AMENDMENT_RE.match(stripped):
            current_amendment = amendment_match.group(1).strip()
            last_task = None
            continue

        if task_match := self._TASK_RE.match(stripped):
            task = Task(
                id=task_match.group(2),
                description=task_match.group(3).strip(),
                done=task_match.group(1) == "x",
                amendment=current_amendment,
            )
            tasks.append(task)
            last_task = task
            continue

        # Commit hint: match on raw line (not stripped) for indentation check
        if last_task is not None:
            if hint_match := self._COMMIT_HINT_RE.match(line):
                last_task.commit_hint = hint_match.group(1).strip()
                last_task = None  # solo primera línea de hint

    return tasks
```

### `core/git_reader.py` — find_commit()

```python
def find_commit(self, message_fragment: str | None, cwd: Path) -> CommitInfo | None:
    if message_fragment is None:
        return None
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--abbrev-commit",
             f"--grep={message_fragment}", "-1"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        parts = result.stdout.strip().split(" ", 1)
        if len(parts) < 2:
            return None
        return CommitInfo(hash=parts[0], message=parts[1])
    except FileNotFoundError:
        return None
```

### `tui/app.py` — _load_tasks()

```python
from sdd_tui.core.pipeline import PipelineInferer, TaskParser
from sdd_tui.core.models import TaskGitState

def __init__(self, openspec_path):
    ...
    self._parser = TaskParser()  # NEW

def _load_changes(self) -> list[Change]:
    changes = self._reader.load(self._openspec_path)
    for change in changes:
        change.pipeline = self._inferer.infer(change.path, self._git)
        change.tasks = self._load_tasks(change)  # NEW
    return changes

def _load_tasks(self, change: Change) -> list[Task]:
    tasks_md = change.path / "tasks.md"
    if not tasks_md.exists():
        return []
    tasks = self._parser.parse(tasks_md)
    for task in tasks:
        if task.commit_hint:
            commit_info = self._git.find_commit(task.commit_hint, change.path)
            if commit_info:
                task.git_state = TaskGitState.COMMITTED
                task.commit = commit_info
    return tasks
```

### `tui/epics.py` — Enter binding

```python
BINDINGS = [
    Binding("enter", "select_change", "Detail"),
    Binding("r", "refresh", "Refresh"),
    Binding("q", "quit", "Quit"),
]

def action_select_change(self) -> None:
    row_index = self.query_one(DataTable).cursor_row
    if 0 <= row_index < len(self._changes):
        self.app.push_screen(ChangeDetailScreen(self._changes[row_index]))
```

### `tui/change_detail.py`

```python
class ChangeDetailScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield TaskListPanel(self._change).classes("tasks-panel")
            yield PipelinePanel(self._change.pipeline).classes("pipeline-panel")
        yield Footer()

class TaskListPanel(ScrollableContainer):
    # Rendea texto formateado con cada tarea:
    # "  ✓ a1b2c3  T01  description"
    # "  ·         T02  description"
    # "  ── amendment: name ──"

class PipelinePanel(Widget):
    # Rendea las 6 fases con ✓ / ·
    # Fijo, no scrollable
```

**CSS layout:**
```css
TaskListPanel  { width: 2fr; height: 1fr; overflow-y: auto; }
PipelinePanel  { width: 1fr; height: 1fr; border-left: solid $panel; }
```

**Formato de fila de tarea:**
```
  ✓ a1b2c3  T01  Create pyproject.toml
  ·         T02  Add core models
```
- Estado: `✓` (COMMITTED) / `·` (PENDING)
- Hash: 7 chars si COMMITTED, 7 espacios si PENDING
- Separadores de amendment: `  ── amendment: {name} ──`

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_parse_bold_format` | `test_pipeline.py` | `**T01**` parseado igual que `T01` |
| `test_parse_captures_commit_hint` | `test_pipeline.py` | hint extraído y sin backticks |
| `test_parse_no_hint_when_absent` | `test_pipeline.py` | tarea sin `- Commit:` → `commit_hint=None` |
| `test_find_commit_returns_none_for_none_fragment` | `test_git_reader.py` | `None` → `None` sin llamar git |
| `test_find_commit_returns_commit_info` | `test_git_reader.py` | subprocess mock → `CommitInfo` |
| `test_find_commit_returns_none_when_not_found` | `test_git_reader.py` | salida vacía → `None` |

**Total: 6 tests nuevos**

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `_load_tasks()` en `SddTuiApp` | En `OpenspecReader` | Reader permanece simple; orquestación en app |
| `Static` panels (no `ListView`) | `ListView` seleccionable | Sin selección en v2; ListView va en View 3 |
| Mock de subprocess en tests | Git real en tmp_path | Tests deterministas, sin setup de repo |
| `cursor_row` del DataTable para selección | Almacenar index aparte | API nativa de Textual, sin estado extra |
