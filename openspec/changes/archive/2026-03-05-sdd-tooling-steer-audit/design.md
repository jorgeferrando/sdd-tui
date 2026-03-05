# Design: SDD Tooling — Steering Generation + Architecture Audit

## Metadata
- **Change:** sdd-tooling-steer-audit
- **Jira:** N/A
- **Proyecto:** skills globales (~/.claude/skills/)
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Dos nuevos SKILL.md en `~/.claude/skills/`. No hay código ejecutable —
son prompts estructurados que el agente sigue al invocarlos.

`sdd-steer` genera cuatro archivos de steering en `openspec/steering/` analizando
el codebase existente y los skills de arquitectura cargados. `sdd-audit` lee
`conventions.md` y analiza archivos modificados en el branch produciendo un
reporte clasificado con prompts `/sdd-new` para corrección.

## Arquitectura

```
/sdd-steer (bootstrap)
  → leer skills: {project}-architecture, {project}-code-quality
  → explorar codebase: src/, estructura de directorios, patrones de naming
  → generar openspec/steering/product.md
  → generar openspec/steering/tech.md
  → generar openspec/steering/structure.md
  → generar openspec/steering/conventions.md  ← el más valioso

/sdd-steer sync
  → leer openspec/steering/conventions.md
  → comparar contra skills actuales + código
  → proponer edits al usuario (no auto-modificar)

/sdd-audit [scope?]
  → leer openspec/steering/conventions.md  ← prereq
  → determinar archivos a analizar:
      sin scope → git diff --name-only {base}..HEAD
      con scope → ruta/directorio proporcionado
  → analizar cada archivo contra conventions
  → clasificar: Crítico / Importante / Menor
  → agrupar y generar prompts /sdd-new
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `~/.claude/skills/sdd-steer/SKILL.md` | Skill prompt | Genera y sincroniza steering files |
| `~/.claude/skills/sdd-audit/SKILL.md` | Skill prompt | Audita codebase contra conventions.md |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `~/.claude/skills/sdd-verify/SKILL.md` | Añadir Paso 4b: ejecutar `/sdd-audit` si existe `conventions.md` | REQ-AU08 — integración opcional en verify |

## Scope

- **Total archivos:** 3
- **Resultado:** Ideal (< 10)

## Contenido detallado — `sdd-steer/SKILL.md`

### Estructura del skill

```
Frontmatter (name, description)
Usage (bootstrap / sync)
Prerequisitos
Paso 1: Detectar proyecto y cargar skills de arquitectura
Paso 2: Explorar codebase (read-only)
Paso 3: Generar product.md
Paso 4: Generar tech.md
Paso 5: Generar structure.md
Paso 6: Generar conventions.md
  → Formato: ## {Área} — {Subárea} / MUST/SHOULD/MAY + razón
Modo Sync (detectado por arg "sync")
  → Comparar steering existente vs skills + código
  → Listar propuestas de cambio, esperar aprobación
Notas de calidad
```

### Contenido de `conventions.md` para sdd-tui (referencia)

El skill debe generar algo como:

```markdown
# Conventions: sdd-tui

## Python — Módulos
- **MUST** use `from __future__ import annotations` — forward references en Python 3.9+
- **MUST** place all imports before module-level code — PEP 8

## Textual — Navegación
- **MUST** use `push_screen` / `pop_screen` — no swap de widgets inline
- **MUST** use `call_after_refresh` for dynamic height calculations — Textual render order

## Tests — Patrones
- **MUST NOT** use `pilot.type()` — does not exist in Textual 8.x; use `widget.value = text`
- **MUST** use `@work(thread=True, exclusive=True)` for blocking subprocess workers

## Commits
- **MUST** follow format `[change-name] Description in English`
- **MUST** be atomic: one logical change, one file per commit
```

### Lógica de derivación de convenciones

El skill extrae convenciones de tres fuentes (en orden de prioridad):
1. **Skills de arquitectura/code-quality del proyecto** — fuente más confiable
2. **MEMORY.md del proyecto** — patrones clave ya descubiertos
3. **Código existente** — evidencia empírica (naming, estructura)

## Contenido detallado — `sdd-audit/SKILL.md`

### Estructura del skill

```
Frontmatter (name, description)
Usage (/sdd-audit / /sdd-audit src/Handler/)
Prerequisitos (conventions.md debe existir)
Paso 1: Verificar prereq — si no existe conventions.md → stop + instrucción
Paso 2: Determinar scope
  → sin arg: git diff --name-only {base}..HEAD (o main..HEAD)
  → con arg: los archivos/directorio proporcionados
Paso 3: Analizar cada archivo
  → leer conventions.md
  → para cada archivo del scope: verificar cada MUST/MUST NOT
  → anotar violaciones con archivo:línea aproximada
Paso 4: Clasificar
  → Crítico: viola MUST/MUST NOT
  → Importante: viola SHOULD
  → Menor: viola MAY
Paso 5: Generar reporte
  → formato estándar (ver spec)
  → agrupar /sdd-new prompts por área
Paso 6: Si cero violaciones → mensaje limpio
```

## Modificación de `sdd-verify/SKILL.md`

Añadir al final del checklist (tras "Spec Compliance") un paso opcional:

```markdown
## Paso 4b: Architecture Audit (si existe conventions.md)

Si `openspec/steering/conventions.md` existe:
```bash
# Verificar existencia
ls openspec/steering/conventions.md
```
Si existe → ejecutar `/sdd-audit` sobre los archivos modificados.
Las violaciones críticas DEBEN corregirse antes de crear el PR.
Las importantes son informativas — documentar en tasks.md si se difieren.
Si no existe → saltar este paso.
```

## Patrones Aplicados

- **Skill como prompt estructurado**: mismo patrón que todos los skills SDD existentes — frontmatter YAML + secciones markdown con instrucciones imperativas para el agente.
- **Prerequisito explícito**: `sdd-audit` para si no tiene su prereq, igual que `sdd-apply` requiere `tasks.md`.
- **Degradación opcional**: la integración en `sdd-verify` usa SHOULD, no MUST — no rompe flujos existentes.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Skill como SKILL.md (prompt) | Script Python ejecutable | No hay lógica computacional — es análisis del agente sobre el código |
| Scope por defecto = archivos modificados en branch | Todo el codebase | Más relevante en el contexto de PR; menos ruido |
| `conventions.md` como prereq hard para audit | Audit sin steering | Sin base de convenciones el audit no tiene referencia — falsos positivos |
| Integración en verify como paso opcional (SHOULD) | Blocking (MUST) | No todos los proyectos tienen steering todavía |
| Modificar sdd-verify en lugar de crear sdd-verify-v2 | Skill nuevo | El cambio es aditivo y pequeño — no justifica un nuevo skill |

## Notas de Implementación

- Los SKILL.md van en `~/.claude/skills/{name}/SKILL.md` — estructura estándar del sistema de skills.
- El frontmatter debe incluir `name` y `description` para que Claude Code lo registre como skill invocable.
- La `description` debe incluir el usage pattern (e.g. "Uso - /sdd-steer o /sdd-steer sync") — aparece en la lista de skills disponibles.
- `sdd-steer` debe detectar el proyecto desde el working directory (igual que `session-init`) para cargar los skills de arquitectura correctos.
