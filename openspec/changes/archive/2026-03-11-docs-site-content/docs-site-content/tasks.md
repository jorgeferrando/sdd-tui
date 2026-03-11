# Tasks: docs-site-content

## Metadata
- **Change:** docs-site-content
- **Jira:** n/a
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

### openspec Reference

- [x] **T01** Modificar `docs/openspec/structure.md` — árbol anotado del directorio openspec/
  - Commit: `[docs-site-content] Add openspec directory structure reference`

- [x] **T02** Modificar `docs/openspec/steering.md` — 5 steering files con propósito y formato
  - Commit: `[docs-site-content] Add steering files reference`
  - Depende de: T01

- [x] **T03** Modificar `docs/openspec/milestones.md` — milestones.yaml y todos/ directory
  - Commit: `[docs-site-content] Add milestones and todos reference`

- [x] **T04** Modificar `docs/openspec/providers.md` — GitHub/Null providers y GitWorkflowConfig
  - Commit: `[docs-site-content] Add providers configuration reference`

### TUI Reference

- [x] **T05** Modificar `docs/tui/overview.md` — qué es el TUI, cuándo usarlo, multi-project
  - Commit: `[docs-site-content] Add TUI overview page`

- [x] **T06** Modificar `docs/tui/keybindings.md` — tablas completas por vista
  - Commit: `[docs-site-content] Add complete keybindings reference`

- [x] **T07** Modificar `docs/tui/views.md` — descripción de cada pantalla
  - Commit: `[docs-site-content] Add TUI views reference`
  - Depende de: T05

### Best Practices

- [x] **T08** Modificar `docs/best-practices/scope-control.md` — regla 20 ficheros, cómo dividir
  - Commit: `[docs-site-content] Add scope control best practice`

- [x] **T09** Modificar `docs/best-practices/atomic-commits.md` — one task = one file = one commit
  - Commit: `[docs-site-content] Add atomic commits best practice`

- [x] **T10** Modificar `docs/best-practices/when-not-to-use-sdd.md` — hotfixes, config, patches
  - Commit: `[docs-site-content] Add when-not-to-use-sdd best practice`

## Quality Gate Final

- [x] **QG** `mkdocs build --strict` sin warnings
