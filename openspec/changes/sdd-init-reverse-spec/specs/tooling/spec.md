# Spec: Tooling — sdd-discover (Reverse-Spec)

## Metadata
- **Dominio:** tooling
- **Change:** sdd-init-reverse-spec
- **Fecha:** 2026-03-11
- **Versión:** 5.2 (delta sobre 5.1)
- **Estado:** draft

---

## Contexto

Cuando `sdd-init` se ejecuta en un proyecto con código existente, `openspec/specs/`
queda vacío. El desarrollador parte de cero para documentar los dominios de un sistema
que ya existe. Este change añade un hint en `sdd-init` y un nuevo skill `/sdd-discover`
que analiza el codebase y genera specs canónicas iniciales marcadas como inferidas.

## Comportamiento Actual

`sdd-init` termina con `openspec/specs/` vacío en cualquier caso — proyecto nuevo o existente.
No existe ningún comando que analice código existente para generar specs.

---

## 9. sdd-init — Hint de Canon Inicial

Extensión del skill `/sdd-init` existente (ver sección 4 del spec canónico).

### Requisitos

- **REQ-HINT-01** `[Event]` When `/sdd-init` completes and `openspec/specs/` is empty,
  the skill SHALL display a hint: `"sin canon inicial — ejecuta /sdd-discover para
  analizar el codebase existente"`.

- **REQ-HINT-02** `[State]` While `openspec/specs/` contains at least one spec file,
  the skill SHALL NOT display the hint.

- **REQ-HINT-03** `[Ubiquitous]` The hint SHALL appear as the last item in the "Próximos pasos"
  section of the init summary — it does not interrupt or alter the existing init flow.

### Reglas de negocio

- **RB-HINT01:** El hint es informativo — no bloquea ni lanza `/sdd-discover` automáticamente.
  El usuario decide cuándo ejecutarlo.
- **RB-HINT02:** La condición es `openspec/specs/` vacío (sin subdirectorios con spec.md),
  no "proyecto sin código". Un proyecto nuevo sin código también muestra el hint.

---

## 10. sdd-discover — Reverse-Spec desde Codebase Existente

### Skill `/sdd-discover`

Nuevo skill que analiza el codebase del proyecto y genera specs canónicas iniciales
en `openspec/specs/` con `Status: inferred`.

### Flujo

```
/sdd-discover
│
├── Paso 1: Detectar dominios
│   ├── Inspeccionar estructura de directorios (src/, app/, lib/, tests/, etc.)
│   ├── Contar archivos fuente por directorio y extensión
│   └── Inferir N dominios candidatos
│
├── Paso 2: Mostrar resumen al usuario
│   ├── Lista de dominios detectados con conteo de archivos
│   └── Pedir confirmación antes de proceder
│
├── Paso 3: Analizar cada dominio (tras confirmación)
│   ├── Leer archivos representativos (Glob + Read)
│   ├── Inferir: propósito, entidades principales, comportamiento clave
│   └── Generar openspec/specs/{dominio}/spec.md (Status: inferred)
│
└── Paso 4: Actualizar/crear openspec/INDEX.md
```

### Requisitos

#### Detección de dominios

- **REQ-DISC-01** `[Event]` When `/sdd-discover` is invoked, the skill SHALL scan the
  project root to identify architectural domains by inspecting directory structure and
  file extensions (`.py`, `.ts`, `.php`, `.rb`, `.go`, `.rs`, `.java`).

- **REQ-DISC-02** `[Ubiquitous]` Domain detection SHALL consider top-level subdirectories
  under common source roots (`src/`, `app/`, `lib/`, `packages/`, project root) as domain
  candidates. `tests/`, `spec/`, `__tests__/` SHALL be treated as a single `tests` domain.

- **REQ-DISC-03** `[Unwanted]` If no source files are found, the skill SHALL stop and
  inform the user: `"No se detectó código fuente. El proyecto parece estar vacío."`.

#### Resumen interactivo

- **REQ-DISC-04** `[Event]` When domains are identified, the skill SHALL present a summary
  list before proceeding:
  ```
  Dominios detectados:
    - core      (src/core/  — 12 archivos .py)
    - tui       (src/tui/   — 8 archivos .py)
    - tests     (tests/     — 24 archivos .py)

  ¿Proceder con el análisis? [S/n]
  ```

- **REQ-DISC-05** `[Event]` When the user confirms, the skill SHALL proceed to analyze
  all detected domains. When the user declines, the skill SHALL stop without creating files.

#### Generación de specs

- **REQ-DISC-06** `[Event]` When analyzing each domain, the skill SHALL delegate the analysis
  to a subagent with its own isolated context. Each subagent receives: the domain path, the
  list of files in that domain, and the output format (canonical spec template). The subagent
  reads files until it has enough context to describe the domain's purpose and main entities,
  prioritizing entry points, models, and public interfaces.

- **REQ-DISC-06b** `[Ubiquitous]` Subagents SHALL run in parallel — each writes its spec to
  `openspec/specs/{dominio}/spec.md` independently. The orchestrating agent only receives the
  completion status per domain, not the full spec content, keeping orchestrator context lean.

- **REQ-DISC-07** `[Event]` When generating a spec, the skill SHALL produce a valid canonical
  spec following the standard format (Metadata, Contexto, Comportamiento Actual, Requisitos EARS,
  Decisiones Tomadas, Abierto/Pendiente).

- **REQ-DISC-08** `[Ubiquitous]` All generated specs SHALL have `Status: inferred` in their
  Metadata section to distinguish them from validated specs written via `/sdd-spec`.

- **REQ-DISC-09** `[Ubiquitous]` REQs in inferred specs SHALL be marked with a comment
  `<!-- inferred — validate with /sdd-spec -->` at the end of the Requisitos section.

- **REQ-DISC-10** `[Ubiquitous]` Inferred specs SHALL include a closing note:
  `> Spec generada automáticamente por /sdd-discover. Validar y completar con /sdd-spec.`

- **REQ-DISC-11** `[Unwanted]` If a spec already exists at `openspec/specs/{dominio}/spec.md`,
  the skill SHALL skip that domain and inform the user: `"[dominio] — ya existe spec, omitido"`.

#### INDEX.md

- **REQ-DISC-12** `[Event]` When all domain specs are generated, the skill SHALL create or
  update `openspec/INDEX.md` with an entry per domain using the standard format.

- **REQ-DISC-13** `[Event]` When `openspec/INDEX.md` already exists, the skill SHALL only
  add entries for new domains — existing entries SHALL NOT be modified.

#### Resumen final

- **REQ-DISC-14** `[Event]` When the analysis completes, the skill SHALL display a summary:
  ```
  sdd-discover completado
  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  Specs generados:
    ✓ core    → openspec/specs/core/spec.md
    ✓ tui     → openspec/specs/tui/spec.md
    ✓ tests   → openspec/specs/tests/spec.md
  Omitidos: —

  Próximos pasos:
    Validar specs con /sdd-spec {dominio}
  ```

### Reglas de negocio

- **RB-DISC01:** `/sdd-discover` es idempotente — re-ejecutarlo en un proyecto donde todos
  los dominios ya tienen spec no genera ni modifica nada.
- **RB-DISC02:** La calidad de las specs inferidas es intencional-mente aproximada. Son un
  punto de partida, no la fuente de verdad. El `Status: inferred` es una señal explícita de ello.
- **RB-DISC03:** El skill no modifica `openspec/changes/` ni crea un change activo. Opera
  directamente sobre `openspec/specs/` — es infraestructura del proyecto, no una feature.
- **RB-DISC04:** El análisis es read-only sobre el código fuente — solo escribe en `openspec/`.
- **RB-DISC05:** Si el proyecto ya tiene steering (`openspec/steering/`), el skill MAY leer
  `structure.md` para mejorar la inferencia de dominios, pero no es obligatorio.

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Skill separado `/sdd-discover` en lugar de integrar en `sdd-init` | Fase 7 integrada en `sdd-init` | `sdd-init` se mantiene rápido y predecible; el análisis puede tardar en proyectos grandes |
| Hint al final de `sdd-init` para discoverar | Auto-ejecutar `sdd-discover` | No forzar análisis — el usuario decide cuándo está listo para el proceso |
| `Status: inferred` como diferenciador | Badge visual en SpecHealthScreen | Evita cambios en el TUI; el estado en el propio archivo es suficiente señal |
| Confirmación interactiva con listado previo | Análisis silencioso | El usuario valida dominios detectados antes de escribir archivos — evita specs erróneos |
| Specs directamente en `openspec/specs/` (no en un change) | Crear un change temporal | `sdd-discover` es bootstrapping del proyecto, no una feature en desarrollo |
| Subagente por dominio en paralelo | Análisis secuencial en un único contexto | Proyectos grandes pueden tener decenas de dominios; cada subagente tiene contexto limpio y la ejecución paralela reduce tiempo total |

## Abierto / Pendiente

- [ ] ¿`sdd-discover` debería poder recibir un argumento de dominio específico (`/sdd-discover core`) para análisis parcial?
