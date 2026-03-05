# Spec: Git — Local Git Info

## Metadata
- **Dominio:** git
- **Change:** git-local-info
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** approved

## Contexto

La TUI expone información básica de git (diff por tarea, estado del working tree,
PR status vía `gh`). Este cambio añade información git local visible directamente
en la UI: rama activa, log de commits del change con autoría, y detalle del
working tree cuando hay cambios sin commitear.

No requiere red ni `gh` — solo `git` en PATH.

## Comportamiento Actual

- `GitReader.find_commit()` — busca el commit de una tarea por fragment del mensaje
- `GitReader.get_diff()` — diff de un commit específico
- `GitReader.get_working_diff()` — `git diff HEAD`
- `GitReader.is_clean()` — comprueba si el working tree está limpio
- La rama activa no se muestra en ninguna vista
- No hay vista de log de commits del change

## Requisitos (EARS)

### Rama activa

- **REQ-BR01** `[Event]` When the app mounts, the TUI SHALL read the current git branch
  using `git branch --show-current` and display it in `app.sub_title`.

- **REQ-BR02** `[Event]` When the user triggers a refresh (`r`), the TUI SHALL re-read
  the current branch and update `app.sub_title`.

- **REQ-BR03** `[Unwanted]` If `git` is not in PATH or the directory is not a git repo,
  `app.sub_title` SHALL display an empty string (no error shown).

- **REQ-BR04** `[Ubiquitous]` The branch SHALL NOT update automatically while the app is
  running — only on mount and explicit refresh.

### GitLogScreen

- **REQ-GL01** `[Event]` When the user presses `G` in View 2 (ChangeDetailScreen),
  the app SHALL push `GitLogScreen` for the current change.

- **REQ-GL02** `[Ubiquitous]` `GitLogScreen` SHALL show up to 50 commits whose message
  contains `[change-name]`, obtained via `git log --grep=[change-name] -F --max-count=50`.

- **REQ-GL03** `[Ubiquitous]` Each row in `GitLogScreen` SHALL show: abbreviated hash (7 chars),
  author name, relative date, and commit message (one line).

- **REQ-GL04** `[Event]` When the user highlights a row in `GitLogScreen`, the diff panel
  SHALL update with the diff of that commit (`git show --no-color <hash>`).

- **REQ-GL05** `[Ubiquitous]` `GitLogScreen` SHALL use a split layout: commit list on top,
  diff panel below — matching the visual pattern of `ChangeDetailScreen`.

- **REQ-GL06** `[Unwanted]` If no commits are found for the change, `GitLogScreen` SHALL
  display "No commits found for [change-name]" in the list panel and an empty diff panel.

- **REQ-GL07** `[Event]` When the user presses `Esc` in `GitLogScreen`, the app SHALL
  pop back to `ChangeDetailScreen`.

- **REQ-GL08** `[Ubiquitous]` `GitLogScreen` SHALL support `j`/`k` bindings for scrolling
  the diff panel (consistent with other viewers).

### Working Tree Detail

- **REQ-WT01** `[Event]` When a task has no commit and `git diff HEAD` is non-empty,
  the DiffPanel in `ChangeDetailScreen` SHALL prepend a header with the output of
  `git status --short` before the diff content.

- **REQ-WT02** `[Ubiquitous]` The `git status --short` header SHALL be visually separated
  from the diff (e.g., a blank line or a `──` separator line).

- **REQ-WT03** `[Unwanted]` If `git status --short` returns no output but `git diff HEAD`
  is non-empty (staged changes), the header SHALL show "Staged changes:" instead.

### GitReader — nuevos métodos

- **REQ-GR01** `[Ubiquitous]` `GitReader.get_branch(cwd)` SHALL return the current branch
  name as a string, or `None` if git is unavailable or the directory is not a repo.

- **REQ-GR02** `[Ubiquitous]` `GitReader.get_change_log(change_name, cwd, limit=50)` SHALL
  return a list of `CommitInfo` objects matching `[change-name]` in the commit message,
  ordered from most recent to oldest.

- **REQ-GR03** `[Ubiquitous]` `CommitInfo` SHALL be extended with optional `author: str | None`
  and `date_relative: str | None` fields.

- **REQ-GR04** `[Ubiquitous]` `GitReader.get_status_short(cwd)` SHALL return the output of
  `git status --short` as a string, or `None` if unavailable or empty.

## Escenarios de Verificación

**REQ-GL06 — sin commits**
**Dado** un change `mi-feature` sin ningún commit con `[mi-feature]` en el mensaje
**Cuando** el usuario pulsa `G` en View 2
**Entonces** `GitLogScreen` muestra "No commits found for [mi-feature]"
**Y** el diff panel está vacío

**REQ-WT01 — working tree con cambios**
**Dado** una tarea sin commit y `git diff HEAD` con contenido
**Cuando** el usuario navega a esa tarea en View 2
**Entonces** el DiffPanel muestra primero los archivos modificados (`git status --short`)
**Y** luego el diff completo

**REQ-BR01 — rama en subtítulo**
**Dado** que la app se abre en un repo en la rama `main`
**Cuando** View 1 se monta
**Entonces** `app.sub_title` muestra `"main"`

## Interfaces / Contratos

### `CommitInfo` (extendido)

```python
@dataclass
class CommitInfo:
    hash: str
    message: str
    author: str | None = None
    date_relative: str | None = None
```

### `GitReader` — nuevos métodos

```python
def get_branch(self, cwd: Path) -> str | None: ...
def get_change_log(self, change_name: str, cwd: Path, limit: int = 50) -> list[CommitInfo]: ...
def get_status_short(self, cwd: Path) -> str | None: ...
```

### GitLogScreen — layout

```
┌─ GitLogScreen: {change-name} ──────────────────────┐
│  HASH     AUTHOR   DATE      MESSAGE                 │
│ > a1b2c3  Jorge    2d ago    [git] Add branch info   │
│   d4e5f6  Jorge    5d ago    [git] Init git reader   │
├─────────────────────────────────────────────────────┤
│  diff --git a/src/sdd_tui/core/git_reader.py        │
│  +++ b/src/sdd_tui/core/git_reader.py               │
│  + def get_branch(...): ...                          │
└─────────────────────────────────────────────────────┘
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Panel dividido en GitLogScreen | Pantalla separada para el diff | Menos pasos; el usuario ve el diff sin perder el contexto del log |
| Solo al montar/refresh | Polling periódico de la rama | Polling añade complejidad y consumo; la rama rara vez cambia |
| Límite 50 commits | Sin límite | Suficiente para cualquier change SDD; evita lentitud en repos grandes |
| `app.sub_title` para la rama | Columna en View 1 | `sub_title` ya existe y es el lugar natural para contexto global |

## Abierto / Pendiente

_(ninguno)_
