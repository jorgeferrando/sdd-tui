# Github Reference

The github domain handles all communication with GitHub via the `gh` CLI: fetching PR status and CI run results for the current branch, listing repository releases, and providing a one-key "ship" shortcut that copies the `gh pr create` command to the clipboard. All calls are non-blocking — they run in background workers so the TUI stays responsive while status loads. If `gh` is not installed or a command fails, every function degrades gracefully to `None` or an empty list rather than raising an exception.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-CI01` | Event | When the user opens `ChangeDetailScreen`, the system SHALL |
| `REQ-CI02` | State | While the CI status is loading, `PipelinePanel` SHALL show |
| `REQ-CI03` | Unwanted | If `gh` is not found or the command fails, `PipelinePanel` |
| `REQ-CI04` | Unwanted | If no workflow runs exist for the branch, `PipelinePanel` |
| `REQ-CI05` | Event | When the CI run status is `completed` and conclusion is |
| `REQ-CI06` | Event | When the CI run status is `completed` and conclusion is |
| `REQ-CI07` | Event | When the CI run status is `in_progress` or `queued`, |
| `REQ-CI08` | Ubiquitous | The CI row SHALL be positioned below the PR row in |
| `REQ-SH01` | Event | When the user presses `W` in `ChangeDetailScreen`, the system |
| `REQ-SH02` | Ubiquitous | The copied command SHALL have the format: |
| `REQ-SH03` | Ubiquitous | The `W` binding SHALL appear in the `Footer` with label |
| `REQ-RL01` | Event | When the user presses `L` in `EpicsView`, the system SHALL |
| `REQ-RL02` | Ubiquitous | `ReleasesScreen` SHALL display a `DataTable` with columns: |
| `REQ-RL03` | Event | When `ReleasesScreen` mounts, the system SHALL call |
| `REQ-RL04` | Unwanted | If `gh` is not found, the command fails, or no releases |
| `REQ-RL05` | Event | When the user presses `Escape` in `ReleasesScreen`, the system |
| `REQ-RL06` | Optional | Where `isLatest` is true, the LATEST column SHALL display |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| CI cargado solo en ChangeDetailScreen (bajo demanda) | Columna CI en EpicsView | Evita O(N) llamadas gh al abrir la app |
| Ship = clipboard solamente | Ejecutar `gh pr create` directo | Acción irreversible — clipboard preserva control del usuario |
| Releases en pantalla separada (L) | Columna en EpicsView | Las releases son del repo, no de un change específico |
| `get_ci_status` recibe `branch: str` | Inferir branch internamente | Desacopla de git_reader — más testeable |
