# Tasks: docs-site

## Metadata
- **Change:** docs-site
- **Jira:** n/a
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Notas previas

- Scope de este change: infraestructura + Getting Started + Workflow (9 skills)
- Scope de `docs-site-content`: openspec ref + TUI ref + best practices
- Proyecto ficticio para ejemplos: "taskflow" (CLI de gestión de tareas)
- Sin Quality Gate de tests — validación es `mkdocs build` sin errores

## Tareas de Implementación

- [x] **T01** Modificar `pyproject.toml` — añadir `[project.optional-dependencies] docs`
  - Commit: `[docs-site] Add mkdocs-material to optional docs dependencies`

- [x] **T02** Crear `mkdocs.yml` — configuración MkDocs Material con nav, Mermaid y tema
  - Commit: `[docs-site] Add mkdocs.yml with Material theme and full navigation`
  - Depende de: T01

- [x] **T03** Crear `.github/workflows/docs.yml` — deploy automático a gh-pages en push a main
  - Commit: `[docs-site] Add GitHub Actions workflow for docs deploy`
  - Depende de: T02

- [x] **T04** Crear `docs/index.md` — hero page: qué es SDD, problema, dos herramientas
  - Commit: `[docs-site] Add home page: SDD intro and tools overview`

- [x] **T05** Crear `docs/getting-started/install.md` — install macOS/Linux/Windows + sdd-setup
  - Commit: `[docs-site] Add install guide for macOS, Linux and Windows`
  - Depende de: T04

- [x] **T06** Crear `docs/getting-started/first-change.md` — tutorial end-to-end con "taskflow"
  - Commit: `[docs-site] Add first-change tutorial with taskflow example project`
  - Depende de: T05

- [x] **T07** Crear `docs/workflow/overview.md` — diagrama Mermaid ciclo completo + tabla de skills
  - Commit: `[docs-site] Add workflow overview with SDD cycle diagram`
  - Depende de: T04

- [x] **T08** Crear `docs/workflow/sdd-init.md` — bootstrap y onboarding guiado
  - Commit: `[docs-site] Add sdd-init skill reference page`
  - Depende de: T07

- [x] **T09** Crear `docs/workflow/sdd-new.md` — explore + propose
  - Commit: `[docs-site] Add sdd-new skill reference page`
  - Depende de: T07

- [x] **T10** Crear `docs/workflow/sdd-ff.md` — fast-forward propose→tasks
  - Commit: `[docs-site] Add sdd-ff skill reference page`
  - Depende de: T07

- [x] **T11** Crear `docs/workflow/sdd-apply.md` — implementación tarea a tarea
  - Commit: `[docs-site] Add sdd-apply skill reference page`
  - Depende de: T07

- [x] **T12** Crear `docs/workflow/sdd-verify.md` — quality gates y self-review
  - Commit: `[docs-site] Add sdd-verify skill reference page`
  - Depende de: T07

- [x] **T13** Crear `docs/workflow/sdd-archive.md` — cierre del change
  - Commit: `[docs-site] Add sdd-archive skill reference page`
  - Depende de: T07

- [x] **T14** Crear `docs/workflow/sdd-continue.md` — router de fase pendiente
  - Commit: `[docs-site] Add sdd-continue skill reference page`
  - Depende de: T07

- [x] **T15** Crear `docs/workflow/sdd-steer.md` — steering artifacts
  - Commit: `[docs-site] Add sdd-steer skill reference page`
  - Depende de: T07

## Bugs detectados en verify

- [x] **BUG01** `docs/workflow/sdd-verify.md` — sin ejemplo concreto de output (REQ-06)
  - Detectado: self-review spec compliance
  - Fix: añadir bloque de ejemplo de verify report
  - Commit: `[docs-site] Add verify output example to sdd-verify page`

## Mejoras post-T15

- [x] **MEJ01** `docs/openspec/`, `docs/tui/`, `docs/best-practices/` — stub placeholder pages (10 files) para que `mkdocs build --strict` pase con el nav completo
  - Commit: `[docs-site] Add placeholder stubs for docs-site-content sections`

## Quality Gate Final

- [x] **QG** Verificar que el site construye sin errores
  - `pip install mkdocs-material && mkdocs build --strict`
  - Comprobar que todos los links internos de `mkdocs.yml` tienen su fichero correspondiente
