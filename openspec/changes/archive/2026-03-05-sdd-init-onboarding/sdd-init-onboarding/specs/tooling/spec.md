# Spec: Tooling — SDD Init Onboarding

## Metadata
- **Dominio:** tooling
- **Change:** sdd-init-onboarding
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** approved

## Contexto

Ampliar `/sdd-init` con un flujo de onboarding guiado que recoge el contexto del proyecto
(stack, patrones, entorno disponible) y genera artefactos de steering que alimentan el resto
del flujo SDD. Añade además: verificación de bootstrap en `/sdd-apply`, y un mecanismo de
"skill vivo" por el que `project-rules.md` crece con las correcciones del usuario.

Este spec extiende `tooling/spec.md` v2.0 (linting + sdd-steer + sdd-audit).

---

## 4. SDD Init — Onboarding Guiado

### Skill `/sdd-init` (ampliado)

#### Fase 1 — Environment Discovery

- **REQ-ENV01** `[Event]` When `/sdd-init` is invoked, the skill SHALL scan the environment
  before asking any questions, detecting: active MCPs, installed runtimes (node, python, php,
  ruby, go, rust), CLI tools (git, gh, docker, uv, bun, composer), and running Docker containers.
- **REQ-ENV02** `[Event]` When source files or known config files exist in the project root
  (`package.json`, `pyproject.toml`, `composer.json`, `go.mod`, `Cargo.toml`, etc.),
  the skill SHALL derive the stack automatically and pre-fill questionnaire answers.
- **REQ-ENV03** `[Event]` When `openspec/steering/` already exists with content, the skill
  SHALL skip the onboarding questionnaire and display the current steering state instead.
- **REQ-ENV04** `[Ubiquitous]` The environment scan SHALL complete silently — no intermediate
  output until the summary is shown.

#### Fase 2 — Cuestionario Interactivo

- **REQ-Q01** `[Event]` When the project has no existing code, the skill SHALL present the
  full questionnaire covering: project description, audience, bounded context, stack, team
  size, rigor level, CI/CD, available MCPs, and preferred patterns.
- **REQ-Q02** `[Event]` When existing code is detected, the skill SHALL present a reduced
  questionnaire that confirms detected values and only asks for unresolvable gaps.
- **REQ-Q03** `[Ubiquitous]` For each technical decision with multiple valid options, the
  skill SHALL present trade-offs in plain language — advantages and disadvantages — without
  assuming prior technical knowledge.
- **REQ-Q04** `[Ubiquitous]` When Claude has high confidence in the best option given the
  project context (e.g. MVP solo, specific stack), the skill SHALL recommend it explicitly
  with a one-line justification. The user may accept or override.
- **REQ-Q05** `[Ubiquitous]` The questionnaire SHALL never require the user to know specific
  technology names to answer — all questions SHALL offer concrete options or "let Claude decide".

#### Fase 3 — Generación de Artefactos

- **REQ-ART01** `[Event]` When all questionnaire answers are collected, the skill SHALL
  generate the full `openspec/steering/` directory with seven files in parallel:
  `product.md`, `tech.md`, `structure.md`, `conventions.md`, `environment.md`,
  `project-skill.md`, `project-rules.md`.
- **REQ-ART02** `[Optional]` Where `mcp__context7` is available, the skill SHALL resolve
  library IDs for the detected stack dependencies and add documentation references to `tech.md`.
- **REQ-ART03** `[Ubiquitous]` The onboarding SHALL NOT block or fail if optional MCPs
  (Context7, Jira, Linear, etc.) are unavailable or unresponsive.
- **REQ-ART04** `[Ubiquitous]` `project-skill.md` SHALL act as an index file — referencing
  the other steering files — and SHALL NOT exceed 100 lines.
- **REQ-ART05** `[Ubiquitous]` `project-rules.md` SHALL be the primary file for granular
  implementation rules (naming, style, test patterns, library decisions). `conventions.md`
  SHALL only contain architectural decisions at RFC 2119 level.
- **REQ-ART06** `[Ubiquitous]` `environment.md` SHALL document the tools and MCPs confirmed
  as available, so subsequent skills can use them without re-scanning.

#### Integración con `sdd-audit`

- **REQ-AUDIT-EXT01** `[Event]` When `/sdd-audit` is invoked and `project-rules.md` exists,
  the skill SHALL read both `conventions.md` and `project-rules.md` as a unified ruleset.
- **REQ-AUDIT-EXT02** `[Ubiquitous]` Violations from `project-rules.md` SHALL follow the
  same severity classification (Critical/Important/Minor) as violations from `conventions.md`.
- **REQ-AUDIT-EXT03** `[Ubiquitous]` Rules in `project-rules.md` that duplicate linter
  coverage SHALL NOT generate audit violations — the audit remains semantic.

#### Estructura de `openspec/steering/`

```
openspec/steering/
├── product.md        ← qué construye, para quién, bounded context
├── tech.md           ← stack, versiones, dependencias clave, refs Context7
├── structure.md      ← organización del código, capas, flujo estándar
├── conventions.md    ← decisiones arquitecturales RFC 2119 (MUST/SHOULD/MAY)
├── environment.md    ← MCPs, CLI tools, contenedores disponibles confirmados
├── project-skill.md  ← índice del proyecto; referencia los demás archivos
└── project-rules.md  ← reglas granulares de implementación; crece con el proyecto
```

### Reglas de negocio

- **RB-INIT01:** El onboarding solo se ejecuta una vez por proyecto. Re-ejecutar `/sdd-init`
  en un proyecto con steering existente muestra el estado actual y ofrece sync (como `/sdd-steer sync`).
- **RB-INIT02:** `project-skill.md` es el punto de entrada que los demás skills cargan.
  Debe poder leerse en < 30 segundos — concisión obligatoria.
- **RB-INIT03:** Las decisiones tomadas durante el onboarding se registran en `conventions.md`
  como sección "## Decisiones de bootstrap" para trazabilidad.

---

## 5. SDD Apply — Bootstrap Verification

### Skill `/sdd-apply` (ampliado)

- **REQ-BOOT01** `[Event]` When `/sdd-apply` is invoked, the skill SHALL verify that
  `openspec/steering/conventions.md` exists before implementing any task.
- **REQ-BOOT02** `[Unwanted]` If `openspec/steering/conventions.md` does not exist, the
  skill SHALL stop and instruct the user to run `/sdd-init` first.
- **REQ-BOOT03** `[Event]` When bootstrap verification passes, the skill SHALL read
  `openspec/steering/conventions.md`, `openspec/steering/project-rules.md`, and
  `openspec/steering/tech.md` before starting implementation.
- **REQ-BOOT04** `[Optional]` Where `openspec/steering/project-skill.md` exists, the skill
  SHALL read it as the primary context entry point instead of reading individual files.

### Reglas de negocio

- **RB-BOOT01:** La lectura del steering es silenciosa — no se muestra al usuario a menos
  que encuentre algo relevante para la tarea actual.
- **RB-BOOT02:** Si algún archivo de steering no existe (excepto `conventions.md`), el skill
  continúa sin error — el steering es incremental.

---

## 6. Living Rules — Actualización de `project-rules.md`

- **REQ-LIVE01** `[Event]` When the user explicitly instructs Claude to remember a rule
  (e.g. "remember this", "always do X", "from now on use Y"), Claude SHALL add the rule to
  `project-rules.md` in RFC 2119 format and confirm what was saved.
- **REQ-LIVE02** `[Event]` When Claude detects an implicit correction during implementation
  (user overrides a decision Claude made), Claude SHALL ask: "¿Quieres que guarde esta
  regla en `project-rules.md` para el futuro?" before writing.
- **REQ-LIVE03** `[Ubiquitous]` Rules added to `project-rules.md` SHALL follow RFC 2119
  format with scope, level (MUST/SHOULD/MAY), rule, and one-line rationale.
- **REQ-LIVE04** `[Ubiquitous]` Granular implementation rules (style, naming, test patterns,
  library usage) SHALL go to `project-rules.md`. Architectural decisions SHALL go to
  `conventions.md`. Claude SHALL classify correctly.
- **REQ-LIVE05** `[Event]` When a rule is saved, Claude SHALL confirm: what the rule is,
  which file it was added to, and what triggered it (explicit request or detected correction).
- **REQ-LIVE06** `[Unwanted]` If `project-rules.md` does not exist when a rule needs saving,
  Claude SHALL create it before writing.

### Reglas de negocio

- **RB-LIVE01:** Una corrección del usuario es una regla, no una excepción puntual. Si el
  usuario corrige lo mismo dos veces, la segunda vez Claude guarda sin preguntar.
- **RB-LIVE02:** `project-rules.md` NO tiene límite de tamaño, pero se organiza por secciones
  temáticas (## Style, ## Tests, ## Architecture, etc.) para mantener legibilidad.
- **RB-LIVE03:** Las reglas guardadas se aplican en la misma sesión desde el momento en que
  se guardan — no solo en sesiones futuras.

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Skill local en `openspec/steering/` | Skill global en `~/.claude/skills/{project}/` | El skill del proyecto viaja con el proyecto; no contamina el entorno global |
| `project-skill.md` como índice pequeño | Un único archivo grande | Mantiene el contexto inicial conciso; detalles en archivos referenciados |
| `project-rules.md` separado de `conventions.md` | Un solo archivo | `sdd-audit` usa `conventions.md` como fuente de arquitectura; las reglas granulares no deben contaminarla |
| Preguntar antes de guardar (detección implícita) | Guardar silenciosamente | El usuario mantiene control; evita guardar interpretaciones incorrectas |
| Context7 opcional, no bloqueante | Requerido para tech.md | No todos los proyectos tienen Context7 disponible; el onboarding debe funcionar offline |
| `sdd-audit` lee ambos archivos (`conventions.md` + `project-rules.md`) | Solo `conventions.md` | Ambos usan RFC 2119; las living rules deben enforcarse para que "corrections stick". El filtro semántico natural evita duplicar lo que ya caza el linter |

## Abierto / Pendiente

- [ ] Estrategia de actualización de skills instalados cuando sdd-tui se actualiza
  (diferido a `sdd-setup-experience`)
