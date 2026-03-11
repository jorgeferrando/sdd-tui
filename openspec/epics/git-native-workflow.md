# Epic: git-native-workflow

## Metadata
- **Fecha:** 2026-03-11
- **Estado:** proposal
- **Alcance:** gestión de proyectos nativa sin herramientas externas, con arquitectura
  extensible para múltiples proveedores de issue tracking y hosting git.

---

## Visión

sdd-tui gestiona el ciclo de vida completo de desarrollo sin depender de
herramientas externas de project management (JIRA, Trello, Linear, etc.)
ni estar acoplado a un proveedor concreto de hosting git (GitHub, Bitbucket,
GitLab).

Un desarrollador puede, sin salir de la TUI:

- Crear y gestionar issues (features, bugs, tareas)
- Crear ramas vinculadas a issues
- Crear y revisar PRs
- Gestionar releases y tags
- Ver el estado real del proyecto (qué está en develop, qué en main, qué pendiente)

Y la misma TUI funciona independientemente de si el equipo usa:
- **Issue tracker:** GitHub Issues / JIRA / Trello / ninguno
- **Git host:** GitHub / Bitbucket / GitLab / solo local

---

## Principio de diseño central — Provider Model

**Issue tracker y git host son concerns separados e intercambiables.**

```
sdd-tui
├── core/providers/
│   ├── protocol.py          ← IssueTracker + GitHost (Protocols)
│   ├── github.py            ← GitHubIssueTracker + GitHubHost (via gh CLI)
│   ├── jira.py              ← JiraIssueTracker (via REST API)    [futuro]
│   ├── trello.py            ← TrelloIssueTracker (via REST API)  [futuro]
│   ├── bitbucket.py         ← BitbucketHost (via bb CLI)         [futuro]
│   ├── gitlab.py            ← GitLabHost (via glab CLI)          [futuro]
│   └── null.py              ← NullIssueTracker + NullGitHost     (sin provider)
└── core/
    └── github.py            ← mover a providers/github.py en Propuesta 0
```

Un proyecto puede usar combinaciones como:
- GitHub Issues + GitHub hosting (stack actual del proyecto)
- JIRA + GitHub hosting (común en enterprise)
- JIRA + Bitbucket (stack Atlassian)
- Trello + GitHub (equipos pequeños)
- Ninguno + git local (sin proveedor externo)

La TUI siempre trabaja contra los Protocols, nunca contra implementaciones concretas.

---

## Contexto — qué existe hoy

| Capacidad | Estado | Dónde |
|-----------|--------|-------|
| PR status (lectura) | ✓ implementado | `core/github.py` + `PipelinePanel` |
| CI status (lectura) | ✓ implementado | `core/github.py` + `PipelinePanel` |
| Releases (lectura) | ✓ implementado | `core/github.py` + `ReleasesScreen` |
| Git log del change | ✓ implementado | `core/git_reader.py` + `GitLogScreen` |
| Branch activo | ✓ implementado | `git_reader.get_branch()` en app.sub_title |
| Ship PR (clipboard) | ✓ parcial | `W` en `ChangeDetailScreen` — solo copia comando |
| Issues | ✗ no existe | — |
| Crear branch | ✗ no existe | — |
| Crear PR real | ✗ no existe | — |
| Crear release/tag | ✗ no existe | — |
| Branching strategy | ✗ no existe | — |
| Provider abstraction | ✗ no existe | `github.py` acoplado directamente |

**Deuda técnica actual:** `core/github.py` contiene funciones puras acopladas a
`gh` CLI. Antes de añadir más integraciones, debe refactorizarse al modelo de
providers. Esto ocurre en Propuesta 0.

---

## Propuestas (desglose del epic)

### Propuesta 0 — `provider-abstraction`
**Capa de abstracción de providers + configuración del modelo de trabajo.**

Este es el fundamento arquitectónico de todo el epic. Sin él, cada propuesta
siguiente acoplaría directamente a GitHub y sería imposible añadir JIRA/Trello
después sin reescribir.

#### 0.1 — Provider Protocols

```python
# core/providers/protocol.py

class Issue(Protocol):
    id: str
    title: str
    body: str
    labels: list[str]
    assignee: str | None
    state: str          # "open" | "closed"
    url: str

class IssueTracker(Protocol):
    def get_issues(self, state: str = "open") -> list[Issue]: ...
    def get_issue(self, issue_id: str) -> Issue | None: ...
    def create_issue(self, title: str, body: str, labels: list[str]) -> Issue: ...
    def close_issue(self, issue_id: str) -> None: ...
    def assign_issue(self, issue_id: str, assignee: str) -> None: ...

class PrInfo(Protocol):
    number: int
    title: str
    url: str
    state: str          # "open" | "closed" | "merged"
    draft: bool

class GitHost(Protocol):
    def get_pr_status(self, branch: str) -> PrStatus | None: ...
    def get_ci_status(self, branch: str) -> CiStatus | None: ...
    def get_releases(self) -> list[ReleaseInfo]: ...
    def create_pr(self, title: str, body: str, base: str, draft: bool) -> PrInfo: ...
    def create_release(self, tag: str, name: str, body: str, draft: bool) -> None: ...
```

#### 0.2 — Refactor de `core/github.py`

Mover funciones existentes al modelo de providers:
- `get_pr_status` → `GitHubHost.get_pr_status`
- `get_ci_status` → `GitHubHost.get_ci_status`
- `get_releases` → `GitHubHost.get_releases`

`core/github.py` se mantiene como alias de compatibilidad durante la transición
(no rompe nada de lo existente).

#### 0.3 — NullProvider

```python
# core/providers/null.py
class NullIssueTracker:
    """Cuando no hay issue tracker configurado — devuelve vacío silenciosamente."""

class NullGitHost:
    """Cuando no hay git host configurado — devuelve None silenciosamente."""
```

#### 0.4 — Config wizard

Extender `openspec/config.yaml` con sección `git_workflow:`:

```yaml
git_workflow:
  issue_tracker: github        # github | jira | trello | none
  git_host: github             # github | bitbucket | gitlab | none
  branching_model: github-flow # github-flow | git-flow
  change_prefix: issue         # issue | "#" | texto libre | ""
  changelog_format: both       # labels | commit-prefix | both
```

Wizard en TUI (`GitWorkflowSetupScreen`) con 5 preguntas:

1. **Issue tracker**
   > ¿Dónde gestionas los issues del proyecto?
   - `[1]` GitHub Issues
   - `[2]` JIRA *(próximamente)*
   - `[3]` Trello *(próximamente)*
   - `[4]` Sin issue tracker

2. **Git host**
   > ¿Dónde está alojado el repositorio?
   - `[1]` GitHub (`gh` CLI)
   - `[2]` Bitbucket *(próximamente)*
   - `[3]` GitLab *(próximamente)*
   - `[4]` Solo local / sin hosting

3. **Branching model**
   > ¿Qué modelo de ramas usa el proyecto?
   - `[1]` github-flow — solo `main`, PRs directos
   - `[2]` git-flow — `develop` + `main`, releases desde `develop`

4. **Naming de changes**
   > ¿Cómo nombrar las ramas y changes vinculados a issues?
   - `[1]` `issue-42-slug` (prefijo `issue`)
   - `[2]` `#42-slug` (prefijo `#`)
   - `[3]` Solo slug libre sin número de issue
   - `[4]` Personalizado — ingresa el prefijo

5. **Formato de changelog**
   > ¿Cómo agrupar los cambios en el changelog de releases?
   - `[1]` GitHub Labels (`bug`, `enhancement`, `feat`)
   - `[2]` Commit prefix (`fix:`, `feat:`, `chore:`)
   - `[3]` Ambos (labels tienen prioridad; fallback a commit prefix)

El wizard se activa:
- Automáticamente al usar cualquier feature git-native por primera vez
- Manualmente vía `sdd-setup git-workflow` CLI o binding `S` en EpicsView

Dependencias: ninguna.
Valor entregado: base arquitectónica que hace posible todo el epic sin deuda técnica.

---

### Propuesta 1 — `issues-viewer`
**Lectura de GitHub Issues desde la TUI.**

Scope:
- Nueva pantalla `IssuesScreen` (binding `I` en `EpicsView`)
- Tabla con columnas: `#`, `TITLE`, `LABELS`, `ASSIGNEE`, `STATE`
- Filtro por estado: open / closed / all (toggle)
- Usa `IssueTracker.get_issues()` — agnóstico al provider
- Si `issue_tracker: none`, muestra mensaje "No issue tracker configured" con
  sugerencia de ejecutar el wizard
- Linking: si un change tiene `issue: 42` en `proposal.md`, mostrar badge en
  `ChangeDetailScreen`

Dependencias: `provider-abstraction`.
Valor entregado: visibilidad del backlog sin salir de la TUI.

---

### Propuesta 2 — `branch-lifecycle`
**Gestión de ramas desde la TUI.**

Scope:
- Nueva pantalla `BranchesScreen` (binding `B` en `EpicsView`)
- Lista de ramas locales y remotas con ahead/behind main (via `git_reader`)
- Crear rama desde change: `C` en `ChangeDetailScreen` → `git checkout -b {prefix}-{#}-{slug}`
  donde `{prefix}` viene de `change_prefix` en config
- Checkout a rama: `Enter` en `BranchesScreen` → `git checkout {branch}`
- Soporte de branching model: `main` = producción, `develop` = integración, `issue-*` = trabajo
- Divergencia develop vs main en header de `EpicsView`

Nota: usa solo `git` local (vía `git_reader`), no requiere un git host configurado.

Dependencias: `provider-abstraction` (para leer `branching_model` y `change_prefix`).
Valor entregado: el flujo branch-per-issue ocurre sin tocar la terminal.

---

### Propuesta 3 — `pr-create-workflow`
**Crear PR real desde la TUI (no solo copiar comando).**

Scope:
- `W` pasa de clipboard a `GitHost.create_pr(...)` real
- Form modal: título (pre-rellenado desde `proposal.md`), base branch
  (inferido de `branching_model`), labels, reviewers
- Confirmación antes de enviar (acción irreversible)
- Draft PR: `shift+W`
- Merge PR: `M` en `ChangeDetailScreen` con selector squash/merge/rebase
- Si `git_host: none`, `W` mantiene comportamiento clipboard actual

Dependencias: `provider-abstraction`.
Valor entregado: el ciclo issue→branch→code→PR cierra sin salir de la TUI.

---

### Propuesta 4 — `issues-actions`
**Escritura de issues desde la TUI (create, close, assign).**

Scope:
- Crear issue desde TUI: `N` en `IssuesScreen` → form modal (título, body, labels)
  → `IssueTracker.create_issue(...)`
- Cerrar issue: `X` → confirmación → `IssueTracker.close_issue(...)`
- Asignar issue: `A` → `IssueTracker.assign_issue(...)`
- Crear change vinculado a issue: `Enter` en `IssuesScreen` → crea
  `openspec/changes/{prefix}-{#}-{slug}/proposal.md` pre-rellenado desde el issue

Dependencias: `issues-viewer`, `provider-abstraction`.
Valor entregado: el ciclo backlog → change empieza dentro de la TUI.

---

### Propuesta 5 — `release-tagging`
**Crear tags y releases desde la TUI.**

Scope:
- Complementa `ReleasesScreen` existente (solo lectura → lectura + escritura)
- `N` en `ReleasesScreen` → crear release: tag (SemVer auto-sugerido desde último tag),
  título, body (changelog automático desde commits según `changelog_format`)
- `D` → draft release / `P` → publish draft
- `T` → crear solo tag sin release
- Changelog automático: commits desde último tag agrupados
  - si `changelog_format: labels` → por GitHub label
  - si `changelog_format: commit-prefix` → por `feat:` / `fix:` / `chore:`
  - si `changelog_format: both` → labels con fallback a commit prefix
- Merge queue visual: changes en develop no mergeados a main

Dependencias: `provider-abstraction`.
Valor entregado: ciclo de release completo sin salir de la TUI.

---

### Propuesta 6 — `git-flow-dashboard`
**Vista kanban del estado real del proyecto.**

Scope:
- Pantalla `FlowScreen` (binding `F` en `EpicsView`)
- Columnas: Backlog / In Progress / In Review / Merged / Released
- Cada issue aparece en la columna según estado:
  - Backlog: issue abierto sin branch
  - In Progress: branch activo, sin PR
  - In Review: PR abierto
  - Merged: PR mergeado, sin release
  - Released: incluido en una release
- Estado inferido desde git + `IssueTracker` + `GitHost`
- Datos cargados async con workers; columnas independientes

Dependencias: `issues-viewer`, `branch-lifecycle`, `pr-create-workflow`.
Valor entregado: kanban visual basado en git — estado real del proyecto de un vistazo.

---

## Hoja de ruta de providers

| Provider | Tipo | Estado | Mecanismo |
|----------|------|--------|-----------|
| GitHub Issues | IssueTracker | Propuesta 0–1 | `gh` CLI |
| GitHub | GitHost | Propuesta 0–3 | `gh` CLI |
| JIRA | IssueTracker | Futuro (epic-2) | REST API (`/rest/api/3/`) |
| Trello | IssueTracker | Futuro (epic-2) | REST API |
| Bitbucket | GitHost | Futuro (epic-2) | `bb` CLI o REST API |
| GitLab | GitHost | Futuro (epic-2) | `glab` CLI |
| Null | Ambos | Propuesta 0 | No-op silencioso |

El wizard marca JIRA, Trello, Bitbucket y GitLab como "próximamente" para que
el usuario sepa que están en el roadmap aunque no disponibles todavía.

---

## Orden de implementación

```
0. provider-abstraction    (arquitectura + config wizard — fundacional)
1. issues-viewer           (lectura del backlog)
2. branch-lifecycle        (crear ramas desde TUI)
3. pr-create-workflow      (cierra el loop de desarrollo)
4. issues-actions          (escritura del backlog)
5. release-tagging         (ciclo de release)
6. git-flow-dashboard      (síntesis — requiere todo lo anterior)
```

---

## Impacto en el modelo de naming

El formato exacto depende de la config elegida en Propuesta 0:

| Aspecto | `issue-42-slug` | `#42-slug` | slug libre |
|---------|----------------|------------|------------|
| Rama | `issue-42-login-timeout` | `42-login-timeout` | `login-timeout` |
| Change dir | `issue-42-login-timeout/` | `42-login-timeout/` | `login-timeout/` |
| Commit | `[issue-42] Fix ...` | `[#42] Fix ...` | `[login-timeout] Fix ...` |
| Config | `change_prefix: issue` | `change_prefix: "#"` | `change_prefix: ""` |

El SDD workflow no cambia — solo el identificador de la unidad de trabajo.
Las skills SDD existentes siguen funcionando (son agnósticas al ID).

---

## Decisiones pendientes

| Pregunta | Opciones | Resolución |
|----------|----------|------------|
| ¿Branching model? | github-flow vs git-flow | Config wizard — Propuesta 0 |
| ¿Naming de changes? | prefijos múltiples | Config wizard — Propuesta 0 |
| ¿Changelog format? | labels vs commit-prefix | Ambos — labels con fallback |
| ¿Form modal vs `$EDITOR`? | inline TUI vs editor externo | A decidir en design de cada propuesta |
| ¿Operaciones destructivas? | merge, close, delete branch | Siempre con confirmación explícita |
| ¿Credenciales para JIRA/Trello? | env vars vs keychain vs `openspec/config.yaml` | A decidir en epic-2 |

---

## Notas de implementación

- Todas las operaciones de escritura requieren confirmación explícita.
- `gh`/`bb`/`glab` son dependencias opcionales — degradar a NullProvider si no están.
- Tests: todas las operaciones write tienen mocks de `subprocess.run` verificando
  el comando exacto (patrón ya establecido en `test_github.py`).
- `core/github.py` se mantiene como alias durante la transición; se elimina en epic-2.
- Los Protocols de Python no generan overhead en runtime — son solo para type checking.
