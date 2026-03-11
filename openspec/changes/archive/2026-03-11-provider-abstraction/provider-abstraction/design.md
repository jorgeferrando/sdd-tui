# Design: provider-abstraction

## Metadata
- **Change:** provider-abstraction
- **Jira:** N/A
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-11
- **Estado:** draft

## Resumen Técnico

Se introduce el paquete `core/providers/` con tres módulos: `protocol.py` (contratos
y dataclasses compartidos), `github.py` (implementaciones GitHub via `gh` CLI) y
`null.py` (implementaciones no-op). `core/github.py` pasa a ser un shim de
re-exportación para que todo el código existente siga funcionando sin cambios.

En `App.__init__` se instancian los singletons `_git_host` y `_issue_tracker` según
la config leída de `openspec/config.yaml`. La nueva pantalla `GitWorkflowSetupScreen`
gestiona el wizard de configuración y escribe la sección `git_workflow:` en el
archivo de config.

## Arquitectura

```
tui/app.py
  └── SddTuiApp.__init__
        ├── load_git_workflow_config(openspec_path)   → GitWorkflowConfig
        ├── make_git_host(cfg)                        → self._git_host
        └── make_issue_tracker(cfg)                   → self._issue_tracker

tui/epics.py
  └── S → push_screen(GitWorkflowSetupScreen)

tui/setup.py
  └── GitWorkflowSetupScreen
        ├── lee: load_git_workflow_config(openspec_path)
        └── escribe: _write_git_workflow_config(openspec_path, cfg)

core/providers/protocol.py
  ├── dataclasses: Issue, PrStatus, CiStatus, ReleaseInfo, PrInfo, GitWorkflowConfig
  ├── Protocols: IssueTracker, GitHost
  └── factories: make_git_host(cfg), make_issue_tracker(cfg)

core/providers/github.py
  ├── GitHubHost          (implementa GitHost)
  ├── GitHubIssueTracker  (implementa IssueTracker)
  └── get_pr_status / get_ci_status / get_releases  ← funciones module-level (compat)

core/providers/null.py
  ├── NullGitHost         (implementa GitHost — no-op)
  └── NullIssueTracker    (implementa IssueTracker — no-op)

core/github.py  ← SHIM: re-exporta desde providers/
core/reader.py  ← + load_git_workflow_config(openspec_path)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/providers/__init__.py` | Package | Re-exports públicos del paquete |
| `src/sdd_tui/core/providers/protocol.py` | Core | Protocols + dataclasses + factories |
| `src/sdd_tui/core/providers/github.py` | Core | GitHubHost + GitHubIssueTracker + compat functions |
| `src/sdd_tui/core/providers/null.py` | Core | NullGitHost + NullIssueTracker |
| `src/sdd_tui/tui/setup.py` | TUI | GitWorkflowSetupScreen (wizard) |
| `tests/test_providers_github.py` | Test | GitHubHost + GitHubIssueTracker |
| `tests/test_providers_null.py` | Test | NullGitHost + NullIssueTracker |
| `tests/test_git_workflow_config.py` | Test | load_git_workflow_config parsing |
| `tests/test_tui_setup.py` | Test | GitWorkflowSetupScreen (TUI) |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/github.py` | Reemplazar contenido por shim de re-exportación | Compatibilidad sin cambiar callers existentes |
| `src/sdd_tui/core/reader.py` | Añadir `load_git_workflow_config` + `_write_git_workflow_config` | Lectura/escritura per-proyecto de `openspec/config.yaml` |
| `src/sdd_tui/tui/app.py` | Añadir carga de config + singletons `_git_host`/`_issue_tracker` en `__init__` | Patrón singleton establecido en spec |
| `src/sdd_tui/tui/epics.py` | Añadir binding `S` → `GitWorkflowSetupScreen` | REQ-SW01/SW02 |

## Scope

- **Total archivos:** 13 (9 nuevos + 4 modificados)
- **Resultado:** Ideal

## Diseño detallado — `core/providers/protocol.py`

```python
# Dataclasses compartidos (migrados de core/github.py):
# PrStatus, CiStatus, ReleaseInfo  → idénticos a los actuales
# PrInfo  → nuevo (para create_pr)
# Issue   → nuevo
# GitWorkflowConfig → nuevo

@dataclass
class GitWorkflowConfig:
    issue_tracker: str = "none"           # "github"|"jira"|"trello"|"none"
    git_host: str = "none"                # "github"|"bitbucket"|"gitlab"|"none"
    branching_model: str = "github-flow"  # "github-flow"|"git-flow"
    change_prefix: str = "issue"
    changelog_format: str = "both"        # "labels"|"commit-prefix"|"both"

class IssueTracker(Protocol):
    def get_issues(self, state: str = "open", cwd: Path = ...) -> list[Issue]: ...
    def get_issue(self, issue_id: str, cwd: Path = ...) -> Issue | None: ...
    def create_issue(self, ...) -> Issue: ...   # NotImplementedError hasta issues-actions
    def close_issue(self, ...) -> None: ...     # NotImplementedError
    def assign_issue(self, ...) -> None: ...    # NotImplementedError

class GitHost(Protocol):
    def get_pr_status(self, branch: str, cwd: Path) -> PrStatus | None: ...
    def get_ci_status(self, branch: str, cwd: Path) -> CiStatus | None: ...
    def get_releases(self, cwd: Path) -> list[ReleaseInfo]: ...
    def create_pr(self, ...) -> PrInfo: ...     # NotImplementedError hasta pr-create-workflow
    def create_release(self, ...) -> None: ...  # NotImplementedError hasta release-tagging

def make_git_host(cfg: GitWorkflowConfig) -> GitHost:
    if cfg.git_host == "github":
        from sdd_tui.core.providers.github import GitHubHost
        return GitHubHost()
    from sdd_tui.core.providers.null import NullGitHost
    return NullGitHost()

def make_issue_tracker(cfg: GitWorkflowConfig) -> IssueTracker:
    if cfg.issue_tracker == "github":
        from sdd_tui.core.providers.github import GitHubIssueTracker
        return GitHubIssueTracker()
    from sdd_tui.core.providers.null import NullIssueTracker
    return NullIssueTracker()
```

## Diseño detallado — `core/providers/github.py`

```python
class GitHubHost:
    def get_pr_status(self, branch: str, cwd: Path) -> PrStatus | None:
        # lógica exacta de core/github.get_pr_status (migrada)
    def get_ci_status(self, branch: str, cwd: Path) -> CiStatus | None:
        # lógica exacta de core/github.get_ci_status (migrada)
    def get_releases(self, cwd: Path) -> list[ReleaseInfo]:
        # lógica exacta de core/github.get_releases (migrada)
    def create_pr(self, ...) -> PrInfo:
        raise NotImplementedError
    def create_release(self, ...) -> None:
        raise NotImplementedError

class GitHubIssueTracker:
    def get_issues(self, state: str = "open", cwd: Path = ...) -> list[Issue]:
        # gh issue list --state {state} --json number,title,body,labels,assignees,state,url
    def get_issue(self, issue_id: str, cwd: Path = ...) -> Issue | None:
        # gh issue view {id} --json ...
    def create_issue(self, ...) -> Issue:
        raise NotImplementedError
    def close_issue(self, ...) -> None:
        raise NotImplementedError
    def assign_issue(self, ...) -> None:
        raise NotImplementedError

# Module-level functions — backward compat para core/github.py shim
_default_host = GitHubHost()

def get_pr_status(branch: str, cwd: Path) -> PrStatus | None:
    return _default_host.get_pr_status(branch, cwd)

def get_ci_status(branch: str, cwd: Path) -> CiStatus | None:
    return _default_host.get_ci_status(branch, cwd)

def get_releases(cwd: Path) -> list[ReleaseInfo]:
    return _default_host.get_releases(cwd)
```

## Diseño detallado — `core/github.py` (shim)

```python
# core/github.py — shim de compatibilidad (eliminar en epic-2)
from sdd_tui.core.providers.protocol import PrStatus, CiStatus, ReleaseInfo  # noqa: F401
from sdd_tui.core.providers.github import (  # noqa: F401
    get_pr_status, get_ci_status, get_releases,
)
```

## Diseño detallado — `core/reader.py` (adición)

```python
def load_git_workflow_config(openspec_path: Path) -> GitWorkflowConfig:
    """Lee la sección git_workflow: de openspec/config.yaml."""
    config_file = openspec_path / "config.yaml"
    if not config_file.exists():
        return GitWorkflowConfig()
    try:
        return _parse_git_workflow(config_file.read_text(errors="replace"))
    except Exception:
        return GitWorkflowConfig()

def _write_git_workflow_config(openspec_path: Path, cfg: GitWorkflowConfig) -> None:
    """Escribe/reemplaza la sección git_workflow: en openspec/config.yaml."""
    # Genera el bloque YAML manualmente (patrón del proyecto — sin PyYAML)
    # Si el archivo no existe → crea con comment + sección
    # Si existe y contiene git_workflow: → reemplaza solo esa sección
    # Si existe sin git_workflow: → añade al final
```

Parsing de `git_workflow:` sigue el patrón manual de `config.py`: línea a línea con
`re.match`. Sin dependencias externas de YAML.

## Diseño detallado — `tui/setup.py` (GitWorkflowSetupScreen)

```python
_QUESTIONS = [
    {
        "key": "issue_tracker",
        "title": "¿Dónde gestionas los issues?",
        "options": [
            ("github", "GitHub Issues"),
            ("jira", "JIRA  (próximamente)", True),     # disabled=True
            ("trello", "Trello  (próximamente)", True),
            ("none", "Sin issue tracker"),
        ],
    },
    # ... 4 preguntas más
]

class GitWorkflowSetupScreen(Screen):
    BINDINGS = [("escape", "cancel", "Cancelar")]

    def __init__(self, openspec_path: Path) -> None:
        super().__init__()
        self._openspec_path = openspec_path
        self._step: int = 0
        self._answers: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Static(id="wz-progress")    # "Pregunta 1 de 5"
        yield Static(id="wz-title")       # texto de la pregunta
        yield OptionList(id="wz-options") # opciones seleccionables
        yield Input(id="wz-custom", placeholder="Escribe el prefijo...")
        # Input oculto (display:none) hasta que se selecciona "personalizado"

    def on_mount(self) -> None:
        self._render_step()

    def _render_step(self) -> None:
        # Actualiza progress, title y opciones para self._step
        # Opciones disabled se muestran con dim y no son seleccionables

    def on_option_list_option_selected(self, event) -> None:
        value = str(event.option.id)
        if "(próximamente)" in value:
            self.notify("Not yet available", severity="warning")
            return
        if value == "personalizado":
            self.query_one("#wz-custom").display = True
            self.query_one("#wz-custom").focus()
            return
        self._record_answer(value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Para el input de prefijo personalizado
        if event.value.strip():
            self._record_answer(event.value.strip())

    def _record_answer(self, value: str) -> None:
        key = _QUESTIONS[self._step]["key"]
        self._answers[key] = value
        self._step += 1
        if self._step == len(_QUESTIONS):
            self._save_and_dismiss()
        else:
            self._render_step()

    def _save_and_dismiss(self) -> None:
        cfg = GitWorkflowConfig(**self._answers)
        _write_git_workflow_config(self._openspec_path, cfg)
        self.app.notify("Git workflow configured ✓")
        self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()
```

## Diseño detallado — `tui/app.py` (adición en `__init__`)

```python
from sdd_tui.core.reader import load_git_workflow_config
from sdd_tui.core.providers.protocol import make_git_host, make_issue_tracker

def __init__(self, openspec_path: Path, config: AppConfig | None = None) -> None:
    super().__init__()
    self._openspec_path = openspec_path
    self._config = config or AppConfig()
    self._inferer = PipelineInferer()
    self._parser = TaskParser()
    self._git = GitReader()
    # Nuevo:
    _wf_cfg = load_git_workflow_config(openspec_path)
    self._git_host = make_git_host(_wf_cfg)
    self._issue_tracker = make_issue_tracker(_wf_cfg)
```

## Diseño detallado — Tests

**`test_providers_github.py`**
- Mismos 18 tests de `test_github.py` pero con path `sdd_tui.core.providers.github`
- Añadir tests de `GitHubIssueTracker.get_issues` y `get_issue`

**`test_providers_null.py`**
- Null retorna `None`/`[]`/`{}` sin excepciones
- `create_pr`, `create_issue`, etc. lanzan `NotImplementedError`

**`test_git_workflow_config.py`**
- Config completa parseada correctamente
- Config parcial → defaults para campos ausentes
- Archivo inexistente → `GitWorkflowConfig()` con defaults
- Sección `git_workflow:` ausente → defaults
- `_write_git_workflow_config`: crea archivo nuevo, reemplaza sección existente,
  añade a archivo sin sección

**`test_tui_setup.py`**
- Wizard avanza tras seleccionar opción
- Opción "próximamente" no avanza
- Esc cancela sin escribir config
- Completar las 5 preguntas escribe config correctamente
- Opción "personalizado" en step 4 muestra Input

## Patrones Aplicados

- **Singleton en App:** consistente con `self.app._git` (ya establecido)
- **Module-level compat functions:** `_default_host = GitHubHost()` en `providers/github.py`
  — misma signature que las funciones actuales de `core/github.py`
- **YAML manual parsing:** sin PyYAML — patrón establecido en `core/config.py`
- **Lazy imports en factory:** `from ... import GitHubHost` dentro del `if` evita
  importar módulos opcionales en el startup

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| PrStatus/CiStatus/ReleaseInfo se mueven a `protocol.py` | Mantener en `github.py` | Son parte del contrato, no de la implementación |
| `_default_host` module-level en `providers/github.py` | Instanciar en el shim | El shim no conoce Path — las funciones compat necesitan estado mínimo |
| `_write_git_workflow_config` en `reader.py` | Solo en `setup.py` | Simetría con `load_git_workflow_config`; testeable independientemente del TUI |
| `create_pr` / `create_issue` como `NotImplementedError` | No declararlos aún | El Protocol está completo desde el principio — las screens futuras lo pueden usar |

## Notas de Implementación

- `test_github.py` existente **no se toca** — el shim hace que sus imports sigan
  funcionando. Los nuevos tests en `test_providers_github.py` usan el path nuevo.
- Las opciones "próximamente" en el wizard se identifican por `Option.id` con
  prefijo `_disabled_` para distinguirlas sin depender del texto visible.
- El parsing manual de YAML para `git_workflow:` sigue el patrón de `_parse_config`
  en `config.py`: iterar líneas, detectar sección con `stripped == "git_workflow:"`,
  parsear pares `key: value` con regex.
