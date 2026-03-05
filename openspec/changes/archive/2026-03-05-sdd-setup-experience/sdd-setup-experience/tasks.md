# Tasks: sdd-setup-experience

## Metadata
- **Change:** sdd-setup-experience
- **Jira:** N/A (proyecto standalone)
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Modificar `pyproject.toml` — añadir entry point `sdd-setup`
  - Commit: `[sdd-setup-experience] Add sdd-setup entry point to pyproject.toml`

- [x] **T02** Crear `src/sdd_tui/setup.py` — CLI `sdd-setup` con flags, clone de GitHub, copia de skills, check
  - Depende de: T01
  - Commit: `[sdd-setup-experience] Add sdd-setup CLI with GitHub skills download`

- [x] **T03** Crear `tests/test_setup.py` — tests unitarios de setup.py
  - Depende de: T02
  - Commit: `[sdd-setup-experience] Add tests for sdd-setup CLI`

- [x] **T04** Crear `Formula/sdd-tui.rb` — Homebrew formula
  - Commit: `[sdd-setup-experience] Add Homebrew formula`

- [x] **T05** Crear `scripts/install.sh` — instalador Linux (detecta pkg manager, instala TUI + llama sdd-setup)
  - Commit: `[sdd-setup-experience] Add Linux install.sh`

- [x] **T06** Crear `scripts/Install-SddTui.ps1` — instalador Windows PowerShell 5.1+
  - Commit: `[sdd-setup-experience] Add Windows PowerShell installer`

- [x] **T07** Modificar `README.md` — reescribir sección Install por plataforma (macOS, Linux, Windows)
  - Depende de: T01–T06
  - Commit: `[sdd-setup-experience] Update README with per-platform install instructions`

## Quality Gate Final

- [x] **QG** Ejecutar tests + lint
  - `uv run pytest`
  - `~/.claude/scripts/sdd-tui-lint.sh`

## Notas

- T01 antes que T02: el entry point en pyproject.toml es lo que registra el comando `sdd-setup`
- T02 antes que T03: TDD aquí significaría tests primero, pero el CLI tiene IO complejo — implementar y luego testear con mocks es más pragmático
- T04–T06 son independientes entre sí y de T02–T03 — pueden hacerse en cualquier orden
- T07 al final: el README describe la experiencia completa, conviene tenerla implementada para verificar los comandos documentados
- Formula/sdd-tui.rb: el SHA256 se calcula sobre el tarball de la release — dejar placeholder `"SHA256_PLACEHOLDER"` y documentar cómo actualizarlo en el archivo
- `sdd-setup` necesita `git` en PATH para el clone — ya está en DEPS como required, no es una nueva dependencia
