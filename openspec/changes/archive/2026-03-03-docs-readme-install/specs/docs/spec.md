# Spec: README — Instalación desde GitHub

## Metadata
- **Dominio:** docs
- **Change:** docs-readme-install
- **Fecha:** 2026-03-03
- **Estado:** approved

## Comportamiento Esperado

Un usuario que llega al repositorio de GitHub debe poder:

1. Entender qué hace la herramienta en 2-3 líneas
2. Instalarla sin clonar el repo con un único comando
3. Saber qué prerequisito necesita (`openspec/` local)
4. Ejecutarla

## Contenido requerido en el README

| Sección | Contenido |
|---------|-----------|
| Descripción | 1-2 frases sobre qué hace sdd-tui |
| Install | `pip`, `uv tool install`, `pipx` — los tres métodos |
| Prerequisito | `openspec/` inicializado con `sdd-init` |
| Usage | `sdd-tui` (cwd) y `sdd-tui /ruta/openspec` |
| Stack | Python + Textual, uv |

## Reglas

- **RB-D1:** Los comandos de instalación deben funcionar tal como aparecen en el README.
- **RB-D2:** No mencionar dependencias que no se usan (Jira API, pygit2).
- **RB-D3:** No describir vistas como "no implementadas" — todas están implementadas.
