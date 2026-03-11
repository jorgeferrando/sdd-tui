# Proposal: docs-site-content

## Descripción

Completar el site de documentación reemplazando los 10 stubs placeholder creados en `docs-site` con contenido real. Las tres secciones pendientes son: openspec Reference (4 páginas), TUI Reference (3 páginas) y Best Practices (3 páginas).

## Motivación

El change `docs-site` desplegó el site con las secciones Getting Started y Workflow completas, pero las secciones openspec Reference, TUI Reference y Best Practices muestran "Coming soon". El site está activo en https://jorgeferrando.github.io/sdd-tui/ — completar el contenido cierra la documentación v1.

## Scope

10 archivos — todos reemplazos de stubs existentes, sin archivos nuevos ni modificaciones de infraestructura.

### openspec Reference (4 páginas)

| Página | Contenido |
|--------|-----------|
| `docs/openspec/structure.md` | Anatomía del directorio: cada fichero, por qué existe, cuándo se crea |
| `docs/openspec/steering.md` | Qué son los steering files, qué contiene cada uno, cuándo actualizarlos |
| `docs/openspec/milestones.md` | `milestones.yaml` + `todos/` — organización de trabajo |
| `docs/openspec/providers.md` | GitWorkflowConfig, GitHub provider, Null provider, wizard de setup |

### TUI Reference (3 páginas)

| Página | Contenido |
|--------|-----------|
| `docs/tui/overview.md` | Qué hace el TUI, cuándo usarlo vs solo skills, multi-project config |
| `docs/tui/keybindings.md` | Todas las teclas agrupadas por vista (desde README + pantallas extras) |
| `docs/tui/views.md` | Descripción de cada pantalla: EpicsView, ChangeDetail, SpecHealth, etc. |

### Best Practices (3 páginas)

| Página | Contenido |
|--------|-----------|
| `docs/best-practices/scope-control.md` | Regla de los 20 ficheros, cuándo dividir, cómo dividir con valor independiente |
| `docs/best-practices/atomic-commits.md` | One task = one file = one commit, cómo revisar, cómo revertir |
| `docs/best-practices/when-not-to-use-sdd.md` | Hotfixes, config, patches < 3 ficheros, urgencias |

## Criterios de éxito

- [ ] Las 10 páginas tienen contenido real (no "Coming soon")
- [ ] `mkdocs build --strict` pasa sin warnings
- [ ] Ninguna referencia a Parclick, proyectos internos ni terminología de empresa
- [ ] Tono y estilo coherente con las páginas ya escritas en `docs-site`
- [ ] Las páginas de keybindings y views son consistentes con la implementación real del TUI
