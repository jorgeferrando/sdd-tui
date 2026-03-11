# Spec: Tooling — OpenSpec Index (Two-Level Lookup)

## Metadata
- **Dominio:** tooling
- **Change:** openspec-index
- **Jira:** —
- **Fecha:** 2026-03-11
- **Versión:** 5.0
- **Estado:** draft

## Contexto

A medida que `openspec/specs/` crece, los skills SDD (sdd-explore, sdd-spec, sdd-design)
consumen cada vez más tokens para orientarse: actualmente 8 dominios × ~400 líneas promedio
= ~3300 líneas = 5000-8000 tokens solo para saber qué specs existen y de qué tratan.

Este cambio introduce un índice de dos niveles: `openspec/INDEX.md` como nivel 1
(orientación rápida, ~300 tokens) y los spec files individuales como nivel 2
(detalle solo cuando es relevante).

## Comportamiento Actual

`sdd-explore` lista `openspec/specs/` y lee specs ad-hoc según el nombre del dominio.
No existe ningún mecanismo de indexado — la exploración es lineal y crece con el número
de dominios.

## Requisitos (EARS)

### INDEX.md — Estructura y contenido

- **REQ-IDX-01** `[Ubiquitous]` The `openspec/INDEX.md` SHALL exist at the root of `openspec/`
  and cover all canonical domains present in `openspec/specs/`.

- **REQ-IDX-02** `[Ubiquitous]` Each domain entry SHALL contain:
  path to spec file, one-paragraph summary (≤ 2 lines), key entities/symbols, and keywords.

- **REQ-IDX-03** `[Ubiquitous]` The INDEX.md SHALL include a header note explaining its purpose
  and instructing readers to use it for orientation before loading individual specs.

- **REQ-IDX-04** `[Ubiquitous]` The INDEX.md SHALL remain under 400 lines regardless of the
  number of domains, enforcing conciseness per entry.

- **REQ-IDX-05** `[Unwanted]` If a domain in `openspec/specs/` has no entry in INDEX.md,
  the skill sdd-archive SHALL warn the user after closing a change.

### sdd-archive — Mantenimiento del índice

- **REQ-ARC-01** `[Event]` When closing a change that adds or modifies a canonical spec,
  sdd-archive SHALL update the corresponding entries in `openspec/INDEX.md`.

- **REQ-ARC-02** `[Event]` When closing a change that adds a new domain,
  sdd-archive SHALL add a new entry to `openspec/INDEX.md`.

- **REQ-ARC-03** `[Ubiquitous]` The INDEX.md update SHALL happen after merging delta specs
  into canonical specs (after current Step 2) and before moving the change to archive.

### sdd-explore — Uso del índice

- **REQ-EXP-01** `[Event]` When `openspec/INDEX.md` exists, sdd-explore SHALL read it as
  Step 0 before loading any individual spec file.

- **REQ-EXP-02** `[Event]` When INDEX.md is available, sdd-explore SHALL use it to identify
  1-3 relevant domains and load only those spec files.

- **REQ-EXP-03** `[Unwanted]` If `openspec/INDEX.md` does not exist, sdd-explore SHALL
  fall back to the current behavior (scan `openspec/specs/` directly) without error.

- **REQ-EXP-04** `[Ubiquitous]` The domain selection from INDEX.md SHALL be based on keyword
  matching between the change description and the `Keywords` field of each entry.

### sdd-spec — Uso del índice

- **REQ-SPEC-01** `[Event]` When `openspec/INDEX.md` exists, sdd-spec SHALL read it to
  identify the target domain before loading the full canonical spec.

- **REQ-SPEC-02** `[Unwanted]` If the target domain is not found in INDEX.md but exists
  in `openspec/specs/`, sdd-spec SHALL proceed normally and note the missing entry.

## Formato de INDEX.md

```markdown
# OpenSpec Index

> Índice de dominios canónicos. Actualizado por sdd-archive al cerrar cada change.
> **Uso:** leer este archivo primero; cargar solo los specs relevantes para el change.

---

## {domain} (`specs/{domain}/spec.md`)
{Descripción en 1-2 líneas: qué cubre este dominio, qué problema resuelve.}
**Entidades:** {Symbol1}, {Symbol2}, {function()}, {ClassName}
**Keywords:** {keyword1}, {keyword2}, {keyword3}
```

## Escenarios de verificación

**REQ-EXP-01/02 — Orientación rápida con índice**
**Dado** que `openspec/INDEX.md` existe con 8 entradas
**Cuando** sdd-explore arranca para un change sobre "PR status in pipeline"
**Entonces** lee INDEX.md (1 archivo, ~300 tokens), identifica dominios `github` y `tui`,
y carga solo `specs/github/spec.md` + `specs/tui/spec.md` (~250 líneas)
en lugar de las 3308 líneas totales

**REQ-EXP-03 — Fallback sin índice**
**Dado** que `openspec/INDEX.md` no existe (repo recién inicializado)
**Cuando** sdd-explore arranca
**Entonces** hace `ls openspec/specs/` y lee los spec files directamente (comportamiento actual)

**REQ-ARC-01 — Actualización tras archive**
**Dado** que un change modifica `specs/core/spec.md` añadiendo `VelocityMetrics`
**Cuando** sdd-archive cierra el change
**Entonces** actualiza la entrada `core` en INDEX.md con la nueva entidad en **Entidades**

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Markdown plano como formato | SQLite / JSON | Zero infraestructura; legible por humanos y Claude; no requiere herramientas |
| Mantenimiento manual + auto por sdd-archive | Solo auto-generado | Auto-generado puede perder contexto semántico; manual garantiza calidad |
| Fallback silencioso si no existe INDEX.md | Error o warning | Compatibilidad con repos existentes sin INDEX.md |
| Keywords como campo libre (no taxonomía formal) | Tags controlados | Menor coste de mantenimiento; suficiente para matching semántico |
| Límite de 400 líneas para INDEX.md | Sin límite | Previene que el índice se convierta en el problema que resuelve |

## Abierto / Pendiente

- [ ] ¿Añadir sección `depends_on` opcional por entrada? (evolución futura hacia grafo ligero — no bloquea)
