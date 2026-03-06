# Spec: Core — repair_hints

## Metadata
- **Dominio:** core
- **Change:** spec-health-hints
- **Fecha:** 2026-03-06
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Añadir `repair_hints(metrics, change) -> list[str]` en `core/metrics.py`.
Función pura que infiere el hint de acción más urgente para un change dado su
estado de pipeline y sus métricas de calidad de spec.

Sin estado propio. Retorna lista ordenada por prioridad (el primero es el más urgente).
Consumida por `SpecHealthScreen` para mostrar la columna `HINT`.

## ADDED

### `repair_hints` — Generador de hints de reparación

**Dado** un `change: Change` con su `pipeline` poblado y un `metrics: ChangeMetrics`
**Cuando** se llama a `repair_hints(metrics, change)`
**Entonces** se retorna una lista de strings con los hints, ordenados de mayor a menor urgencia

```python
def repair_hints(metrics: ChangeMetrics, change: Change) -> list[str]: ...
```

### Lógica de prioridad

Los hints se evalúan en el siguiente orden; el primero que aplique se incluye primero:

| Prioridad | Condición | Hint |
|-----------|-----------|------|
| 1 | `pipeline.propose == PENDING` | `/sdd-propose {name}` |
| 2 | `pipeline.spec == PENDING` | `/sdd-spec {name}` |
| 3 | `pipeline.design == PENDING` | `/sdd-design {name}` |
| 4 | `pipeline.tasks == PENDING` | `/sdd-tasks {name}` |
| 5 | `pipeline.apply == PENDING` | `/sdd-apply {name}` |
| 6 | `pipeline.verify == PENDING` | `/sdd-verify {name}` |
| 7 | spec existe y `req_count == 0` | `add REQ-XX tags` |
| 8 | `req_count > 0` y `ears_count < req_count` | `add EARS tags` |
| 9 | Ninguno anterior | `✓` |

### Requisitos (EARS)

- **REQ-RH-01** `[Event]` When `repair_hints(metrics, change)` is called, the function SHALL return a non-empty list with at least one hint string.
- **REQ-RH-02** `[Ubiquitous]` The function SHALL evaluate hints in priority order 1→9; each hint that applies SHALL appear before any lower-priority hint.
- **REQ-RH-03** `[Ubiquitous]` Pipeline hints (1–6) SHALL take precedence over spec quality hints (7–8).
- **REQ-RH-04** `[Ubiquitous]` When all pipeline phases are DONE and all quality checks pass, the function SHALL return `["✓"]`.
- **REQ-RH-05** `[Unwanted]` If `pipeline.spec == PENDING`, the function SHALL NOT include spec quality hints (7–8) — they are irrelevant when the spec does not exist yet.
- **REQ-RH-06** `[Ubiquitous]` Hint strings for pipeline phases SHALL include the change name: `/sdd-{phase} {change.name}`.
- **REQ-RH-07** `[Ubiquitous]` The function SHALL NOT raise exceptions for any combination of input values.

### Escenarios de verificación

**REQ-RH-02** — Pipeline incompleto toma prioridad sobre calidad
**Dado** un change con `pipeline.spec == DONE`, `pipeline.design == PENDING`, `req_count == 0`
**Cuando** se llama a `repair_hints`
**Entonces** el primer hint es `/sdd-design {name}` (no `add REQ-XX tags`)

**REQ-RH-05** — Sin spec, no se sugieren tags de REQ
**Dado** un change con `pipeline.spec == PENDING`
**Cuando** se llama a `repair_hints`
**Entonces** el primer hint es `/sdd-spec {name}`, y `add REQ-XX tags` no aparece

**REQ-RH-04** — Todo completo
**Dado** un change con todos los pipeline DONE, `req_count > 0`, `ears_count == req_count`
**Cuando** se llama a `repair_hints`
**Entonces** retorna `["✓"]`

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Retornar lista (no solo el primero) | Solo el hint más urgente | La TUI muestra el primero; tests pueden verificar el orden completo |
| Usar `change.pipeline` (ya poblado) | Re-inferir desde `metrics.artifacts` | `Pipeline` es la fuente de verdad, ya está calculado en `Change` |
| Hint de inactividad eliminado | Prioridad 9: `resume: /sdd-apply {name}` si inactive > threshold | Si `apply == PENDING`, ya hay hint `/sdd-apply`. Si todo está done, inactividad no es un problema accionable. Redundante. |
| `✓` como único elemento de la lista | `[]` vacío | Lista vacía requiere manejo especial en la TUI; `"✓"` es explícito |

## Abierto / Pendiente

Ninguno.
