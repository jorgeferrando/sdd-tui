# Proposal: sdd-docs-generator

## Metadata
- **Change:** sdd-docs-generator
- **Fecha:** 2026-03-11
- **Estado:** draft

## Descripción

Añadir un generador automático de documentación MkDocs para proyectos con `openspec/`.
El sistema tiene dos capas independientes que se complementan:

1. **`sdd-docs` CLI (Python)** — scaffold mecánico: lee `openspec/` y genera
   `docs/` + `mkdocs.yml` con contenido estructurado derivado de los datos del spec
   (dominios, decisiones, changelog, tareas completadas). Sin prosa inventada —
   placeholders explícitos donde el contenido requiere inteligencia.

2. **`/sdd-docs` skill (Claude Code)** — capa inteligente: transforma los placeholders
   en prosa de usuario, detecta el tech stack desde `openspec/steering/`, y produce
   páginas completas listas para publicar. Invoca `sdd-docs` internamente si aún no
   se ha generado el scaffold.

## Motivación

El change `docs-site-content` requirió escribir manualmente 20+ páginas de documentación
para `sdd-tui`. Cualquier equipo que adopte SDD en un proyecto diferente (API PHP, frontend
Angular, microservicio, etc.) tiene que hacer ese mismo trabajo desde cero.

`openspec/` ya contiene toda la información necesaria:
- `specs/` → dominios y requisitos → secciones de referencia
- `changes/archive/` → historial completo → changelog automático
- `steering/` → tech stack, convenciones → contexto del proyecto
- `tasks.md` en cada change → ADRs implícitos

El generador convierte esa información en un site MkDocs de calidad sin trabajo manual.
`sdd-tui` es el caso de dogfooding: el propio site debería poder regenerarse con `sdd-docs`.

## Alternativas Consideradas

1. **Solo skill, sin CLI** — descartado. La generación mecánica de `mkdocs.yml` y estructura
   de archivos es determinista y no necesita LLM. Separar las capas evita gastar tokens
   en operaciones de filesystem.

2. **Integración directa en `sdd-tui` TUI** — descartado. Añade complejidad a la TUI sin
   beneficio; el CLI es más componible y testeable.

3. **Template Cookiecutter / Copier** — descartado. No lee `openspec/` real; produce
   estructura genérica vacía en lugar de contenido derivado del proyecto actual.

4. **Generador standalone (repo separado)** — descartado. Aumenta la fricción de instalación;
   distribuir como parte de `sdd-tui` aprovecha el canal ya existente (Homebrew + sdd-setup).

## Impacto

### Archivos nuevos
- `src/sdd_tui/docs_gen.py` — CLI entry point + generación de scaffold
- `~/.claude/skills/sdd-docs/SKILL.md` — skill para capa inteligente
- `tests/test_docs_gen.py` — tests unitarios del generador

### Archivos modificados
- `pyproject.toml` — nuevo entry point `sdd-docs`
- `openspec/specs/distribution/spec.md` — añadir dominio docs-generator
- `openspec/specs/tooling/spec.md` — referenciar el nuevo skill

### No modificado
- TUI (epics, change_detail, etc.) — fuera de scope
- `docs/` del propio repo — no se autoaplica en este change

## Criterios de Éxito

- `sdd-docs --help` muestra uso correcto
- `sdd-docs` ejecutado en el repo `sdd-tui` genera `docs/` y `mkdocs.yml` equivalentes
  al actual (estructura idéntica, contenido derivado de openspec/)
- `sdd-docs --dry-run` lista los archivos que se generarían sin escribirlos
- `/sdd-docs` skill documenta cómo usar el CLI y cómo completar la capa inteligente
- Tests cubren: generación de mkdocs.yml, pages por dominio, changelog, placeholder format
- 0 referencias hardcoded a `sdd-tui` en el generador — agnóstico al proyecto

## Scope Estimado

~6-8 archivos modificados/creados. Dentro del límite de 10.
