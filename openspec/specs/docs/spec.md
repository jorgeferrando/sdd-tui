# Spec: Docs — Documentation Site (MkDocs + GitHub Pages)

## Metadata
- **Dominio:** docs
- **Change:** docs-site
- **Fecha:** 2026-03-11
- **Versión:** 1.1
- **Estado:** canonical

## Contexto

sdd-tui es un repo público que carece de documentación navegable. Las 14 skills están escritas como instrucciones para LLM — operativas para Claude Code pero opacas para un lector humano. No existe un punto de entrada que explique qué es SDD, cuándo usarlo ni cómo empezar en un proyecto nuevo.

El site cubre dos audiencias:
- **Adopter:** alguien que quiere usar SDD en su proyecto y necesita entender el flujo completo.
- **User:** alguien que ya usa SDD/sdd-tui y necesita referencia rápida de keybindings o sintaxis de una skill.

## Comportamiento Actual

No existe `docs/`, no existe `mkdocs.yml`, no existe workflow de GitHub Actions. La única documentación es `README.md` (install + keybindings básicos, en español).

## Requisitos (EARS)

### Estructura y contenido

- **REQ-01** `[Ubiquitous]` The docs site SHALL be written entirely in English, with no references to Parclick, internal projects, or proprietary tooling.

- **REQ-02** `[Ubiquitous]` The docs site SHALL cover five sections: Getting Started, Workflow (skills), openspec Reference, TUI Reference, Best Practices.

- **REQ-03** `[Event]` When a reader lands on the home page, the site SHALL present a hero section that explains what SDD is, what problem it solves, and what the two tools are (skills + sdd-tui).

- **REQ-04** `[Ubiquitous]` The Getting Started section SHALL allow a reader to go from zero to a working first change without reading any other section.

- **REQ-05** `[Ubiquitous]` The Workflow section SHALL document each of the 8 core skills (sdd-init, sdd-new, sdd-ff, sdd-apply, sdd-verify, sdd-archive, sdd-continue, sdd-steer) as human-readable prose — not a copy of the raw SKILL.md instructions.

- **REQ-06** `[Ubiquitous]` Each skill page SHALL include: purpose (one sentence), when to use it, what it reads, what it produces, and at least one concrete example.

- **REQ-07** `[Ubiquitous]` The Workflow overview page SHALL include a Mermaid diagram showing the complete SDD cycle from init to archive.

- **REQ-08** `[Ubiquitous]` The openspec Reference section SHALL document the directory structure (each file and why it exists), steering files, milestones.yaml, todos/, and provider config.

- **REQ-09** `[Ubiquitous]` The TUI Reference section SHALL document all keybindings grouped by view, and describe each screen with its purpose and navigation.

- **REQ-10** `[Ubiquitous]` The Best Practices section SHALL cover: scope control (when to split a change), atomic commits (one task = one file), and when NOT to use SDD (hotfixes, config changes).

### Deploy y tooling

- **REQ-11** `[Event]` When a commit is pushed to `main`, the GitHub Actions workflow SHALL rebuild the MkDocs site and deploy it to `gh-pages` branch automatically.

- **REQ-12** `[Ubiquitous]` The site SHALL be buildable locally with `mkdocs serve` using only `pip install mkdocs-material`.

- **REQ-13** `[Ubiquitous]` The `mkdocs.yml` SHALL configure: site name, repo URL, Material theme with dark/light toggle, Mermaid support, and navigation matching REQ-02.

- **REQ-14** `[Ubiquitous]` The docs dependencies SHALL be isolated in an optional dependency group `[project.optional-dependencies] docs` in `pyproject.toml` — not added to main dependencies.

### Calidad y mantenibilidad

- **REQ-15** `[Ubiquitous]` Skills content SHALL be written as standalone prose — if the SKILL.md changes, the docs page may diverge and requires a manual update (no auto-sync in this change).

- **REQ-16** `[Ubiquitous]` The `README.md` SHALL NOT be modified — it serves a different audience (Spanish-speaking, quick install reference).

- **REQ-17** `[Unwanted]` If a docs page references a skill that does not exist in `skills/`, the build SHALL still succeed — no hard links between docs and skill files.

## Interfaces / Contratos

### Archivos producidos

```
docs/
├── index.md
├── getting-started/
│   ├── install.md
│   └── first-change.md
├── workflow/
│   ├── overview.md
│   ├── sdd-init.md
│   ├── sdd-new.md
│   ├── sdd-ff.md
│   ├── sdd-apply.md
│   ├── sdd-verify.md
│   ├── sdd-archive.md
│   ├── sdd-continue.md
│   └── sdd-steer.md
├── openspec/
│   ├── structure.md
│   ├── steering.md
│   ├── milestones.md
│   └── providers.md
├── tui/
│   ├── overview.md
│   ├── keybindings.md
│   └── views.md
└── best-practices/
    ├── scope-control.md
    ├── atomic-commits.md
    └── when-not-to-use-sdd.md

mkdocs.yml                         ← raíz del repo
.github/workflows/docs.yml         ← GitHub Actions deploy
pyproject.toml                     ← añadir [docs] optional deps
```

### mkdocs.yml (estructura mínima)

```yaml
site_name: SDD — Spec-Driven Development
repo_url: https://github.com/jorgeferrando/sdd-tui
theme:
  name: material
  palette:
    - scheme: default
      toggle: ...
    - scheme: slate
      toggle: ...
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          ...
```

### GitHub Actions workflow

```yaml
on:
  push:
    branches: [main]
    paths: ['docs/**', 'mkdocs.yml']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| MkDocs Material | Docusaurus | Zero JS toolchain; compatible con proyecto Python |
| Inglés como idioma principal | Español / bilingüe | Audiencia pública más amplia; README ya cubre ES |
| Skills como prosa (no raw SKILL.md) | Incluir SKILL.md directamente | SKILL.md son instrucciones para LLM, no guías de usuario |
| Optional deps group `[docs]` | Dev dependency | Quien usa sdd-tui no necesita mkdocs |
| Deploy solo en cambios a `docs/**` o `mkdocs.yml` | En cada push | Evita rebuilds innecesarios por cambios de código |
| README.md intacto | Reescribir en inglés | Audiencias distintas; no romper flujo de instalación actual |

## Abierto / Pendiente

- [ ] ¿El site vive en `jorgeferrando.github.io/sdd-tui` o se configurará un dominio propio? (no bloquea implementación — GitHub Pages por defecto)
- [ ] ¿sdd-audit y sdd-spec se incluyen en el Workflow section o solo las 8 core? (decisión editorial, no técnica)
