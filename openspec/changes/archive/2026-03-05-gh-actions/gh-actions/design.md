# Design: gh-actions

## Metadata
- **Change:** gh-actions
- **Jira:** N/A
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Tres extensiones independientes sobre la integración GitHub existente (`core/github.py`
+ `tui/change_detail.py`). CI status sigue el patrón exacto de PR status: sentinel
`_CI_LOADING`, worker `@work(thread=True)`, `call_from_thread` para actualizar
`PipelinePanel`. Ship binding reutiliza `copy_to_clipboard` ya disponible en la app.
`ReleasesScreen` es una pantalla nueva mínima, sin diff panel.

## Arquitectura

```
github.py
  CiStatus / get_ci_status(branch, cwd)     ← nuevo
  ReleaseInfo / get_releases(cwd)           ← nuevo

change_detail.py
  _CI_LOADING (sentinel)                    ← nuevo
  PipelinePanel(ci_status=_CI_LOADING)      ← extendido
    update_ci(ci_status)
    _build_ci_line(ci_status)
  ChangeDetailScreen
    _load_ci_status_worker()                ← nuevo worker
    action_ship_pr()                        ← nuevo

epics.py
  Binding("l", "releases", "Releases")      ← nuevo
  action_releases()                         ← nuevo

releases.py (nuevo)
  ReleasesScreen
    on_mount → get_releases() → DataTable
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/tui/releases.py` | Screen | ReleasesScreen con lista de releases |
| `tests/test_tui_releases.py` | Tests | Cobertura de ReleasesScreen |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/github.py` | Añadir `CiStatus`, `ReleaseInfo`, `get_ci_status()`, `get_releases()` | Nuevas funciones de integración GitHub |
| `src/sdd_tui/tui/change_detail.py` | `_CI_LOADING` sentinel, extender `PipelinePanel`, worker CI, binding `W` + `action_ship_pr` | CI status + ship |
| `src/sdd_tui/tui/epics.py` | Binding `l` + `action_releases()` | Acceso a ReleasesScreen |
| `tests/test_github.py` | Tests para `get_ci_status` y `get_releases` | Cobertura nuevas funciones |
| `tests/test_tui_change_detail.py` | Tests CI status en PipelinePanel + ship binding | Cobertura nuevas features |

## Scope

- **Total archivos:** 7
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- `gh` CLI — opcional en todos los casos (graceful degradation a "—" / lista vacía)
- `GitReader.get_branch()` — disponible desde `git-local-info`
- `app.copy_to_clipboard()` — disponible desde `view-5-clipboard`

## Patrones Aplicados

- **Sentinel + async worker** (`_CI_LOADING`): igual que `_PR_LOADING` en PR status.
  El worker corre en thread, llama `call_from_thread` para actualizar UI.
- **Unit tests de PipelinePanel sin TUI**: instanciar `PipelinePanel` directamente
  y verificar `_text` (patrón ya establecido en `test_tui_change_detail.py`).
- **`patch("sdd_tui.core.github.subprocess.run")`**: patrón de `test_github.py` —
  mockear `subprocess.run` con `_mock_result(returncode, stdout)`.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Branch obtenida en el worker CI (no en `on_mount`) | Obtener branch en `on_mount` y pasar al worker | Worker es thread-safe; evita estado compartido |
| `_build_ci_line` separado de `_build_pr_line` | Fusionarlos | Simetría con el método de PR; más fácil de testear por separado |
| Ship extrae descripción de `## Descripción` en `proposal.md` | Usar nombre del change | Genera un título útil sin necesitar que el usuario lo escriba |
| `l` (minúscula) para Releases en EpicsView | `L` mayúscula | Los bindings existentes usan mayúscula solo para `V` (Velocity); `l` está libre |

## Detalle de Implementación

### github.py — CiStatus + get_ci_status

```python
@dataclass
class CiStatus:
    workflow: str
    status: str          # "queued" | "in_progress" | "completed"
    conclusion: str | None  # "success" | "failure" | "cancelled" | None

def get_ci_status(branch: str, cwd: Path) -> CiStatus | None:
    # gh run list --branch {branch} --limit 1
    #   --json status,conclusion,workflowName
    # retorna None si gh ausente, error, o lista vacía
```

### github.py — ReleaseInfo + get_releases

```python
@dataclass
class ReleaseInfo:
    tag_name: str
    name: str
    published_at: str
    is_latest: bool

def get_releases(cwd: Path) -> list[ReleaseInfo]:
    # gh release list --json tagName,name,publishedAt,isLatest
    # retorna [] si gh ausente o error
```

### change_detail.py — CI en PipelinePanel

```python
_CI_LOADING = object()  # sentinel

class PipelinePanel(Static):
    def __init__(self, pipeline, tasks, metrics=None,
                 pr_status=_PR_LOADING, ci_status=_CI_LOADING):
        ...

    def update_ci(self, ci_status: CiStatus | None) -> None:
        self._ci_status = ci_status
        self._text = self._build_content(...)
        self.update(self._text)

    def _build_ci_line(self, ci_status) -> str:
        if ci_status is _CI_LOADING: return "  …    CI"
        if ci_status is None:        return "  —    CI"
        if ci_status.status != "completed": return "  ⟳    CI"
        if ci_status.conclusion == "success": return "  ✓    CI"
        return "  ✗    CI"
```

### change_detail.py — worker CI

```python
@work(thread=True)
def _load_ci_status_worker(self) -> None:
    from sdd_tui.core.github import get_ci_status
    cwd = self._change.project_path or Path.cwd()
    branch = GitReader().get_branch(cwd)
    ci = get_ci_status(branch, cwd) if branch else None
    self.app.call_from_thread(
        lambda s=ci: self.query_one(PipelinePanel).update_ci(s)
    )
```

### change_detail.py — ship binding

```python
Binding("shift+w", "ship_pr", "Ship PR")  # o "W" según Textual

def action_ship_pr(self) -> None:
    desc = self._extract_proposal_description()
    title = f"[{self._change.name}] {desc}".strip() if desc else f"[{self._change.name}]"
    cmd = f'gh pr create --title "{title}" --body ""'
    self.app.copy_to_clipboard(cmd)
    self.notify(f"Copied: {cmd}")

def _extract_proposal_description(self) -> str:
    # Lee ## Descripción de proposal.md, retorna primera línea no vacía
    proposal = self._change.path / "proposal.md"
    if not proposal.exists(): return ""
    ...
```

### releases.py — ReleasesScreen

```python
class ReleasesScreen(Screen):
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def compose(self):
        yield Header()
        yield DataTable(cursor_type="row", show_header=True)
        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("TAG", "NAME", "DATE", "LATEST")
        releases = get_releases(Path.cwd())
        if not releases:
            table.add_row("", "No releases found", "", "")
            return
        for r in releases:
            table.add_row(r.tag_name, r.name, r.published_at[:10], "✓" if r.is_latest else "·")
```

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_get_ci_status_returns_none_when_gh_missing` | `test_github.py` | FileNotFoundError → None |
| `test_get_ci_status_returns_none_on_empty_list` | `test_github.py` | Lista vacía → None |
| `test_get_ci_status_success` | `test_github.py` | completed+success → CiStatus correcto |
| `test_get_ci_status_failure` | `test_github.py` | completed+failure → CiStatus correcto |
| `test_get_ci_status_in_progress` | `test_github.py` | in_progress → CiStatus correcto |
| `test_get_releases_returns_empty_on_error` | `test_github.py` | FileNotFoundError → [] |
| `test_get_releases_returns_list` | `test_github.py` | JSON válido → lista ReleaseInfo |
| `test_pipeline_panel_ci_loading` | `test_tui_change_detail.py` | sentinel → "… CI" |
| `test_pipeline_panel_ci_none` | `test_tui_change_detail.py` | None → "— CI" |
| `test_pipeline_panel_ci_success` | `test_tui_change_detail.py` | success → "✓ CI" |
| `test_pipeline_panel_ci_failure` | `test_tui_change_detail.py` | failure → "✗ CI" |
| `test_pipeline_panel_ci_in_progress` | `test_tui_change_detail.py` | in_progress → "⟳ CI" |
| `test_ship_binding_copies_command` | `test_tui_change_detail.py` | W → clipboard + notify |
| `test_releases_screen_mounts` | `test_tui_releases.py` | Monta sin errores con lista vacía |
| `test_releases_screen_no_releases_message` | `test_tui_releases.py` | "No releases found" en tabla |
| `test_releases_screen_shows_releases` | `test_tui_releases.py` | Releases en DataTable |
| `test_releases_screen_esc_returns` | `test_tui_releases.py` | Esc → EpicsView |
