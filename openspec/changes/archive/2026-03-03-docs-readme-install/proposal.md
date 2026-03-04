# Proposal: README actualizado con instrucciones de instalación

## Metadata
- **Change:** docs-readme-install
- **Jira:** N/A
- **Fecha:** 2026-03-03

## Problema

El README describe el estado inicial del proyecto (diseño conceptual, vistas no
implementadas, dependencias que no se usan como Jira REST API o pygit2). Un usuario
que llega al repo no sabe cómo instalar ni usar la herramienta.

## Solución Propuesta

Reescribir `README.md` con:
- Descripción real del proyecto
- Instrucciones de instalación desde GitHub (`pip`, `uv tool`, `pipx`)
- Instrucciones de uso (`sdd-tui` + prerequisito `openspec/`)
- Stack real y vistas implementadas

El `pyproject.toml` ya está correctamente configurado — no requiere cambios.

## Impacto

- **Archivos:** 1 (`README.md`)
- **Dominio:** docs
- **Tests:** ninguno
