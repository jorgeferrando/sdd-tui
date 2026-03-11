# Proposal: decision-status-badges

## Descripción

Añadir un campo `status` a las decisiones de diseño (`locked` / `open` / `deferred`) y mostrarlo como badge visual en `DecisionsTimeline`.

## Motivación

Actualmente `DecisionsTimeline` muestra todas las decisiones como hechos consumados, sin distinguir su estado. En la práctica, algunas decisiones archivadas son permanentes (`locked`), otras están siendo revisadas (`open`) y otras se pospusieron sin resolver (`deferred`). Esta distinción tiene valor informativo para entender el estado real del diseño.

## Problema actual

- `Decision` dataclass no tiene campo `status`
- La tabla de decisiones en `design.md` solo tiene 3 columnas: `Decisión | Alternativa | Motivo`
- `DecisionsTimeline` renderiza todas las entradas igual (bullet blanco)
- No hay forma de saber si una decisión sigue vigente o fue reabierta

## Solución propuesta

### 1. Extender el formato de `design.md`

Añadir una 4ª columna opcional `Estado` a la tabla de decisiones:

```markdown
| Decisión | Alternativa | Motivo | Estado |
|---------|------------|--------|--------|
| Use X | Use Y | X is simpler | locked |
| Use Z | Keep current | Performance | open |
| Schema v2 | Schema v1 | TBD | deferred |
```

Las tablas de 3 columnas existentes son backwards-compatible: el parser asignará `status = "locked"` por defecto.

### 2. Extender `Decision` dataclass

```python
@dataclass
class Decision:
    decision: str
    alternative: str
    reason: str
    status: str = "locked"  # locked | open | deferred
```

### 3. Actualizar `extract_decisions()`

- Si la fila tiene 4 columnas → leer `status` del grupo 4
- Si tiene 3 columnas → `status = "locked"` (backwards compat)

### 4. Actualizar `DecisionsTimeline`

Añadir badge coloreado al lado de cada decisión:

| Status | Badge | Color |
|--------|-------|-------|
| `locked` | `[locked]` | dim (gris) |
| `open` | `[open]` | yellow |
| `deferred` | `[deferred]` | cyan |

Línea actual: `• {decision.decision}`
Línea nueva: `• [badge] {decision.decision}`

## Alternativas descartadas

| Alternativa | Motivo de descarte |
|------------|-------------------|
| Tag inline en texto (`[open] Use X`) | Rompe la semántica del campo; mezcla datos con metadatos |
| Archivo YAML separado de status | Sobrecarga: dos archivos para una sola tabla |
| Solo mostrar decisiones `locked` | Pierde visibilidad de las abiertas/diferidas |

## Impacto

- **Archivos afectados:** `core/spec_parser.py`, `tui/spec_evolution.py`, `tests/test_spec_parser.py`, `tests/test_tui_spec_evolution.py`
- **Backwards compatible:** tablas de 3 cols → `status = "locked"` automáticamente
- **Sin cambios en UI layout:** solo añade texto en la línea de cada decisión

## Criterios de éxito

- [ ] `Decision.status` existe con valor por defecto `"locked"`
- [ ] Tablas de 3 columnas parsean sin errores con `status = "locked"`
- [ ] Tablas de 4 columnas parsean `status` correctamente
- [ ] `DecisionsTimeline` muestra badge coloreado según status
- [ ] Tests pasan (+tests nuevos para status parsing y badge render)
