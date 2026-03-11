# Spec: Core — Decision status badges

## Metadata
- **Dominio:** core
- **Change:** decision-status-badges
- **Fecha:** 2026-03-06
- **Versión:** 1.4
- **Estado:** approved

## Contexto

Extensión del modelo de datos de decisiones de diseño. Las decisiones extraídas
de `design.md` ahora tienen un campo `status` que indica si la decisión es
definitiva, está siendo revisada o fue diferida.

---

## Comportamiento Actual

`Decision` tiene 3 campos: `decision`, `alternative`, `reason`.
`extract_decisions()` parsea tablas de 3 columnas. No hay concepto de estado.

---

## Requisitos (EARS)

- **REQ-DSB-01** `[Ubiquitous]` The `Decision` dataclass SHALL have a `status` field of type `str` with default value `"locked"`.

- **REQ-DSB-02** `[Event]` When `extract_decisions()` parses a decisions table row with 4 columns, the system SHALL assign the 4th column value as `Decision.status`.

- **REQ-DSB-03** `[Event]` When `extract_decisions()` parses a decisions table row with 3 columns (legacy), the system SHALL assign `status = "locked"` to that decision.

- **REQ-DSB-04** `[Ubiquitous]` The valid status values SHALL be `"locked"`, `"open"`, and `"deferred"`. Any other value SHALL be stored as-is without error.

- **REQ-DSB-05** `[Ubiquitous]` All existing archived design files with 3-column tables SHALL parse without errors and produce decisions with `status = "locked"`.

### Escenarios de verificación

**REQ-DSB-02** — tabla de 4 columnas
**Dado** un `design.md` con tabla `| Decisión | Alternativa | Motivo | Estado |`
**Cuando** se llama a `extract_decisions()`
**Entonces** `Decision.status` toma el valor del campo `Estado`

**REQ-DSB-03** — tabla de 3 columnas (backwards compat)
**Dado** un `design.md` con tabla `| Decisión | Alternativa | Motivo |` (sin columna Estado)
**Cuando** se llama a `extract_decisions()`
**Entonces** `Decision.status == "locked"` en todos los registros

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| 4ª columna opcional en tabla existente | Archivo YAML separado | Mantiene todo en un solo lugar; menos fricción al editar design.md |
| Default `"locked"` para tablas de 3 cols | Default `"open"` | Las decisiones archivadas ya están tomadas; `locked` es el estado natural |
| Almacenar valor raw sin validar | Raise error si valor inválido | La TUI puede mostrar el valor desconocido; mejor tolerancia a errores |
