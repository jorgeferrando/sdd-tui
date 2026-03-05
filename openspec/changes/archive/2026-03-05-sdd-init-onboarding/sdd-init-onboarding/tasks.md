# Tasks: SDD Init Onboarding

## Metadata
- **Change:** sdd-init-onboarding
- **Jira:** n/a
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05

## Tareas de Implementación

- [x] **T01** Crear `scripts/sdd-env-scan.sh` — script bash que detecta runtimes, CLI tools, Docker y stack desde config files
  - Commit: `[sdd-init-onboarding] Add sdd-env-scan.sh environment detection script`

- [x] **T02** Crear `skills/sdd-steer/SKILL.md` — añadir al repo el skill que faltaba en distribución (sin cambios de comportamiento)
  - Commit: `[sdd-init-onboarding] Add sdd-steer skill to repo distribution`

- [x] **T03** Crear `skills/sdd-audit/SKILL.md` — añadir al repo con soporte para `project-rules.md` como ruleset unificado junto a `conventions.md`
  - Commit: `[sdd-init-onboarding] Add sdd-audit skill with project-rules.md support`

- [x] **T04** Modificar `skills/sdd-apply/SKILL.md` — añadir Step 0: bootstrap verification + carga silenciosa del steering
  - Depende de: T01 (sdd-env-scan.sh define qué existe)
  - Commit: `[sdd-init-onboarding] Add bootstrap verification and steering load to sdd-apply`

- [x] **T05** Reescribir `skills/sdd-init/SKILL.md` — onboarding completo: skills check, env scan, cuestionario con trade-offs, generación de 7 artefactos de steering, living rules
  - Depende de: T01, T02, T03, T04
  - Commit: `[sdd-init-onboarding] Rewrite sdd-init with guided onboarding flow`

## Quality Gate Final

- [x] **QG** Verificación manual en los 4 escenarios del design:
  1. `/sdd-init` en proyecto nuevo (sin código) → cuestionario completo
  2. `/sdd-init` en proyecto con `package.json` → detección Node + cuestionario reducido
  3. `/sdd-apply` sin `openspec/steering/conventions.md` → para con mensaje claro
  4. `/sdd-audit` con `project-rules.md` presente → usa ambos archivos
  - No hay tests Python — skills son prompt-only

## Notas

- T05 es la tarea más compleja — el rewrite de sdd-init incluye las plantillas de los 7 archivos de steering
- T02 (sdd-steer) es una copia del skill instalado en `~/.claude/skills/sdd-steer/SKILL.md` — verificar que está actualizado antes de copiar
- Los commits de T02-T03 incluyen skills que antes no estaban en el repo — `install-skills.sh` los distribuirá automáticamente a partir de ahora
- Living rules (actualización de `project-rules.md` cuando el usuario corrige a Claude) se implementa como instrucciones en el skill sdd-init — no requiere archivo separado
