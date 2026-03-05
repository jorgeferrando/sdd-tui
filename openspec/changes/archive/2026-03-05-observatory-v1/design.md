# Design: observatory-v1 — Multi-project Support

## Metadata
- **Change:** observatory-v1
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Se añade una config global opcional `~/.sdd-tui/config.yaml` que declara
los proyectos a monitorizar. El modelo `Change` gana dos campos (`project`,
`project_path`) que permiten a la TUI agrupar y separar visualmente por proyecto.

La app sigue recibiendo `list[Change]` en todos los widgets — no hay cambio
de contrato interno. La agrupación se infiere de `change.project` en `_populate()`.
En legacy mode (sin config), `project` queda vacío y ningún separador se muestra.

## Arquitectura

```
main()
  → load_config()              ← ~/.sdd-tui/config.yaml
  → SddTuiApp(openspec_path, config)
       → _load_changes()
           → load_all_changes(config, cwd)
               legacy: OpenspecReader.load(cwd/openspec)
               multi:  OpenspecReader.load(proj/openspec) × N
           → infer pipeline + parse tasks
       → EpicsView(changes)    ← list[Change] con project set
           _populate()
               → agrupa por change.project si hay > 1 proyecto
               → inserta separadores de proyecto
       → SpecHealthScreen(changes)  ← change.project_path sustituye Path.cwd()
       → DecisionsTimeline(archive_dirs)  ← list[Path] multi-proyecto
```

## Archivos a Crear

| Archivo | Propósito |
|---------|-----------|
| `src/sdd_tui/core/config.py` | `AppConfig`, `ProjectConfig`, `load_config()` |
| `tests/test_config.py` | Tests unitarios del config loader |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/models.py` | Añadir `project: str = ""` y `project_path: Path \| None = None` a `Change` | Cada change conoce su proyecto origen |
| `src/sdd_tui/core/reader.py` | Añadir `project_path` param a `OpenspecReader.load()`; añadir `load_all_changes()` | Multi-project loading |
| `src/sdd_tui/tui/app.py` | Recibir `AppConfig`; adaptar `_load_changes()` a `load_all_changes()` | Punto de entrada multi-proyecto |
| `src/sdd_tui/tui/epics.py` | `_populate()` con separadores de proyecto; `action_decisions_timeline()` pasa `list[Path]` | View 1 multi-proyecto |
| `src/sdd_tui/tui/spec_health.py` | Separadores de proyecto en `_populate()`; `change.project_path` en lugar de `Path.cwd()` | Health multi-proyecto + fix bug path |
| `src/sdd_tui/tui/spec_evolution.py` | `DecisionsTimeline.__init__(archive_dirs: list[Path])` | Agrega decisions de todos los proyectos |
| `tests/test_reader.py` | Casos multi-project + `project`/`project_path` en Change | Cobertura de nuevas funciones |
| `tests/test_tui_epics.py` | Casos multi-project separators | Cobertura de la nueva UI |

## Scope

- **Total archivos:** 10 (2 nuevos, 8 modificados)
- **Resultado:** Evaluar (10-20) — dentro de límite, cambios localizados

## Detalles de Implementación

### `core/config.py` — sin pyyaml

La config es simple (`- path: ~/ruta`). Parser manual con regex, sin dependencias nuevas:

```python
@dataclass
class ProjectConfig:
    path: Path

@dataclass
class AppConfig:
    projects: list[ProjectConfig] = field(default_factory=list)

def load_config() -> AppConfig:
    config_path = Path.home() / ".sdd-tui" / "config.yaml"
    if not config_path.exists():
        return AppConfig()
    try:
        return _parse_config(config_path.read_text(errors="replace"))
    except Exception:
        return AppConfig()

def _parse_config(text: str) -> AppConfig:
    # Parsea solo líneas "  - path: ~/..." bajo "projects:"
    # Usa re.match para extraer el path, expande ~ y resuelve
```

### `core/models.py` — Change extendido

```python
@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline = field(default_factory=Pipeline)
    tasks: list[Task] = field(default_factory=list)
    archived: bool = False
    project: str = ""                  # basename del proyecto (e.g., "sdd-tui")
    project_path: Path | None = None   # raíz del repo git del proyecto
```

### `core/reader.py` — load_all_changes

```python
# OpenspecReader.load() acepta project_path opcional:
def load(self, openspec_path, include_archived=False, project_path=None):
    ...
    proj = project_path or openspec_path.parent
    for change in changes:
        change.project = proj.name
        change.project_path = proj
    return changes

# Nueva función de módulo:
def load_all_changes(config: AppConfig, cwd: Path, include_archived: bool = False) -> list[Change]:
    if not config.projects:
        return OpenspecReader().load(cwd / "openspec", include_archived, project_path=cwd)
    all_changes = []
    for pc in config.projects:
        try:
            all_changes.extend(
                OpenspecReader().load(pc.path / "openspec", include_archived, project_path=pc.path)
            )
        except OpenspecNotFoundError:
            pass  # skip silently
    return all_changes
```

### `tui/app.py` — main() carga config

```python
def __init__(self, openspec_path: Path, config: AppConfig | None = None) -> None:
    ...
    self._config = config or AppConfig()

def _load_changes(self, include_archived: bool = False) -> list[Change]:
    from sdd_tui.core.reader import load_all_changes
    cwd = self._openspec_path.parent
    changes = load_all_changes(self._config, cwd, include_archived)
    # infer + tasks como antes
    ...

# En main():
from sdd_tui.core.config import load_config
config = load_config()
app = SddTuiApp(openspec_path, config)
```

### `tui/epics.py` — separadores en _populate()

Detecta multi-proyecto mirando cuántos `project` distintos hay en `_changes`.
Agrupa preservando orden de aparición:

```python
def _populate(self):
    ...
    # Detectar si multi-project (solo activos, sin archived)
    active_projects = list(dict.fromkeys(c.project for c in active))
    is_multi = len(active_projects) > 1

    if is_multi:
        for project_name in active_projects:
            proj_changes = [c for c in active if c.project == project_name]
            filtered = self._filter_changes(proj_changes, self._search_query)
            # Separador de proyecto (sin key)
            table.add_row(f"─── {project_name} ───", "", "", "", "", "", "")
            if not filtered:
                table.add_row("  (no active changes)", "", "", "", "", "", "")
            else:
                for change in filtered:
                    self._add_change_row(table, change)
    else:
        # Comportamiento actual
        for change in (filtered_active):
            self._add_change_row(table, change)

    # Archived: separador global (igual que ahora)
    if archived:
        table.add_row("── archived ──", ...)
```

`action_decisions_timeline()` construye la lista de archive_dirs desde los proyectos:

```python
def action_decisions_timeline(self) -> None:
    seen, dirs = set(), []
    for change in self._changes:
        if change.project_path and change.project_path not in seen:
            seen.add(change.project_path)
            dirs.append(change.project_path / "openspec" / "changes" / "archive")
    if not dirs:
        dirs = [self.app._openspec_path / "changes" / "archive"]
    self.app.push_screen(DecisionsTimeline(dirs))
```

### `tui/spec_health.py` — project_path + separadores

```python
# Fix: usar change.project_path en lugar de Path.cwd()
all_metrics = {
    c.name: parse_metrics(c.path, c.project_path or Path.cwd())
    for c in visible
}

# Separadores de proyecto (mismo patrón que epics.py)
active_projects = list(dict.fromkeys(c.project for c in active))
is_multi = len(active_projects) > 1
if is_multi:
    for project_name in active_projects:
        table.add_row("─── {project_name} ───", "", "", "", "", "")  # sin key
        for change in proj_changes:
            self._add_row(...)
else:
    # comportamiento actual
```

### `tui/spec_evolution.py` — DecisionsTimeline multi-archive

```python
class DecisionsTimeline(Screen):
    def __init__(self, archive_dirs: list[Path]) -> None:
        super().__init__()
        self._archive_dirs = archive_dirs

    def _populate(self) -> None:
        # Aggregate + sort by date
        from itertools import chain
        all_decisions = sorted(
            chain.from_iterable(
                collect_archived_decisions(d) for d in self._archive_dirs
            ),
            key=lambda cd: cd.archive_date,
        )
        with_decisions = [cd for cd in all_decisions if cd.decisions]
        ...
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Parser YAML manual (regex) | pyyaml como dependencia | Formato simple y fijo — evita nueva dependencia |
| `change.project` vacío en legacy | `project = cwd.name` siempre | `is_multi` basado en `len(projects) > 1` — si solo hay un proyecto no hay separadores |
| `EpicsView` sigue recibiendo `list[Change]` | `list[tuple[str, list[Change]]]` | Contrato mínimo — la agrupación se infiere del campo `project` |
| `is_multi` en `_populate()` | Flag persistente en `__init__` | Más simple; se recalcula en cada populate (trivial) |
| `DecisionsTimeline` recibe `list[Path]` | `list[Change]` | DecisionsTimeline necesita el archive dir, no los changes activos |
| `project_path` en `Change` | Derivar del `path` en runtime | Explícito y testable; evita `path.parent.parent.parent` frágil |

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_load_config_no_file` | `test_config.py` | Sin config → `AppConfig(projects=[])` |
| `test_load_config_with_projects` | `test_config.py` | Parsea paths correctamente |
| `test_load_config_malformed` | `test_config.py` | YAML roto → `AppConfig(projects=[])` |
| `test_load_config_expands_tilde` | `test_config.py` | `~/sites/x` → absoluto |
| `test_load_all_changes_legacy` | `test_reader.py` | Config vacía usa cwd |
| `test_load_all_changes_multi` | `test_reader.py` | Agrega de N proyectos |
| `test_load_all_changes_skips_missing` | `test_reader.py` | Path sin openspec/ → skip |
| `test_change_has_project_fields` | `test_reader.py` | `project` y `project_path` correctos |
| `test_epics_multi_project_separators` | `test_tui_epics.py` | Separadores visibles en multi-proyecto |
| `test_epics_single_project_no_separators` | `test_tui_epics.py` | Sin separadores en legacy |

## Notas de Implementación

- `load_all_changes` con config vacía debe ser **exactamente equivalente** al comportamiento actual — misma llamada a `OpenspecReader.load()`.
- La fila `(no active changes)` para proyectos sin changes solo aparece en modo multi-proyecto (si hay separadores activos).
- `SpecHealthScreen` ya recibe `list[Change]` con `project` field — puede agrupar sin cambio de interfaz.
- El test de `DecisionsTimeline` existente pasa `archive_dir: Path` — hay que actualizar la firma a `list[Path]` y actualizar los tests existentes.
