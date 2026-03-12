# Providers Reference

The providers domain defines the abstractions that connect sdd-tui to external services — currently GitHub and optional issue trackers. It uses `typing.Protocol` for structural subtyping: `GitHost` wraps `gh` CLI calls for PR status, CI status, and releases; `IssueTracker` wraps issue list/create/close operations. Both protocols have a `Null*` implementation that returns safe empty values when no integration is configured, and a `GitHub*` implementation backed by the `gh` CLI. Which implementation is active is controlled by `openspec/config.yaml` (`git_host:`, `issue_tracker:`) and can be set interactively via the `S` key in EpicsView, which opens the `GitWorkflowSetupScreen` wizard.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-PR01` | Ubiquitous | The system SHALL define `IssueTracker` and `GitHost` as `Protocol` classes (`typing.Protocol`). No concrete class SHALL inherit from them explicitly. |
| `REQ-PR02` | Ubiquitous | `IssueTracker` SHALL declare: `get_issues(state)`, `get_issue(id)`, `create_issue(title, body)`, `close_issue(id)`, `assign_issue(id, assignee)`. |
| `REQ-PR03` | Ubiquitous | `GitHost` SHALL declare: `get_pr_status(branch, cwd)`, `get_ci_status(branch, cwd)`, `get_releases(cwd)`, `create_pr(title, body, cwd)`, `create_release(tag, name, cwd)`. |
| `REQ-GH01` | Event | When `GitHubHost.get_pr_status(branch, cwd)` is called, the system SHALL invoke `gh pr list` and return `PrStatus \| None`. Behavior identical to the former `core/github.get_pr_status`. |
| `REQ-GH02` | Event | When `GitHubHost.get_ci_status(branch, cwd)` is called, the system SHALL invoke `gh run list --branch {branch} --limit 1` and return `CiStatus \| None`. |
| `REQ-GH03` | Event | When `GitHubHost.get_releases(cwd)` is called, the system SHALL invoke `gh release list --json tagName,name,publishedAt,isLatest` and return `list[ReleaseInfo]`. |
| `REQ-GH04` | Unwanted | If `gh` is not found or any `gh` command fails, all `GitHubHost` methods SHALL return `None` or empty list without raising exceptions. |
| `REQ-GH05` | Ubiquitous | `GitHubHost.create_pr` and `GitHubHost.create_release` SHALL raise `NotImplementedError` until `pr-create-workflow` and `release-tagging` changes. |
| `REQ-GI01` | Event | When `GitHubIssueTracker.get_issues(state, cwd)` is called, the system SHALL invoke `gh issue list --state {state} --json number,title,body,labels,assignees,state,url` and return `list[Issue]`. |
| `REQ-GI02` | Unwanted | If `gh` is not found or the command fails, `get_issues` SHALL return an empty list without raising exceptions. |
| `REQ-GI03` | Ubiquitous | `create_issue`, `close_issue` and `assign_issue` SHALL raise `NotImplementedError` until `issues-actions` change. |
| `REQ-NL01` | Ubiquitous | `NullIssueTracker` SHALL implement all `IssueTracker` methods returning `[]` or `None` without raising exceptions. |
| `REQ-NL02` | Ubiquitous | `NullGitHost` SHALL implement all `GitHost` methods returning `None` or `[]` without raising exceptions. |
| `REQ-NL03` | Ubiquitous | `NullIssueTracker` and `NullGitHost` SHALL be the default when `issue_tracker: none` or `git_host: none` is configured. *(Fallback when `gh` is not installed regardless of config is deferred.)* |
| `REQ-CM01` | Ubiquitous | `core/github.py` SHALL re-export `PrStatus`, `CiStatus`, `ReleaseInfo`, `get_pr_status`, `get_ci_status`, `get_releases` from `core/providers/` so that all existing imports continue to work unchanged. |
| `REQ-WC01` | Event | When `load_git_workflow_config(openspec_path)` is called and `openspec/config.yaml` contains `git_workflow:`, the system SHALL return a `GitWorkflowConfig` with the parsed values. |
| `REQ-WC02` | Unwanted | If `openspec/config.yaml` does not exist or has no `git_workflow:` section, `load_git_workflow_config` SHALL return `GitWorkflowConfig()` with defaults. SHALL NOT raise exceptions. |
| `REQ-WC03` | Ubiquitous | Default values: `issue_tracker="none"`, `git_host="none"`, `branching_model="github-flow"`, `change_prefix="issue"`, `changelog_format="both"`. |
| `REQ-WC04` | Event | When `App` initializes, the system SHALL call `load_git_workflow_config(openspec_path)` and assign singletons to `app._git_host` and `app._issue_tracker`. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| `typing.Protocol` (structural subtyping) | ABC + herencia explícita | Sin acoplamiento; mocks sin herencia |
| Singletons en App | Instancia por llamada | Consistente con `self.app._git` existente |
| Shim en `core/github.py` | Actualizar todos los imports | Cero riesgo de regresión; eliminable en epic-2 |
| `load_git_workflow_config` en `core/reader.py` | En `core/config.py` | `config.py` lee config global del usuario; `reader.py` lee por proyecto |
| `create_pr` / `create_issue` con `NotImplementedError` | No declararlos aún | Protocolo completo desde el inicio |
