# Design: git-local-info

## Metadata
- **Change:** git-local-info
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Tres mejoras ortogonales que comparten la misma capa de datos (`GitReader`):

1. **Rama activa:** `GitReader.get_branch()` → `app.sub_title` en mount y refresh.
2. **GitLogScreen:** nueva pantalla con el mismo split layout que `ChangeDetailScreen`
   (DataTable arriba + DiffPanel abajo), diff cargado async via `@work(thread=True, exclusive=True)`.
3. **Working tree header:** en `_load_diff_worker`, cuando la tarea no tiene commit,
   se antepone `git status --short` al diff como bloque de comentario (`# líneas`).

`CommitInfo` se extiende con campos opcionales `author` y `date_relative` para no romper
ningún uso existente (todos los constructores actuales usan keyword args o solo `hash`+`message`).

## Arquitectura

```
app.py (on_mount / refresh)
  → GitReader.get_branch(cwd) → app.sub_title

ChangeDetailScreen
  → Binding "G" → action_git_log()
      → push GitLogScreen(change)

GitLogScreen
  ├─ CommitListPanel (DataTable)
  │     git log --grep=[change-name] -F --max-count=50
  │     columnas: hash | author | date | message
  └─ DiffPanel (reutilizado de change_detail)
        on_data_table_row_highlighted → @work → git show <hash>

_load_diff_worker (tarea sin commit)
  → GitReader.get_working_diff()   → diff content
  → GitReader.get_status_short()   → archivos modificados
  → concatena: "# Modified:\n# M file.py\n#\n<diff>"
  → DiffPanel.show_diff(combined)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/tui/git_log.py` | Screen | `GitLogScreen` + `CommitListPanel` |
| `tests/test_tui_git_log.py` | Tests | Cobertura de `GitLogScreen` |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/models.py` | Añadir `author`, `date_relative` a `CommitInfo` | REQ-GR03 |
| `src/sdd_tui/core/git_reader.py` | Añadir `get_branch()`, `get_change_log()`, `get_status_short()` | REQ-GR01–04 |
| `src/sdd_tui/tui/change_detail.py` | Binding `G` + working tree header en `_load_diff_worker` | REQ-GL01, REQ-WT01–03 |
| `src/sdd_tui/tui/app.py` | Leer branch en mount + refresh, asignar a `sub_title` | REQ-BR01–04 |
| `tests/test_git_reader.py` | Tests para los 3 nuevos métodos | Cobertura REQ-GR01–04 |

## Scope

- **Total archivos:** 7
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Sin nuevas dependencias de runtime
- `DiffPanel` se reutiliza sin modificaciones — ya expone `show_diff()` y `show_message()`
- `@work(thread=True, exclusive=True)` + `self.app.call_from_thread` ya disponible (patrón de `perf-async-diffs`)

## Detalle de Implementación

### `models.py` — CommitInfo extendido

```python
@dataclass
class CommitInfo:
    hash: str
    message: str
    author: str | None = None          # nuevo — opcional
    date_relative: str | None = None   # nuevo — opcional
```

Los usos existentes (`CommitInfo(hash=x, message=y)`) no se rompen.

### `git_reader.py` — nuevos métodos

```python
def get_branch(self, cwd: Path) -> str | None:
    # git branch --show-current
    # Retorna "" si detached HEAD, None si error/no repo

def get_change_log(self, change_name: str, cwd: Path, limit: int = 50) -> list[CommitInfo]:
    # git log -F --grep=[{change_name}] --max-count={limit}
    #          --format="%h\x1f%an\x1f%ar\x1f%s"
    # Parsea con split("\x1f") → CommitInfo(hash, message, author, date_relative)
    # \x1f = ASCII unit separator — no aparece en mensajes de commit

def get_status_short(self, cwd: Path) -> str | None:
    # git status --short --porcelain
    # Retorna None si vacío o error
```

### `git_log.py` — estructura

```python
class CommitListPanel(Widget):
    # DataTable: columnas hash(7) | author | date | message
    # cursor_type="row"

class GitLogScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("j", "scroll_down", "Scroll down"),
        Binding("k", "scroll_up", "Scroll up"),
    ]

    def __init__(self, change: Change): ...
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield CommitListPanel(commits)
            yield DiffPanel()
        yield Footer()

    def on_mount(self):
        # load commits via get_change_log()
        # auto-highlight first row → dispara diff load

    def on_data_table_row_highlighted(self, event):
        self._load_diff_worker(commit_hash)

    @work(thread=True, exclusive=True)
    def _load_diff_worker(self, commit_hash: str): ...

    def action_scroll_down(self):
        self.query_one(DiffPanel).scroll_down()

    def action_scroll_up(self):
        self.query_one(DiffPanel).scroll_up()
```

### `change_detail.py` — cambios

```python
# Añadir binding
Binding("g", "git_log", "Git log")

# Nuevo action
def action_git_log(self) -> None:
    self.app.push_screen(GitLogScreen(self._change))

# Modificar _load_diff_worker (rama sin commit)
diff = GitReader().get_working_diff(Path.cwd())
status = GitReader().get_status_short(Path.cwd())
if diff:
    if status:
        header = "# Modified files:\n" + "\n".join(f"# {l}" for l in status.splitlines()) + "\n#\n"
    else:
        header = "# Staged changes:\n#\n"
    combined = header + diff
    self.app.call_from_thread(self._update_diff_panel, combined, True)
```

### `app.py` — rama en sub_title

```python
def on_mount(self) -> None:
    self._refresh_branch()
    # ... resto del on_mount existente

def _refresh_branch(self) -> None:
    branch = GitReader().get_branch(self._openspec_path.parent)
    self.sub_title = branch or ""

# En action_refresh (si existe) o donde se refresca la lista:
self._refresh_branch()
```

## Patrones Aplicados

- **Split layout (DataTable + DiffPanel):** igual que `ChangeDetailScreen` — reutiliza `DiffPanel` directamente
- **Worker async:** `@work(thread=True, exclusive=True)` + `self.app.call_from_thread` — igual que `_load_diff_worker` en `ChangeDetailScreen`
- **`app.sub_title`:** patrón existente en el proyecto para estado transitorio de UI (ya documentado en MEMORY)
- **`\x1f` como separador en `--format`:** evita colisiones con contenido del commit

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Status header como `# comentario` en el diff | Widget Static separado encima de DiffPanel | No requiere modificar DiffPanel; el syntax highlighter lo trata como comentario |
| `get_change_log` con `\x1f` separator | Parsear `--oneline` + llamadas separadas | Una sola llamada `git log`; `\x1f` no aparece en mensajes reales |
| `CommitInfo.author` y `date_relative` opcionales | Nuevo dataclass `CommitLogEntry` | Evita duplicar estructura; backward-compatible |
| Branch leída sincrónicamente en mount | Worker async | `git branch --show-current` es instantáneo; no justifica la complejidad de un worker |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_get_branch_returns_current` | Unit | Retorna nombre de rama desde repo real/mock |
| `test_get_branch_returns_none_if_no_git` | Unit | FileNotFoundError → None |
| `test_get_change_log_returns_commits` | Unit | Parsea formato `\x1f` correctamente |
| `test_get_change_log_empty_when_no_match` | Unit | Sin commits → lista vacía |
| `test_get_status_short_returns_files` | Unit | Retorna líneas de archivos modificados |
| `test_get_status_short_returns_none_when_clean` | Unit | Working tree limpio → None |
| `test_git_log_screen_mounts` | TUI | Screen monta sin errores |
| `test_git_log_screen_no_commits` | TUI | Muestra mensaje "No commits found" |

## Notas de Implementación

- `git branch --show-current` requiere git 2.22+ — si retorna vacío (detached HEAD), tratar como `None`
- `DiffPanel` está en `change_detail.py` — importarlo en `git_log.py` desde ahí
- El primer commit en `CommitListPanel` debe auto-seleccionarse al montar (call_after_refresh + focus + move_cursor)
- `app.py` expone `refresh_changes()` — añadir `_refresh_branch()` al mismo método para mantener consistencia
