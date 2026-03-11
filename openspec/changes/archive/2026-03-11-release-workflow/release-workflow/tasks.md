# Tasks: Release Workflow

## Metadata
- **Change:** release-workflow
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/core/providers/protocol.py` — añadir `ReleaseWorkflowConfig` dataclass
  - Commit: `[release-workflow] Add ReleaseWorkflowConfig dataclass`

- [x] **T02** Modificar `src/sdd_tui/core/reader.py` — añadir `load_release_config`, `_parse_release_workflow`, `_write_release_config`
  - Depende de: T01
  - Commit: `[release-workflow] Add load_release_config and write helpers to reader`

- [x] **T03** Crear `tests/test_release_config.py` — tests unitarios de `load_release_config` y `_write_release_config`
  - Depende de: T02
  - Commit: `[release-workflow] Add tests for load_release_config and _write_release_config`

- [x] **T04** Modificar `src/sdd_tui/tui/app.py` — check en `on_mount`: notificación si `release_workflow:` ausente (REQ-OB01-03)
  - Depende de: T02
  - Commit: `[release-workflow] Notify on startup when release workflow not configured`

- [x] **T05** Modificar `src/sdd_tui/tui/setup.py` — añadir `_RELEASE_QUESTIONS` (3 pasos condicionales) + extender `_save_and_dismiss` para escribir `release_workflow:` en config.yaml
  - Depende de: T02
  - Commit: `[release-workflow] Add release workflow steps to GitWorkflowSetupScreen`

- [x] **T06** Modificar `tests/test_tui_setup.py` — tests del wizard extendido: releases=yes (versioning+formula), releases=no (skip), config escrita correctamente
  - Depende de: T05
  - Commit: `[release-workflow] Add tests for release workflow wizard steps`

- [x] **T07** Crear `scripts/changelog.py` — generación de CHANGELOG.md desde openspec/archive, version boundaries (git tags + openspec/versions/), flags `--version` y `--mark-version`
  - Commit: `[release-workflow] Add changelog.py script`

- [x] **T08** Crear `tests/test_changelog.py` — tests de `changelog.py`: collect_archived_changes, version boundaries desde markers, assign changes, mark_version, extract_section, sin boundaries → [Unreleased]
  - Depende de: T07
  - Commit: `[release-workflow] Add tests for changelog.py`

- [x] **T09** Crear `openspec/versions/.gitkeep` — mantiene el directorio en git
  - Commit: `[release-workflow] Add openspec/versions/ directory`

- [x] **T10** Crear `scripts/release.sh` — script de release completo: validate → pytest → git clean → bump pyproject.toml → changelog → tag → push → gh release → formula SHA256 → push
  - Depende de: T07
  - Commit: `[release-workflow] Add release.sh script`

## Quality Gate Final

- [x] **QG** Ejecutar tests + lint
  - `uv run pytest`
  - `~/.claude/scripts/sdd-tui-lint.sh`

## Notas

- T01 primero: `ReleaseWorkflowConfig` es el contrato que usan T02, T04, T05
- T02 antes de T04 y T05: `load_release_config` y `_write_release_config` deben existir
- T03, T04, T05 son independientes entre sí (todos dependen solo de T02)
- T07 es standalone (stdlib Python puro) — no depende del paquete sdd_tui
- T08 puede desarrollarse en TDD (RED→GREEN) junto con T07
- T09 es trivial — puede hacerse en cualquier momento
- T10 al final: depende de T07 (llama a `changelog.py`) y requiere los scripts probados
- `_RELEASE_QUESTIONS` usa `skip_if: lambda answers: answers.get("releases_enabled") == "no"` para omitir pasos conditionales
- `load_release_config` retorna `(ReleaseWorkflowConfig, bool)` — la tupla distingue "ausente" (notify) de `enabled=False` (no notify)
- `release.sh` lee `openspec/config.yaml` con grep/awk sin depender de Python
- SHA256 del tarball: `curl -sL <url> | sha256sum` — sin descargar a disco
