# Tasks: OpenSpec Index Bootstrap

## Metadata
- **Change:** openspec-index-bootstrap
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Modificar `skills/sdd-archive/SKILL.md` — añadir lógica de bootstrap al inicio del Paso 2b
  - Si INDEX.md no existe Y specs/ tiene dominios → generar INDEX.md desde cero
  - Mismo cambio en `~/.claude/skills/sdd-archive/SKILL.md`
  - Commit: `[openspec-index-bootstrap] Bootstrap INDEX.md in sdd-archive when missing`

## Quality Gate Final

- [x] **QG** Verificar coherencia
  - Confirmar que el flujo "no existe → bootstrap → update" es correcto en el skill
  - Confirmar que "no existe + specs/ vacío → saltar" está cubierto
  - Confirmar que el caso "existe → comportamiento anterior" no cambió

## Notas

- Sin tests Python — solo skill Markdown
- T01 modifica 1 archivo en 2 ubicaciones (repo + ~/.claude)
