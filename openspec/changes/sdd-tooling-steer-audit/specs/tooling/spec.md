# Spec: Tooling — SDD Steer + SDD Audit Skills

## Metadata
- **Dominio:** tooling
- **Change:** sdd-tooling-steer-audit
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Delta sobre el spec canónico `tooling/spec.md` v1.0.

Dos nuevos skills globales (`~/.claude/skills/`) que cierran el gap entre
convenciones documentadas en los skills de arquitectura y el código real.

---

## 1. Skill `/sdd-steer`

### Propósito

Genera archivos de "steering" en `openspec/steering/` que capturan las
convenciones del proyecto en formato legible por el agente. Dos modos:
bootstrap (primera ejecución) y sync (actualización incremental).

### Archivos generados

```
openspec/steering/
├── product.md       ← qué construye el proyecto, para quién, dominio
├── tech.md          ← stack, versiones, herramientas clave, entornos
├── structure.md     ← organización del código, capas, qué hace cada directorio
└── conventions.md   ← reglas explícitas: naming, final, readonly, capas, etc.
```

`conventions.md` es el archivo de mayor valor. Captura reglas que causan
errores de PR pero no están en ningún README.

### Modo Bootstrap (`/sdd-steer`)

- **REQ-ST01** `[Event]` When the user invokes `/sdd-steer`, the skill SHALL create `openspec/steering/` if it does not exist.
- **REQ-ST02** `[Event]` When bootstrapping, the skill SHALL generate all four files (`product.md`, `tech.md`, `structure.md`, `conventions.md`).
- **REQ-ST03** `[Ubiquitous]` The skill SHALL derive conventions by reading: (a) existing architecture/code-quality skills for the project, (b) recent commit messages and PR reviews if available, (c) actual code patterns in the codebase.
- **REQ-ST04** `[Ubiquitous]` Each convention in `conventions.md` SHALL include: scope (e.g. "PHP — Classes"), rule level (MUST/SHOULD/MAY), and a one-line rationale.
- **REQ-ST05** `[Unwanted]` If `openspec/steering/` already has content, bootstrap SHALL warn the user and offer to run sync instead.

### Modo Sync (`/sdd-steer sync`)

- **REQ-ST06** `[Event]` When the user invokes `/sdd-steer sync`, the skill SHALL compare the current steering files against the actual codebase and skills.
- **REQ-ST07** `[Event]` When drift is detected (new convention not in steering, or documented convention no longer present), the skill SHALL propose specific edits to the affected file.
- **REQ-ST08** `[Ubiquitous]` Sync SHALL present proposed changes to the user before writing — it SHALL NOT auto-modify steering files.

### Formato de `conventions.md`

```markdown
# Conventions: {Proyecto}

## {Área} — {Subárea}
- **MUST** {regla} — {razón en una línea}
- **SHOULD** {regla} — {razón en una línea}

## PHP — Clases
- **MUST** use `final` keyword — inheritance not used by convention
- **MUST** declare all Request properties as `readonly` — immutability contract

## CQRS — Handlers
- **MUST NOT** inject Repository directly — only via interfaces
- **MUST** receive a single Command/Query object as parameter
```

### Reglas de negocio

- **RB-ST01:** El skill lee los architecture/code-quality skills del proyecto **antes** de explorar el código. Los skills son la fuente de verdad; el código es evidencia de implementación.
- **RB-ST02:** `conventions.md` usa niveles RFC 2119 (`MUST`, `MUST NOT`, `SHOULD`, `MAY`) — no lenguaje libre.
- **RB-ST03:** El steering vive en `openspec/steering/` — mismo espacio que el resto de openspec. Puede estar commiteado o excluido según la preferencia del proyecto.
- **RB-ST04:** El skill NO modifica skills existentes — solo genera/actualiza steering.
- **RB-ST05:** En sdd-tui, las convenciones a documentar incluyen: patrones Textual (push_screen/pop_screen, call_after_refresh, @work), naming de tests, formato de commits.

---

## 2. Skill `/sdd-audit`

### Propósito

Analiza el codebase contra el steering generado y produce un reporte de
violaciones clasificadas por severidad con prompts de corrección.

### Formato del reporte

```
## Audit Report — {proyecto} — {fecha}

### Crítico (bloquea PR review)
- [C01] `{ruta/archivo}:{línea}` — {descripción de la violación}
  - Convención: {referencia a conventions.md}
  - Fix: {qué cambiar}

### Importante (deuda técnica)
- [I01] `{ruta/archivo}:{línea}` — {descripción}

### Menor
- [M01] `{ruta/archivo}:{línea}` — {descripción}

## Acciones SDD

Para corregir críticos:
/sdd-new "fix: {descripción agrupada de los errores críticos}"

Para deuda técnica:
/sdd-new "refactor: {descripción agrupada}"
```

### Clasificación de violaciones

| Nivel | Criterio |
|-------|----------|
| **Crítico** | Viola una convención `MUST`/`MUST NOT`; habitualmente señalado en PR review |
| **Importante** | Viola una convención `SHOULD`; deuda técnica acumulable |
| **Menor** | Viola una convención `MAY`; estético o de preferencia |

### Comportamientos esperados

- **REQ-AU01** `[Event]` When the user invokes `/sdd-audit`, the skill SHALL read `openspec/steering/conventions.md` first.
- **REQ-AU02** `[Unwanted]` If `openspec/steering/conventions.md` does not exist, the skill SHALL instruct the user to run `/sdd-steer` first and stop.
- **REQ-AU03** `[Optional]` Where a scope is provided (`/sdd-audit src/Handler/`), the skill SHALL restrict analysis to that path.
- **REQ-AU04** `[Ubiquitous]` Without a scope argument, the skill SHALL analyze all files modified since the base branch (equivalent to `git diff --name-only {base}..HEAD`).
- **REQ-AU05** `[Ubiquitous]` Each violation SHALL include: file path, approximate line, violated convention, and a one-line fix suggestion.
- **REQ-AU06** `[Event]` When critical violations are found, the skill SHALL generate at least one `/sdd-new` prompt to initiate correction via SDD flow.
- **REQ-AU07** `[Unwanted]` If no violations are found, the skill SHALL output `No violations found — conventions upheld.`

### Integración con `/sdd-verify`

- **REQ-AU08** `[Optional]` Where `openspec/steering/conventions.md` exists, `/sdd-verify` SHOULD run `/sdd-audit` on changed files as an additional self-review step.

### Reglas de negocio

- **RB-AU01:** El audit es semántico, no sintáctico — complementa linters (ruff, PHPStan), no los reemplaza.
- **RB-AU02:** El audit NO modifica código — solo reporta y propone prompts.
- **RB-AU03:** Los prompts `/sdd-new` agrupan violaciones por dominio/área, no uno por violación.
- **RB-AU04:** El scope por defecto (archivos modificados en el branch) es intencional — el audit es más útil como quality gate en `/sdd-verify` que como análisis masivo del repo.
- **RB-AU05:** El skill puede ejecutarse sin steering si el usuario pasa una lista de convenciones inline, pero este caso de uso es secundario.

---

## 3. Preguntas Resueltas

| Pregunta | Decisión |
|----------|---------|
| ¿`openspec/steering/` va en el repo o excluido? | Decisión por proyecto. Por defecto excluido (`.git/info/exclude`), como el resto de openspec. En sdd-tui puede commitearse dado que openspec/ es público. |
| ¿`/sdd-audit` analiza archivos modificados o todo el codebase? | Por defecto archivos modificados en el branch (`git diff --name-only`). Scope explícito opcional. |
| ¿El audit se integra en `/sdd-verify`? | Opcional — si existe `conventions.md`, `/sdd-verify` SHOULD ejecutarlo. No es blocking. |

---

## Fuera de scope

- Integración del reporte de audit en View 8 (SpecHealthScreen) de sdd-tui — diferido.
- Generación automática de fixes (el skill reporta, no corrige).
- Soporte multi-proyecto en el audit (analiza un proyecto a la vez).
