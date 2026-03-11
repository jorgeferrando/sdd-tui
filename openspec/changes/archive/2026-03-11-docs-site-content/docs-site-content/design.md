# Design: docs-site-content

## Metadata
- **Change:** docs-site-content
- **Fecha:** 2026-03-11
- **Estado:** approved

## Resumen Técnico

Reemplazar 10 stubs placeholder con contenido real. Sin cambios de infraestructura (mkdocs.yml, workflows, pyproject.toml ya están configurados). Cada archivo es una operación Write independiente.

## Archivos a Modificar

| Archivo | Contenido principal |
|---------|---------------------|
| `docs/openspec/structure.md` | Árbol del directorio anotado + propósito de cada fichero |
| `docs/openspec/steering.md` | 5 steering files: product, tech, structure, conventions, project-rules |
| `docs/openspec/milestones.md` | milestones.yaml formato + todos/ directorio |
| `docs/openspec/providers.md` | GitWorkflowConfig, GitHub vs Null provider, wizard sdd-setup |
| `docs/tui/overview.md` | Qué es el TUI, cuándo usarlo, multi-project config.yaml |
| `docs/tui/keybindings.md` | Tablas de teclas por vista (View 1/2/8/9 + Viewers + Global) |
| `docs/tui/views.md` | Descripción de cada pantalla (7 screens) |
| `docs/best-practices/scope-control.md` | Regla 20 ficheros, cómo dividir con valor independiente |
| `docs/best-practices/atomic-commits.md` | One task = one file = one commit, ejemplos buenos/malos |
| `docs/best-practices/when-not-to-use-sdd.md` | Hotfixes, config-only, < 3 ficheros |

## Scope

- **Total archivos:** 10 modificaciones
- **Resultado:** Ideal (< 10... es exactamente 10, pero son Markdown plano)

## Fuentes de contenido

| Sección | Fuente |
|---------|--------|
| openspec/structure | `openspec/` del propio repo + specs canónicas |
| openspec/steering | `openspec/specs/tooling/spec.md` + steering files del repo |
| openspec/providers | `openspec/specs/providers/spec.md` |
| tui/keybindings | `README.md` sección Keybindings (fuente de verdad) |
| tui/views | `openspec/specs/tui/spec.md` + MEMORY.md |
| best-practices | CLAUDE.md (reglas de scope) + patrones del proyecto |
