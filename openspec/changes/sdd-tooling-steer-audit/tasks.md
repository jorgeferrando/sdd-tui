# Tasks: SDD Tooling — Steering Generation + Architecture Audit

## Metadata
- **Change:** sdd-tooling-steer-audit
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Crear `~/.claude/skills/sdd-steer/SKILL.md` — skill para generar y sincronizar steering files
  - Commit: `[sdd-tooling-steer-audit] Add sdd-steer skill`

- [x] **T02** Crear `~/.claude/skills/sdd-audit/SKILL.md` — skill para auditar codebase contra conventions.md
  - Commit: `[sdd-tooling-steer-audit] Add sdd-audit skill`
  - Depende de: T01 (referencia a /sdd-steer en el prereq)

- [x] **T03** Modificar `~/.claude/skills/sdd-verify/SKILL.md` — añadir Paso 4b: audit opcional si existe conventions.md
  - Commit: `[sdd-tooling-steer-audit] Integrate sdd-audit as optional step in sdd-verify`
  - Depende de: T02

## Quality Gate Final

- [x] **QG** Revisar los tres archivos: estructura correcta, frontmatter válido, instrucciones completas
  - Verificar que `/sdd-steer` tiene bootstrap + sync documentados
  - Verificar que `/sdd-audit` tiene prereq check + reporte clasificado
  - Verificar que `sdd-verify` integra el paso sin romper el flujo existente

## Notas

- No hay tests (prompt skills — no código ejecutable)
- T01 antes de T02 porque sdd-audit referencia a `/sdd-steer` como prerequisito
- El QG es revisión manual de los SKILL.md — sin script automatizado
- Los skills se activan inmediatamente tras crear los archivos (sin instalación)
