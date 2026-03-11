# Tasks: OpenSpec Index — Two-Level Lookup

## Metadata
- **Change:** openspec-index
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-11

## Tareas de Implementación

- [x] **T01** Crear `openspec/INDEX.md` — índice de los 8 dominios canónicos
  - Leer cada spec canónica y extraer sumario, entidades clave y keywords
  - Ordenar por tamaño descendente: tui → core → distribution → tooling → docs → tests → github → providers
  - Commit: `[openspec-index] Add openspec/INDEX.md with 8 domain entries`

- [x] **T02** Modificar `~/.claude/skills/sdd-explore/SKILL.md` — integrar lectura de INDEX.md en Paso 4
  - Añadir bloque al inicio del Paso 4: si INDEX.md existe, leerlo primero y cargar solo dominios relevantes
  - Incluir fallback explícito: si no existe → comportamiento actual
  - Commit: `[openspec-index] Update sdd-explore to read INDEX.md first`

- [x] **T03** Modificar `~/.claude/skills/sdd-archive/SKILL.md` — añadir Paso 2b
  - Insertar entre Paso 2 y Paso 3: actualizar entradas de INDEX.md tras merge de specs
  - Incluir aviso si dominio en specs/ no tiene entrada en INDEX.md
  - Commit: `[openspec-index] Update sdd-archive to maintain INDEX.md`

## Quality Gate Final

- [x] **QG** Verificar coherencia del índice
  - Confirmar que los 8 dominios en INDEX.md coinciden con `ls openspec/specs/`
  - Confirmar que las entidades listadas existen en el código (`src/sdd_tui/`)
  - Confirmar que el flujo en sdd-explore y sdd-archive es coherente con la spec

## Notas

- Sin tests Python — este change no toca código ejecutable
- T01 requiere leer los 8 specs canónicos para extraer entidades y keywords con precisión
- T02 y T03 son cambios quirúrgicos en los skills — no renumerar pasos existentes
- Orden obligatorio: T01 → T02 → T03 (el índice debe existir antes de actualizar los skills que lo referencian)
