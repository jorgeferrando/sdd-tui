# Tasks: Convención de diagramas Mermaid en SDD docs

## Metadata
- **Change:** mermaid-diagrams
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [ ] **T01** Modificar `~/.claude/skills/sdd-design/SKILL.md` — reemplazar sección Arquitectura del template por guía Mermaid con regla ≥3 componentes y tabla de tipos
  - Commit: `[mermaid-diagrams] Add Mermaid diagram convention to sdd-design template`

- [ ] **T02** Modificar `~/.claude/skills/sdd-propose/SKILL.md` — añadir nota opcional de diagrama de contexto en template de Solución Propuesta
  - Commit: `[mermaid-diagrams] Add optional context diagram note to sdd-propose template`

## Quality Gate Final

- [ ] **QG** Verificar que los SKILL.md son sintácticamente correctos (markdown válido, sin bloques de código rotos)

## Notas

- T01 y T02 son independientes — no hay dependencia entre sí
- Sin tests (skills son prompt-only)
- Ediciones quirúrgicas: no alterar estructura ni orden de secciones
