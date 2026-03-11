# Spec: Tooling — OpenSpec Index Bootstrap

## Metadata
- **Dominio:** tooling
- **Change:** openspec-index-bootstrap
- **Jira:** —
- **Fecha:** 2026-03-11
- **Versión:** 5.1
- **Estado:** approved

## Contexto

El change `openspec-index` (v5.0) implementó el índice y enseñó a `sdd-archive` a
mantenerlo. Pero el Paso 2b salta silenciosamente si `openspec/INDEX.md` no existe,
lo que significa que en proyectos nuevos el índice nunca se crea automáticamente.

Este delta extiende REQ-ARC-01 con la capacidad de bootstrap.

## Delta sobre v5.0

### Extensión de REQ-ARC-01

**REQ-ARC-01 (v5.0):** When closing a change that adds or modifies a canonical spec,
sdd-archive SHALL update the corresponding entries in `openspec/INDEX.md`.

**REQ-ARC-01 (v5.1 — este delta):** When closing a change that adds or modifies a
canonical spec:
- If `openspec/INDEX.md` **exists**: update the corresponding entries.
- If `openspec/INDEX.md` **does not exist** AND `openspec/specs/` contains at least
  one domain: **generate INDEX.md from scratch** by reading all canonical specs and
  creating one entry per domain.
- If `openspec/specs/` is empty: do not create INDEX.md.

### Nuevo requisito

- **REQ-BOOT-01** `[Event]` When sdd-archive runs Paso 2b and `openspec/INDEX.md`
  does not exist, the skill SHALL read all spec files in `openspec/specs/` and generate
  a complete INDEX.md with one entry per domain.

- **REQ-BOOT-02** `[Ubiquitous]` The generated INDEX.md SHALL follow the same format
  as a manually maintained index: header note, one `##` section per domain with path,
  summary, entities, and keywords.

- **REQ-BOOT-03** `[Unwanted]` If `openspec/specs/` is empty or does not exist,
  sdd-archive SHALL NOT create an empty INDEX.md.

- **REQ-BOOT-04** `[Ubiquitous]` After bootstrap generation, sdd-archive SHALL
  continue with the normal Paso 2b update logic (the newly generated INDEX.md now
  "exists" for the purpose of updating entries of the current change).

## Escenarios de verificación

**REQ-BOOT-01 — Bootstrap en proyecto nuevo**
**Dado** que `openspec/INDEX.md` no existe
**Y** que `openspec/specs/` contiene dominios `core`, `tui`, `github`
**Cuando** sdd-archive cierra un change que modifica `specs/github/spec.md`
**Entonces** genera `openspec/INDEX.md` con entradas para los 3 dominios
**Y** la entrada de `github` refleja el estado post-merge del change actual

**REQ-BOOT-03 — No crear índice vacío**
**Dado** que `openspec/INDEX.md` no existe
**Y** que `openspec/specs/` está vacío (primer change sin specs)
**Cuando** sdd-archive cierra el change
**Entonces** no crea `openspec/INDEX.md`

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Bootstrap en sdd-archive (no en sdd-init) | Crear en sdd-init | sdd-init no tiene specs aún; archive es el momento correcto (specs ya mergeadas) |
| Leer todas las specs al bootstrappear | Solo la del change actual | El índice debe ser completo desde el primer momento |
| No crear INDEX.md si specs/ está vacío | Crear vacío y rellenar después | Un índice vacío aporta cero valor y confunde |
