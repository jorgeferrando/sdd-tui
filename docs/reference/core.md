# Core Reference

The core domain is the headless engine of sdd-tui: it reads `openspec/` from disk, parses pipeline state and task lists, queries git, and computes derived metrics — all without any TUI dependency. Key modules include `reader.py` (change loading and multi-project config), `git_reader.py` (commits, diffs, working-tree state), `pipeline.py` (task and pipeline state parsing), `metrics.py` (spec coverage, complexity, repair hints), `velocity.py` (lead time and throughput), and `providers/` (GitHub and issue-tracker integrations via Protocol). The core is designed to be fully testable in isolation: no screen is ever imported, and all git calls are mockable at the `GitReader` boundary.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-VM01` | Event | When `compute_velocity(archive_dirs, cwd)` is called, the system SHALL return a `VelocityReport` aggregated from all archive dirs. |
| `REQ-VM02` | Ubiquitous | The system SHALL infer start_date as the first git commit containing `[{change_name}]`. |
| `REQ-VM03` | Ubiquitous | The system SHALL infer end_date as the last git commit containing `[{change_name}]`. |
| `REQ-VM04` | Ubiquitous | The lead time SHALL be `end_date - start_date` in days. |
| `REQ-VM05` | Unwanted | If no commits found, the system SHALL set all dates to `None` without raising. |
| `REQ-VM06` | Ubiquitous | Throughput SHALL be computed per ISO week for the last 8 weeks. |
| `REQ-VM07` | Unwanted | If a change has no `end_date`, it SHALL be excluded from calculations. |
| `REQ-VM08` | Ubiquitous | `median_lead_time` and `p90_lead_time` SHALL aggregate across all projects. |
| `REQ-VM09` | Unwanted | If fewer than 2 changes have lead time data, both SHALL be `None`. |
| `REQ-VM10` | Optional | Where multi-project, the system SHALL aggregate all archive_dirs. |
| `REQ-VM11` | Unwanted | If git fails, the system SHALL return an empty `VelocityReport` without raising. |
| `REQ-VM12` | Ubiquitous | git queries SHALL use `-F` (fixed-strings). |
| `REQ-01` | Optional | Where `~/.sdd-tui/config.yaml` exists and declares multiple projects, the system SHALL load changes from all declared project paths. |
| `REQ-02` | Ubiquitous | The system SHALL use `Path.cwd()` as the single project when no config file exists. |
| `REQ-03` | Unwanted | If a declared project path does not exist or has no `openspec/`, the system SHALL skip it silently. |
| `REQ-04` | Ubiquitous | Each `Change` SHALL carry `project: str` and `project_path: Path`. |
| `REQ-05` | Ubiquitous | In single-project mode, `Change.project` SHALL be the basename of `Path.cwd()`. |
| `REQ-06` | Unwanted | If `config.yaml` is malformed, the system SHALL fall back to single-project mode silently. |
| `REQ-01` | Ubiquitous | The `check_deps()` function SHALL detect a dependency as missing when its `check_cmd` raises `FileNotFoundError` OR returns a non-zero exit code. |
| `REQ-02` | Ubiquitous | The `check_deps()` function SHALL detect a dependency as present when its `check_cmd` exits with code 0. |
| `REQ-03` | Ubiquitous | Each dependency check SHALL be independent — failure of one SHALL NOT prevent checking the rest. |
| `REQ-SK-01` | Event | When `load_skills(skills_dir)` es llamado, the reader SHALL escanear todos los subdirectorios de `skills_dir` y retornar `list[SkillInfo]` ordenada. |
| `REQ-SK-02` | Event | When se procesa un subdirectorio, the reader SHALL leer el front matter YAML de `{subdir}/SKILL.md` y extraer `name` y `description`. |
| `REQ-SK-03` | Unwanted | If `skills_dir` no existe, the reader SHALL retornar `[]` sin excepción. |
| `REQ-SK-04` | Unwanted | If un subdirectorio no tiene `SKILL.md` o su front matter es inválido/incompleto, the reader SHALL ignorarlo silenciosamente. |
| `REQ-SK-05` | Ubiquitous | The reader SHALL retornar los skills con prefijo `sdd-` primero (alfabético), seguidos del resto también alfabéticamente. |
| `REQ-RH-01` | Event | When `repair_hints(metrics, change)` is called, the function SHALL return a non-empty list with at least one hint string. |
| `REQ-RH-02` | Ubiquitous | The function SHALL evaluate hints in priority order 1→9; each hint that applies SHALL appear before any lower-priority hint. |
| `REQ-RH-03` | Ubiquitous | Pipeline hints (1–6) SHALL take precedence over spec quality hints (7–8). |
| `REQ-RH-04` | Ubiquitous | When all pipeline phases are DONE and all quality checks pass, the function SHALL return `["✓"]`. |
| `REQ-RH-05` | Unwanted | If `pipeline.spec == PENDING`, the function SHALL NOT include spec quality hints (7–8). |
| `REQ-RH-06` | Ubiquitous | Hint strings for pipeline phases SHALL include the change name: `/sdd-{phase} {change.name}`. |
| `REQ-RH-07` | Unwanted | If any error occurs, the function SHALL NOT raise exceptions. |
| `REQ-ML-01` | Event | When `load_milestones(openspec_path)` is called and `milestones.yaml` exists, the system SHALL return a `list[Milestone]` parsed from the file, in declaration order. |
| `REQ-ML-02` | Unwanted | If `milestones.yaml` does not exist, the system SHALL return `[]` without raising. |
| `REQ-ML-03` | Unwanted | If `milestones.yaml` is malformed or unparseable, the system SHALL return `[]` without raising. |
| `REQ-ML-04` | Unwanted | If a milestone block has no `changes:` list, the system SHALL include the milestone with `changes=[]`. |
| `REQ-ML-05` | Ubiquitous | The parser SHALL NOT require PyYAML — parsing SHALL be implemented with stdlib only (regex + string ops). |
| `REQ-TD-01` | Event | When `load_todos(openspec_path)` is called and `openspec/todos/` exists, the system SHALL return a `list[TodoFile]` parsed from all `*.md` files, sorted alphabetically by filename. |
| `REQ-TD-02` | Unwanted | If `openspec/todos/` does not exist, the system SHALL return `[]` without raising. |
| `REQ-TD-03` | Unwanted | If a file cannot be read or decoded, the system SHALL skip it silently. |
| `REQ-TD-04` | Ubiquitous | The `TodoFile.title` SHALL be the text of the first `# Heading` found in the file; if none, the filename stem. |
| `REQ-TD-05` | Ubiquitous | Only lines matching `- [ ] text` or `- [x] text` SHALL be parsed as `TodoItem`; all other lines SHALL be ignored. |
| `REQ-TD-06` | Ubiquitous | The parser SHALL NOT require PyYAML or any dependency beyond stdlib. |
| `REQ-TD-07` | Unwanted | If a file contains no checkbox lines, the system SHALL include a `TodoFile` with `items=[]`. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| Inferencia sin estado propio | Base de datos SQLite | Máxima simplicidad, fuente de verdad = disco |
| `git status --porcelain` via subprocess | pygit2 / gitpython | Sin dependencias extra, git asumido instalado |
| Dataclasses para modelos | TypedDict / Pydantic | Suficiente para v1, sin overhead |
| `OpenspecNotFoundError` en lugar de `[]` | Retornar lista vacía | Distinguir "no hay changes" de "no hay openspec" |
| IDs de tarea siempre `TXX` | IDs libres | Formato fijo → parseado predecible, líneas sin ID ignoradas |
| Hint de commit en tasks.md | Buscar por TXX en git log | Formato de commit no incluye TXX; hint es preciso |
| `git log --grep` | `git log --all` manual | Comando nativo, un resultado basta |
| `TaskGitState` independiente de `done` | Unificar en un solo campo | `done` = estado en tasks.md; `git_state` = realidad en git. Pueden diferir |
| Hash 7 chars | Hash completo | Estándar git, suficiente para display |
| `find_commit` usa `-F` (fixed-strings) | grep regex por defecto | `[view-3]` como regex es clase de caracteres, nunca coincide |
| Transport Protocol eliminado (TmuxTransport, ZellijTransport, detect_transport) | Mantener como feature activa | Complejidad sin retorno: tmux/zellij targeting no fiable. Eliminado en cleanup-remove-transports (2026-03-03) |
| `git show` para diff de commit | `git diff {hash}^..{hash}` | `git show` incluye metadata del commit |
| `get_working_diff` retorna `None` si vacío | Retornar `""` | Permite distinción entre "sin cambios" y "error" en la TUI |
| TaskParser acepta `[A-Z]+\d+` | Solo `T\d+` | BUG01, MEJ01 son IDs válidos en el flujo SDD |
