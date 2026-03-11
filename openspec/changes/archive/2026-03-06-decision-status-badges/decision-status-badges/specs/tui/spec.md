# Spec: TUI — Decision status badges en DecisionsTimeline

## Metadata
- **Dominio:** tui
- **Change:** decision-status-badges
- **Fecha:** 2026-03-06
- **Versión:** 2.4
- **Estado:** approved

## Contexto

`DecisionsTimeline` muestra todas las decisiones igual, sin indicar su estado.
Este change añade un badge coloreado (`[locked]` / `[open]` / `[deferred]`)
al inicio de cada línea de decisión.

---

## Comportamiento Actual

Cada decisión se renderiza como:
```
  • {decision.decision}
    vs: {decision.alternative}
    why: {decision.reason}
```
Sin distinción visual de estado.

---

## Requisitos (EARS)

- **REQ-DSB-06** `[Event]` When `DecisionsTimeline` renders a decision with `status = "locked"`, the system SHALL prepend a `[locked]` badge in `dim` style.

- **REQ-DSB-07** `[Event]` When `DecisionsTimeline` renders a decision with `status = "open"`, the system SHALL prepend a `[open]` badge in `yellow` style.

- **REQ-DSB-08** `[Event]` When `DecisionsTimeline` renders a decision with `status = "deferred"`, the system SHALL prepend a `[deferred]` badge in `cyan` style.

- **REQ-DSB-09** `[Unwanted]` If `Decision.status` has an unrecognized value, the system SHALL render it as `[{status}]` in `dim` style (same as locked).

- **REQ-DSB-10** `[Ubiquitous]` The decision text (`decision.decision`) SHALL appear after the badge on the same line.

### Layout esperado

```
── my-change (2026-03-06) ──
  • [locked] Use X over Y
    vs: Use Y
    why: X is simpler
  • [open] Schema v2 migration
    vs: Schema v1
    why: Performance (under review)
  • [deferred] Add caching layer
    vs: No cache
    why: TBD
```

### Escenarios de verificación

**REQ-DSB-07** — badge open en amarillo
**Dado** una decisión con `status = "open"`
**Cuando** `DecisionsTimeline` renderiza el timeline
**Entonces** la línea de decisión contiene `[open]` en estilo `yellow`

**REQ-DSB-09** — valor desconocido
**Dado** una decisión con `status = "experimental"`
**Cuando** `DecisionsTimeline` renderiza el timeline
**Entonces** la línea muestra `[experimental]` en estilo `dim`

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Badge `[locked]` en dim (no verde) | Verde para locked | `locked` no es un estado positivo/negativo, es neutro; dim comunica "ya resuelto, no requiere atención" |
| Badge al inicio de la línea de decisión | Badge al final | Es lo primero que el ojo capta; permite escanear el estado de todas las decisiones de un vistazo |
| Valor desconocido → dim (no error) | Raise en render | Tolerancia a errores; el usuario ve el valor aunque no sea estándar |
