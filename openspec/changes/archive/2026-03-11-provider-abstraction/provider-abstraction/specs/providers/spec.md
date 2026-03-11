# Spec: Providers — provider-abstraction

## Metadata
- **Dominio:** providers
- **Change:** provider-abstraction
- **Jira:** N/A
- **Fecha:** 2026-03-11
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Nuevo dominio. Define el modelo de abstracción de providers para issue tracking y
hosting git. Permite que la TUI trabaje con GitHub hoy y con JIRA/Trello/Bitbucket
mañana sin cambiar código de presentación ni de dominio.

Los providers se instancian una vez en `App` y se pasan como atributos
(`self._git_host`, `self._issue_tracker`). Las screens los leen igual que hoy con
`self.app._git`.

## Requisitos (EARS)

### Protocols

- **REQ-PR01** `[Ubiquitous]` The system SHALL define `IssueTracker` and `GitHost`
  as `Protocol` classes (Python `typing.Protocol`). No concrete class SHALL inherit
  from them explicitly.

- **REQ-PR02** `[Ubiquitous]` `IssueTracker` SHALL declare the following methods:
  `get_issues(state)`, `get_issue(id)`, `create_issue(title, body, labels)`,
  `close_issue(id)`, `assign_issue(id, assignee)`.

- **REQ-PR03** `[Ubiquitous]` `GitHost` SHALL declare the following methods:
  `get_pr_status(branch, cwd)`, `get_ci_status(branch, cwd)`, `get_releases(cwd)`,
  `create_pr(title, body, base, draft, cwd)`, `create_release(tag, name, body, draft, cwd)`.

### GitHubHost

- **REQ-GH01** `[Event]` When `GitHubHost.get_pr_status(branch, cwd)` is called,
  the system SHALL invoke `gh pr list --head {branch}` and return `PrStatus | None`.
  Behavior identical to the current `core/github.get_pr_status`.

- **REQ-GH02** `[Event]` When `GitHubHost.get_ci_status(branch, cwd)` is called,
  the system SHALL invoke `gh run list --branch {branch} --limit 1` and return
  `CiStatus | None`. Behavior identical to the current `core/github.get_ci_status`.

- **REQ-GH03** `[Event]` When `GitHubHost.get_releases(cwd)` is called, the system
  SHALL invoke `gh release list --json tagName,name,publishedAt,isLatest` and return
  `list[ReleaseInfo]`. Behavior identical to `core/github.get_releases`.

- **REQ-GH04** `[Unwanted]` If `gh` is not found or any `gh` command fails, all
  `GitHubHost` methods SHALL return `None` or empty list without raising exceptions.

- **REQ-GH05** `[Ubiquitous]` `GitHubHost.create_pr` and `GitHubHost.create_release`
  SHALL be defined in the interface but raise `NotImplementedError` in this change.
  They will be implemented in `pr-create-workflow` and `release-tagging`.

### GitHubIssueTracker

- **REQ-GI01** `[Event]` When `GitHubIssueTracker.get_issues(state, cwd)` is called,
  the system SHALL invoke `gh issue list --state {state} --json number,title,body,
  labels,assignees,state,url` and return `list[Issue]`.

- **REQ-GI02** `[Unwanted]` If `gh` is not found or the command fails,
  `get_issues` SHALL return an empty list without raising exceptions.

- **REQ-GI03** `[Ubiquitous]` `create_issue`, `close_issue` and `assign_issue`
  SHALL be defined in the interface but raise `NotImplementedError` in this change.
  They will be implemented in `issues-actions`.

### NullProvider

- **REQ-NL01** `[Ubiquitous]` `NullIssueTracker` SHALL implement all `IssueTracker`
  methods returning empty collections or `None` without raising exceptions.

- **REQ-NL02** `[Ubiquitous]` `NullGitHost` SHALL implement all `GitHost` methods
  returning `None` or empty collections without raising exceptions.

- **REQ-NL03** `[Ubiquitous]` `NullIssueTracker` and `NullGitHost` SHALL be used
  when `issue_tracker: none` or `git_host: none` is configured, and also when the
  required CLI (`gh`) is not installed regardless of config.

### Compatibilidad con `core/github.py`

- **REQ-CM01** `[Ubiquitous]` `core/github.py` SHALL re-export `PrStatus`,
  `CiStatus`, `ReleaseInfo`, `get_pr_status`, `get_ci_status`, `get_releases`
  from `core/providers/github.py` so that all existing imports continue to work
  unchanged without any modification to callers.

### GitWorkflowConfig

- **REQ-WC01** `[Event]` When `load_git_workflow_config(openspec_path)` is called
  and `openspec/config.yaml` contains a `git_workflow:` section, the system SHALL
  return a `GitWorkflowConfig` populated with the parsed values.

- **REQ-WC02** `[Unwanted]` If `openspec/config.yaml` does not exist or has no
  `git_workflow:` section, `load_git_workflow_config` SHALL return
  `GitWorkflowConfig()` with all default values. It SHALL NOT raise exceptions.

- **REQ-WC03** `[Ubiquitous]` Default values for `GitWorkflowConfig` SHALL be:
  `issue_tracker="none"`, `git_host="none"`, `branching_model="github-flow"`,
  `change_prefix="issue"`, `changelog_format="both"`.

- **REQ-WC04** `[Event]` When `App` initializes, the system SHALL call
  `load_git_workflow_config(openspec_path)` and instantiate the appropriate
  provider singletons, assigning them to `app._git_host` and
  `app._issue_tracker`.

### Escenarios de verificación

**REQ-CM01** — shim de compatibilidad
**Dado** código existente con `from sdd_tui.core.github import get_pr_status`
**Cuando** se importa el módulo tras el refactor
**Entonces** el import funciona sin errores y `get_pr_status` es la misma función

**REQ-WC04** — provider selection en App init
**Dado** `openspec/config.yaml` con `git_host: github`
**Cuando** `App` inicializa
**Entonces** `app._git_host` es una instancia de `GitHubHost`

**REQ-WC04** — NullProvider fallback
**Dado** `openspec/config.yaml` con `git_host: none`
**Cuando** `App` inicializa
**Entonces** `app._git_host` es una instancia de `NullGitHost`

## Interfaces / Contratos

### Issue dataclass

```python
@dataclass
class Issue:
    id: str            # número como string (ej: "42") o key JIRA ("PROJ-123")
    title: str
    body: str
    labels: list[str]
    assignee: str | None
    state: str         # "open" | "closed"
    url: str
```

### GitWorkflowConfig dataclass

```python
@dataclass
class GitWorkflowConfig:
    issue_tracker: str = "none"           # "github" | "jira" | "trello" | "none"
    git_host: str = "none"                # "github" | "bitbucket" | "gitlab" | "none"
    branching_model: str = "github-flow"  # "github-flow" | "git-flow"
    change_prefix: str = "issue"          # cualquier string, incluyendo ""
    changelog_format: str = "both"        # "labels" | "commit-prefix" | "both"
```

### Factory en App

```python
# core/providers/protocol.py
def make_git_host(cfg: GitWorkflowConfig) -> GitHost: ...
def make_issue_tracker(cfg: GitWorkflowConfig) -> IssueTracker: ...
```

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|------------|--------|
| `typing.Protocol` (structural subtyping) | ABC + herencia explícita | Sin acoplamiento en implementaciones; mocks en tests sin herencia |
| Singletons en App | Instancia por llamada | Consistente con el patrón existente `self.app._git`; evita instancias repetidas |
| Shim en `core/github.py` | Actualizar todos los imports | Cero riesgo de regresión; eliminable en epic-2 |
| `load_git_workflow_config` en `core/reader.py` | En `core/config.py` | `config.py` lee config global; reader.py ya lee per-proyecto |
| `create_pr` / `create_issue` con `NotImplementedError` | No declararlos aún | Establece el contrato completo del Protocol desde el inicio |

## Abierto / Pendiente

- La integración de JIRA, Trello, Bitbucket y GitLab se implementa en epic-2.
  Sus entradas en el wizard serán visibles pero no seleccionables en este change.
