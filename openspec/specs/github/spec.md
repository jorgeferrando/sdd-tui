# Spec: GitHub — gh-actions

## Metadata
- **Dominio:** github
- **Change:** gh-actions
- **Jira:** N/A
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Integración de la TUI con GitHub vía `gh` CLI. Amplía la visibilidad del estado de
un change más allá del PR (ya implementado): CI status, ship shortcut y releases.

## Comportamiento Actual

- `PipelinePanel` muestra estado del PR (número, estado, aprobaciones) cargado async.
- `gh` disponible es opcional — si no está, la fila PR muestra "—".
- `Space` en `ChangeDetailScreen` copia el siguiente comando SDD al clipboard.

## Requisitos (EARS)

### CI Status

- **REQ-CI01** `[Event]` When the user opens `ChangeDetailScreen`, the system SHALL
  fetch the CI status of the change's active branch asynchronously and display it in
  `PipelinePanel` under a "CI" row.

- **REQ-CI02** `[State]` While the CI status is loading, `PipelinePanel` SHALL show
  "…" in the CI row.

- **REQ-CI03** `[Unwanted]` If `gh` is not found or the command fails, `PipelinePanel`
  SHALL show "—" in the CI row.

- **REQ-CI04** `[Unwanted]` If no workflow runs exist for the branch, `PipelinePanel`
  SHALL show "—" in the CI row.

- **REQ-CI05** `[Event]` When the CI run status is `completed` and conclusion is
  `success`, `PipelinePanel` SHALL display "✓" in the CI row.

- **REQ-CI06** `[Event]` When the CI run status is `completed` and conclusion is
  `failure` or `cancelled`, `PipelinePanel` SHALL display "✗" in the CI row.

- **REQ-CI07** `[Event]` When the CI run status is `in_progress` or `queued`,
  `PipelinePanel` SHALL display "⟳" in the CI row.

- **REQ-CI08** `[Ubiquitous]` The CI row SHALL be positioned below the PR row in
  `PipelinePanel`.

### Ship Binding

- **REQ-SH01** `[Event]` When the user presses `W` in `ChangeDetailScreen`, the system
  SHALL copy a `gh pr create` command to the clipboard and notify the user.

- **REQ-SH02** `[Ubiquitous]` The copied command SHALL have the format:
  `gh pr create --title "[{change-name}] {description}" --body ""`
  where `{description}` is the first non-empty line of `proposal.md` after the `# ` heading,
  or empty string if `proposal.md` does not exist.

- **REQ-SH03** `[Ubiquitous]` The `W` binding SHALL appear in the `Footer` with label
  "Ship PR".

### Releases Screen

- **REQ-RL01** `[Event]` When the user presses `L` in `EpicsView`, the system SHALL
  open `ReleasesScreen`.

- **REQ-RL02** `[Ubiquitous]` `ReleasesScreen` SHALL display a `DataTable` with columns:
  TAG, NAME, DATE, LATEST.

- **REQ-RL03** `[Event]` When `ReleasesScreen` mounts, the system SHALL call
  `gh release list --json tagName,name,publishedAt,isLatest` and populate the table.

- **REQ-RL04** `[Unwanted]` If `gh` is not found, the command fails, or no releases
  exist, `ReleasesScreen` SHALL show "No releases found" in the table.

- **REQ-RL05** `[Event]` When the user presses `Escape` in `ReleasesScreen`, the system
  SHALL return to `EpicsView`.

- **REQ-RL06** `[Optional]` Where `isLatest` is true, the LATEST column SHALL display
  "✓", otherwise "·".

## Interfaces / Contratos

### CiStatus dataclass
```python
@dataclass
class CiStatus:
    workflow: str        # nombre del workflow
    status: str          # "queued" | "in_progress" | "completed"
    conclusion: str | None  # "success" | "failure" | "cancelled" | None
```

### ReleaseInfo dataclass
```python
@dataclass
class ReleaseInfo:
    tag_name: str
    name: str
    published_at: str   # ISO 8601
    is_latest: bool
```

### get_ci_status(branch: str, cwd: Path) -> CiStatus | None
- Llama `gh run list --branch {branch} --limit 1 --json status,conclusion,workflowName`
- Retorna `None` si gh no disponible, error o lista vacía

### get_releases(cwd: Path) -> list[ReleaseInfo]
- Llama `gh release list --json tagName,name,publishedAt,isLatest`
- Retorna lista vacía si gh no disponible o error

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| CI cargado solo en ChangeDetailScreen (bajo demanda) | Columna CI en EpicsView | Evita O(N) llamadas gh al abrir la app |
| Ship = clipboard solamente | Ejecutar `gh pr create` directo | Acción irreversible — clipboard preserva control del usuario |
| Releases en pantalla separada (L) | Columna en EpicsView | Las releases son del repo, no de un change específico |
| `get_ci_status` recibe `branch: str` | Inferir branch internamente | Desacopla de git_reader — más testeable |

## Abierto / Pendiente

- ¿Cómo obtener el branch del change en `ChangeDetailScreen`? La rama activa viene de
  `app._git.get_branch(cwd)` — usaremos `get_branch()` al montar la pantalla.
  (No bloquea — decisión de implementación para design.)
