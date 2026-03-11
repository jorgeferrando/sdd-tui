# Proposal: provider-abstraction

## Descripción

Introduce una capa de abstracción de providers (Protocol-based) para desacoplar
la TUI de implementaciones concretas de issue tracking (GitHub Issues, JIRA, Trello)
y hosting git (GitHub, Bitbucket, GitLab). Incluye el wizard de configuración de
flujo git en `openspec/config.yaml`.

## Motivación

`core/github.py` contiene funciones acopladas directamente a `gh` CLI. Si se añade
soporte para JIRA, Trello o Bitbucket sin este cambio, cada propuesta del epic
`git-native-workflow` duplicaría lógica de selección de provider, haría los tests
más complejos y convertiría una futura integración en una reescritura.

Este cambio establece la base arquitectónica que hace posible todo el epic sin
deuda técnica acumulada.

## Qué cambia

### Nuevo paquete `core/providers/`

```
core/providers/
├── __init__.py
├── protocol.py     ← IssueTracker + GitHost (Protocols) + dataclasses compartidos
├── github.py       ← GitHubIssueTracker + GitHubHost (migración de core/github.py)
└── null.py         ← NullIssueTracker + NullGitHost (no-op silencioso)
```

### Compatibilidad hacia atrás

`core/github.py` pasa a ser un shim de re-exportación:

```python
# core/github.py — shim de compatibilidad (se elimina en epic-2)
from sdd_tui.core.providers.github import (  # noqa: F401
    PrStatus, CiStatus, ReleaseInfo,
    get_pr_status, get_ci_status, get_releases,
)
```

Ningún archivo existente (change_detail.py, releases.py, tests) requiere cambios.

### Extensión de config

Nuevo dataclass `GitWorkflowConfig` + parsing de la sección `git_workflow:` en
`openspec/config.yaml` (config per-proyecto, distinta de `~/.sdd-tui/config.yaml`):

```yaml
git_workflow:
  issue_tracker: github        # github | jira | trello | none
  git_host: github             # github | bitbucket | gitlab | none
  branching_model: github-flow # github-flow | git-flow
  change_prefix: issue         # issue | "#" | texto libre | ""
  changelog_format: both       # labels | commit-prefix | both
```

### Wizard TUI

Nueva pantalla `GitWorkflowSetupScreen` (5 preguntas secuenciales) que escribe la
sección `git_workflow:` en `openspec/config.yaml`. Accesible vía binding `S` en
`EpicsView` y de forma automática cuando una feature git-native detecta que falta
la config.

## Alternativas descartadas

| Alternativa | Motivo descartado |
|-------------|------------------|
| Añadir JIRA/Trello directamente en `core/github.py` con `if provider == "jira"` | Viola OCP — cada nuevo provider toca el mismo archivo |
| ABC en lugar de Protocol | Protocol es más Pythónico, no requiere herencia explícita, mejor para tests con mocks |
| Config en `~/.sdd-tui/config.yaml` (global) | El branching model y prefix son per-proyecto — deben vivir en `openspec/config.yaml` |
| Wizard separado del epic (sdd-setup) | El wizard es parte del contrato de configuración del epic — incluirlo aquí evita que las propuestas 1–6 lo reciban incompleto |

## Impacto

| Área | Impacto |
|------|---------|
| `core/github.py` | Pasa a shim — sin cambios de comportamiento |
| `tui/change_detail.py` | Sin cambios — sigue importando de `core/github.py` |
| `tui/releases.py` | Sin cambios |
| `tests/test_github.py` | Sin cambios — el shim preserva los paths de import |
| Tests nuevos | `test_providers_github.py`, `test_providers_null.py`, `test_git_workflow_config.py` |
| Archivos nuevos | `core/providers/__init__.py`, `protocol.py`, `github.py`, `null.py` |
| `core/reader.py` | Nueva función `load_git_workflow_config(openspec_path)` |
| `tui/epics.py` | Binding `S` → `GitWorkflowSetupScreen` |

Cambios visibles para el usuario: solo el nuevo binding `S` en `EpicsView`.

## Criterios de éxito

- [ ] `core/providers/protocol.py` define `IssueTracker` y `GitHost` como Protocols
- [ ] `GitHubHost` implementa `get_pr_status`, `get_ci_status`, `get_releases`
- [ ] `GitHubIssueTracker` implementa `get_issues` (stub read-only para propuesta 1)
- [ ] `NullIssueTracker` y `NullGitHost` retornan vacío silenciosamente
- [ ] `core/github.py` es un shim — todos los imports existentes siguen funcionando
- [ ] `GitWorkflowConfig` parseado desde `openspec/config.yaml`
- [ ] `GitWorkflowSetupScreen` escribe la sección `git_workflow:` en el archivo
- [ ] Todos los tests existentes siguen en verde sin modificaciones
- [ ] Tests nuevos cubren providers github, null y config parsing
