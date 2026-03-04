# Tasks: Distribución de SDD skills

## Metadata
- **Change:** docs-skills-install
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Setup

- [x] **SETUP** Crear directorio `skills/` y `scripts/` en el repo

## Skills genéricas (una por commit)

- [x] **T01** Crear `skills/sdd-init/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-init skill`

- [x] **T0X** Crear `skills/sdd-new/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-new skill`

- [x] **T0X** Crear `skills/sdd-explore/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-explore skill`

- [x] **T0X** Crear `skills/sdd-propose/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-propose skill`

- [x] **T0X** Crear `skills/sdd-spec/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-spec skill`

- [x] **T0X** Crear `skills/sdd-design/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-design skill`

- [x] **T0X** Crear `skills/sdd-tasks/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-tasks skill`

- [x] **T0X** Crear `skills/sdd-apply/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-apply skill`

- [x] **T0X** Crear `skills/sdd-verify/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-verify skill`

- [x] **T10** Crear `skills/sdd-archive/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-archive skill`

- [x] **T11** Crear `skills/sdd-continue/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-continue skill`

- [x] **T12** Crear `skills/sdd-ff/SKILL.md` — versión genérica
  - Commit: `[docs] Add generic sdd-ff skill`

## Script e integración

- [x] **T13** Crear `scripts/install-skills.sh` — modo interactivo + flags `--global`/`--local`
  - Commit: `[docs] Add install-skills.sh script`

- [x] **T14** Modificar `README.md` — añadir sección "Skills (Claude Code)"
  - Commit: `[docs] Add skills installation section to README`

## Quality Gate Final

- [x] **QG** Verificar script + skills
  - `bash scripts/install-skills.sh --local` desde el repo
  - Verificar que las skills aparecen en Claude Code con `/sdd-`

## Notas

- Skills completamente agnósticas: sin Parclick, sin Docker, sin scripts internos, sin DI-XXX obligatorio
- Solo skills SDD (12) — no incluir otras skills personales
- T01-T12 independientes entre sí (pueden hacerse en cualquier orden)
- T13 y T14 independientes de T01-T12 pero por claridad se hacen al final
