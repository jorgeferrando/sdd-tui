# Design: Bootstrap — Project setup + openspec reader + Epics view

## Metadata
- **Change:** bootstrap
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-02
- **Estado:** draft

## Resumen Técnico

Proyecto Python con layout `src/`. Core domain en Python puro (stdlib únicamente),
sin dependencias de TUI. Textual solo en la capa `tui/`. `uv` como gestor de
dependencias y entorno virtual. Tests con `pytest` sobre el core domain exclusivamente.

El arranque detecta automáticamente el `openspec/` del directorio actual (o el
indicado como argumento). La TUI muestra View 1 (lista de changes con su pipeline).

## Arquitectura

```
CLI (sdd-tui)
    └── SddTuiApp(openspec_path)        [Textual App]
          └── EpicsView                 [DataTable]
                └── OpenspecReader.load(path) → List[Change]
                      └── por cada subdirectorio:
                            PipelineInferer.infer(change_path) → Pipeline
                              ├── comprobar huellas en disco
                              ├── TaskParser.parse(tasks_md) → List[Task]
                              └── GitReader.is_clean(cwd) → bool | None
```

## Estructura de Archivos

```
pyproject.toml
src/
  sdd_tui/
    __init__.py
    core/
      models.py        ← dataclasses + enums + OpenspecNotFoundError
      reader.py        ← OpenspecReader
      pipeline.py      ← PipelineInferer + TaskParser
      git_reader.py    ← GitReader
    tui/
      app.py           ← SddTuiApp + main()
      epics.py         ← EpicsView
tests/
  conftest.py          ← fixtures (directorio openspec/ temporal)
  test_reader.py
  test_pipeline.py
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `pyproject.toml` | Config | Dependencias, scripts, metadatos del proyecto |
| `src/sdd_tui/__init__.py` | Package | Vacío |
| `src/sdd_tui/core/models.py` | Modelos | `Change`, `Pipeline`, `Task`, `PhaseState`, `OpenspecNotFoundError` |
| `src/sdd_tui/core/reader.py` | Core | `OpenspecReader`: escanea `openspec/changes/` |
| `src/sdd_tui/core/pipeline.py` | Core | `PipelineInferer` + `TaskParser` |
| `src/sdd_tui/core/git_reader.py` | Core | `GitReader`: `git status --porcelain` |
| `src/sdd_tui/tui/app.py` | TUI | `SddTuiApp` + `main()` (entrypoint CLI) |
| `src/sdd_tui/tui/epics.py` | TUI | `EpicsView`: DataTable con pipeline por change |
| `tests/conftest.py` | Test | Fixture `openspec_dir` (tmp_path con estructura mínima) |
| `tests/test_reader.py` | Test | 3 tests del reader |
| `tests/test_pipeline.py` | Test | 7 tests de pipeline + task parser |

**Total: 11 archivos — Ideal**

## Scope

- **Total archivos:** 11 (todos nuevos)
- **Resultado:** Ideal (< 10 "reales", 11 contando `__init__.py`)

## Detalle por Módulo

### `core/models.py`

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class PhaseState(Enum):
    DONE = "done"
    PENDING = "pending"

@dataclass
class Pipeline:
    propose: PhaseState = PhaseState.PENDING
    spec:    PhaseState = PhaseState.PENDING
    design:  PhaseState = PhaseState.PENDING
    tasks:   PhaseState = PhaseState.PENDING
    apply:   PhaseState = PhaseState.PENDING
    verify:  PhaseState = PhaseState.PENDING

@dataclass
class Task:
    id: str
    description: str
    done: bool
    amendment: str | None = None

@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline

class OpenspecNotFoundError(Exception):
    pass
```

### `core/reader.py`

```python
class OpenspecReader:
    def load(self, openspec_path: Path) -> list[Change]:
        # Valida que openspec_path/changes/ existe
        # Itera subdirectorios (excluye "archive" y archivos)
        # Para cada uno: infiere Pipeline y construye Change
        # Retorna ordenado alfabéticamente
```

### `core/pipeline.py`

```python
class TaskParser:
    TASK_RE = re.compile(r"^- \[(x| )\] (T\d+) (.+)$")
    AMENDMENT_RE = re.compile(r"^── amendment: (.+) ──$")

    def parse(self, tasks_md: Path) -> list[Task]:
        # Lee líneas, extrae Task por regex TXX
        # Acumula amendment context
        # Ignora líneas que no coincidan con ningún patrón

class PipelineInferer:
    def infer(self, change_path: Path, git_reader: GitReader) -> Pipeline:
        # propose: proposal.md existe
        # spec:    specs/*/spec.md existe (glob)
        # design:  design.md existe
        # tasks:   tasks.md existe
        # apply:   tasks.md existe + no hay Task con done=False
        # verify:  apply DONE + git_reader.is_clean() is True
```

### `core/git_reader.py`

```python
class GitReader:
    def is_clean(self, cwd: Path) -> bool | None:
        # subprocess.run(["git", "status", "--porcelain"], cwd=cwd)
        # True si stdout vacío, False si hay cambios
        # None si falla (no repo, git no instalado)
```

### `tui/app.py`

```python
class SddTuiApp(App):
    def __init__(self, openspec_path: Path): ...
    def compose(self) -> ComposeResult:
        yield EpicsView(self._load_changes())

def main():
    # Detecta openspec/ desde cwd o argumento
    # Lanza SddTuiApp
```

### `tui/epics.py`

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui                                                      │
├──────────────────┬──────┬──────┬──────┬──────┬──────┬──────┤
│ change           │ prop │ spec │ des  │tasks │apply │ ver  │
├──────────────────┼──────┼──────┼──────┼──────┼──────┼──────┤
│ bootstrap        │  ✓   │  ✓   │  ✓   │  ✓   │  ·   │  ·  │
│ di-450-rates     │  ✓   │  ·   │  ·   │  ·   │  ·   │  ·  │
└──────────────────┴──────┴──────┴──────┴──────┴──────┴──────┘
  [r] refresh   [q] quit
```

```python
class EpicsView(Widget):
    # DataTable con columnas: change, propose, spec, design, tasks, apply, verify
    # ✓ para DONE, · para PENDING
    # Keybinding r → refresh (recarga desde disco)
    # Keybinding q → quit app
```

### `pyproject.toml`

```toml
[project]
name = "sdd-tui"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["textual>=0.70.0"]

[project.scripts]
sdd-tui = "sdd_tui.tui.app:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["pytest>=8.0"]
```

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_empty_changes` | `test_reader.py` | Lista vacía cuando `changes/` solo tiene `archive/` |
| `test_lists_active_changes` | `test_reader.py` | Retorna changes activos ordenados alfabéticamente |
| `test_missing_openspec_raises` | `test_reader.py` | `OpenspecNotFoundError` si no existe `openspec/` |
| `test_all_pending_when_empty` | `test_pipeline.py` | Change vacío → todas las fases PENDING |
| `test_propose_done` | `test_pipeline.py` | `proposal.md` existe → `propose=DONE` |
| `test_apply_done_all_checked` | `test_pipeline.py` | Todas las tasks `[x]` → `apply=DONE` |
| `test_apply_pending_with_unchecked` | `test_pipeline.py` | Alguna task `[ ]` → `apply=PENDING` |
| `test_parse_tasks_with_amendment` | `test_pipeline.py` | Tasks con amendment → `amendment` correcto |
| `test_parse_ignores_malformed` | `test_pipeline.py` | Líneas sin TXX se ignoran |
| `test_verify_pending_without_apply` | `test_pipeline.py` | `apply=PENDING` → `verify=PENDING` |

**Total: 10 tests mínimos**

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `PipelineInferer` + `TaskParser` en mismo módulo | Módulos separados | Acoplados por diseño, menos archivos |
| `GitReader` inyectado en `PipelineInferer.infer()` | Importado directo | Permite mock en tests sin parchear subprocess |
| Fixture `tmp_path` en conftest | Archivos reales | Tests aislados, reproducibles |
| `hatchling` como build backend | `setuptools` | Más moderno, compatible con `uv` por defecto |
| Detección automática de `openspec/` desde `cwd` | Path obligatorio como arg | UX más natural para uso cotidiano |

## Dependencias Técnicas

- **Runtime:** `textual>=0.70.0`, Python `>=3.11`, `git` CLI en PATH
- **Dev:** `pytest>=8.0`
- **Sin dependencias extra** para el core (stdlib: `pathlib`, `subprocess`, `re`, `dataclasses`)
