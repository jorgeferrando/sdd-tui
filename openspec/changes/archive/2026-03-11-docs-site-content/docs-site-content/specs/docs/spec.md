# Spec: Docs — Content Completion (openspec Ref + TUI Ref + Best Practices)

## Metadata
- **Dominio:** docs
- **Change:** docs-site-content
- **Fecha:** 2026-03-11
- **Versión:** 1.1 (delta sobre v1.0)
- **Estado:** approved

## Contexto

Completa los REQ-08, REQ-09 y REQ-10 de la spec `docs` v1.0, que quedaron como stubs en `docs-site`.

## Requisitos (delta)

- **REQ-08** `[Ubiquitous]` The openspec Reference section SHALL document: full directory structure with purpose of each file, steering files (one sub-section per file), milestones.yaml format, todos/ directory, and provider configuration (GitHub + Null).

- **REQ-09** `[Ubiquitous]` The TUI Reference section SHALL document: what sdd-tui does vs using skills alone, multi-project config.yaml, all keybindings grouped by view (View 1, View 2, View 8, View 9, Viewers, Global), and all screens with purpose and navigation.

- **REQ-10** `[Ubiquitous]` The Best Practices section SHALL cover: the 20-file limit rule with how to split, one-task-one-file-one-commit discipline with examples of good/bad commits, and three explicit cases where SDD adds more friction than value (hotfixes, config-only changes, < 3 file patches).

- **REQ-18** `[Ubiquitous]` After this change, `mkdocs build --strict` SHALL produce zero warnings (no "Coming soon" stubs remaining in nav).
