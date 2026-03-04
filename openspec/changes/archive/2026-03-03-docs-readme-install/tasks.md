# Tasks: README actualizado con instrucciones de instalación

## Metadata
- **Change:** docs-readme-install
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Reescribir `README.md` — descripción, install, prerequisito, usage, keybindings, stack
  - Commit: `[docs] Update README with install instructions and current state`

## Quality Gate Final

- [x] **QG** Verificar que los comandos de instalación son correctos
  - `pip install git+https://github.com/jorgeferrando/sdd-tui` — sintaxis válida ✓ (build funciona)
  - `uv tool install git+...` — mismo URL
  - `pipx install git+...` — mismo URL
