# Tasks: sdd-init-reverse-spec

## Metadata
- **Change:** sdd-init-reverse-spec
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Crear `~/.claude/skills/sdd-discover/SKILL.md` — nuevo skill de reverse-spec con patrón orquestador + subagentes
  - Commit: `[sdd-init-reverse-spec] Add sdd-discover skill for codebase reverse-spec`

- [x] **T02** Modificar `~/.claude/skills/sdd-init/SKILL.md` — añadir hint en Paso 6 cuando `openspec/specs/` está vacío
  - Commit: `[sdd-init-reverse-spec] Add sdd-discover hint to sdd-init when specs/ is empty`
  - Depende de: T01 (el hint referencia un skill que ya debe existir)

- [x] **T03** Modificar `openspec/specs/tooling/spec.md` — merge delta, añadir secciones 9 y 10, bump a v5.2
  - Commit: `[sdd-init-reverse-spec] Update tooling spec to v5.2 with sdd-discover requirements`
  - Depende de: T01, T02 (se documenta lo ya implementado)

- [x] **T04** Modificar `openspec/INDEX.md` — actualizar entrada `tooling` con nuevos skills documentados
  - Commit: `[sdd-init-reverse-spec] Update INDEX.md tooling entry for v5.2`
  - Depende de: T03

## Bugs post-T04

- [x] **BUG01** `skills/sdd-discover/SKILL.md` — skill no añadido al directorio del repo (solo se creó en ~/.claude/skills/)
  - Fix: copiar desde ~/.claude/skills/sdd-discover/SKILL.md a skills/sdd-discover/SKILL.md
  - Commit: `[sdd-init-reverse-spec] Add sdd-discover skill to repo skills directory`

## Notas

- Sin quality gate de código — los skills son prompt-only (no hay tests ni lint aplicable)
- T01 es la tarea más extensa: incluye los 5 pasos del skill, el prompt del subagente y las reglas de inferencia de dominios
- El orden T01 → T02 es lógico (el hint de init menciona un skill que ya debe estar creado) pero no es una dependencia técnica estricta
