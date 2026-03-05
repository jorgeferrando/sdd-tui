# Tasks: git-local-info

## Metadata
- **Change:** git-local-info
- **Jira:** N/A (proyecto standalone)
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/models.py` — extender `CommitInfo` con `author` y `date_relative` opcionales
  - Commit: `[git-local-info] Extend CommitInfo with author and date_relative fields`

- [x] **T02** Modificar `src/sdd_tui/core/git_reader.py` — añadir `get_branch()`, `get_change_log()`, `get_status_short()`
  - Depende de: T01
  - Commit: `[git-local-info] Add get_branch, get_change_log, get_status_short to GitReader`

- [x] **T03** Modificar `tests/test_git_reader.py` — tests para los 3 nuevos métodos de GitReader
  - Depende de: T02
  - Commit: `[git-local-info] Add tests for new GitReader methods`

- [x] **T04** Modificar `src/sdd_tui/tui/app.py` — leer rama activa en mount y refresh, asignar a `sub_title`
  - Depende de: T02
  - Commit: `[git-local-info] Show active git branch in app sub_title`

- [x] **T05** Crear `src/sdd_tui/tui/git_log.py` — `GitLogScreen` con split layout (CommitListPanel + DiffPanel)
  - Depende de: T01, T02
  - Commit: `[git-local-info] Add GitLogScreen with commit list and diff panel`

- [x] **T06** Modificar `src/sdd_tui/tui/change_detail.py` — binding `G` → GitLogScreen + working tree header en `_load_diff_worker`
  - Depende de: T05
  - Commit: `[git-local-info] Add G binding for GitLogScreen and working tree header in diff`

- [x] **T07** Crear `tests/test_tui_git_log.py` — tests de `GitLogScreen`
  - Depende de: T05
  - Commit: `[git-local-info] Add tests for GitLogScreen`

## Quality Gate Final

- [x] **QG** Ejecutar tests + lint
  - `uv run pytest`
  - `~/.claude/scripts/sdd-tui-lint.sh`

## Notas

- T01 antes que todo: `CommitInfo` es el contrato que usan `GitReader` y `GitLogScreen`
- T03 y T04 son independientes entre sí — ambos dependen solo de T02
- T05 antes que T06: `change_detail.py` importa `GitLogScreen`
- T07 puede hacerse en paralelo con T06 conceptualmente, pero en la práctica va después de T05
- `DiffPanel` se importa desde `change_detail.py` en `git_log.py` — no hay módulo separado para él
- `git branch --show-current` puede retornar cadena vacía en detached HEAD → tratar como `None`
- El separador `\x1f` en `--format` de git log evita colisiones con cualquier contenido de commit
