# Proposal: docs-site

## Descripción

Crear un sitio de documentación público con MkDocs Material, publicado en GitHub Pages, que cubra tanto la metodología SDD como el tooling (sdd-tui + skills). El site actúa como punto de entrada amigable para cualquier persona o equipo que quiera adoptar SDD en su proyecto.

## Motivación

sdd-tui es un repo público pero no tiene documentación más allá de un README. Las 14 skills están escritas como instrucciones para LLM — útiles para Claude Code, pero opacas para un lector humano que quiere entender qué hace el sistema. No existe un punto de entrada que explique qué es SDD, cuándo usarlo y cómo empezar.

Actualmente, para adoptar SDD hay que:
1. Leer el README (install)
2. Leer 14 archivos SKILL.md de forma lineal
3. Inferir el flujo a partir de la nomenclatura de skills

Un site de documentación convierte ese proceso en una experiencia guiada y estructurada.

## Alternativas consideradas

| Alternativa | Por qué descartada |
|-------------|-------------------|
| Docusaurus | React + npm — toolchain pesado para proyecto Python puro |
| GitBook | Dependencia de plataforma externa, no se puede self-host |
| Ampliar README | No escala; pierde estructura de navegación |
| Sphinx | Orientado a API docs Python, excesivo para contenido conceptual |

**MkDocs Material elegido:** zero JS toolchain, Markdown nativo, Mermaid integrado, GitHub Pages con 1 workflow file, `pip install mkdocs-material`.

## Scope

### IN

- `docs/` con estructura MkDocs: getting started, workflow, skills reference, TUI reference, best practices
- `mkdocs.yml` en raíz del repo
- `.github/workflows/docs.yml` para deploy automático en push a `main`
- Adaptación de `skills/*/SKILL.md` → prosa de usuario (no copiar raw: transformar instrucciones LLM → guía humana)
- Diagrama Mermaid del ciclo SDD completo
- Tutorial "first change" con ejemplo sintético (proyecto ficticio, sin referencias a Parclick)
- `openspec/` structure reference (qué es cada fichero y por qué existe)

### OUT

- Documentación auto-generada desde openspec de proyectos (eso es el change `sdd-docs-generator`)
- API reference de módulos Python internos del TUI
- `openspec/specs/github/` y `openspec/specs/tests/` (implementación interna del TUI)
- Integración con Algolia search (demasiado para v1)

## Idioma

**Inglés** como idioma principal. El site es público y su audiencia potencial es más amplia en inglés. El README en español se mantiene tal cual — son públicos distintos.

## Estructura del site

```
docs/
├── index.md                         ← What is SDD? (hero page)
├── getting-started/
│   ├── install.md                   ← Desde README (adaptado)
│   └── first-change.md              ← Tutorial end-to-end (nuevo)
├── workflow/
│   ├── overview.md                  ← Diagrama Mermaid + ciclo
│   ├── sdd-init.md
│   ├── sdd-new.md
│   ├── sdd-continue.md
│   ├── sdd-ff.md
│   ├── sdd-apply.md
│   ├── sdd-verify.md
│   └── sdd-archive.md
├── openspec/
│   ├── structure.md                 ← Anatomía del directorio
│   ├── steering.md                  ← Qué son los steering files
│   ├── milestones.md
│   └── providers.md
├── tui/
│   ├── overview.md                  ← Qué hace el TUI, cuándo usarlo
│   ├── keybindings.md               ← Todas las vistas
│   └── views.md                     ← Pantallas con ASCII/descripción
└── best-practices/
    ├── scope-control.md             ← Cuándo dividir changes
    ├── atomic-commits.md            ← One task = one file
    └── when-not-to-use-sdd.md       ← Hotfixes, config, small patches
```

## Impacto esperado

- Un lector puede pasar de "no sé qué es SDD" a "tengo mi primer change en pipeline" leyendo solo Getting Started
- Los skills dejan de ser una caja negra — cada uno tiene su página con propósito, cuándo usarlo, input/output esperado
- El TUI tiene referencia visual completa sin necesidad de instalarlo primero
- GitHub Pages indexable por buscadores — descubribilidad orgánica

## Criterios de éxito

- [ ] `mkdocs serve` funciona localmente sin errores
- [ ] GitHub Actions despliega correctamente en `gh-pages` en push a `main`
- [ ] Getting Started completo: install + first-change tutorial
- [ ] Las 8 skills principales tienen su página de referencia (no raw SKILL.md)
- [ ] Diagrama Mermaid del flujo completo renderiza correctamente
- [ ] Sin referencias a Parclick, proyectos internos ni terminología específica de empresa
- [ ] README.md no modificado (audiencias distintas)
