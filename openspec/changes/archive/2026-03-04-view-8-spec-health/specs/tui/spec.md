# Spec: TUI — View 8 (Spec Health Dashboard) + badge REQ en View 2

## Metadata
- **Dominio:** tui
- **Change:** view-8-spec-health
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** draft

## Contexto

View 8 añade una pantalla de salud de specs (`SpecHealthView`) accesible
con `H` desde View 1. Complementariamente, View 2 muestra un badge `REQ`
en el Pipeline sidebar con el recuento de requisitos EARS del change activo.

## Comportamiento Actual

No existe. `SpecHealthView` es una pantalla nueva. El badge REQ es nuevo en
el pipeline sidebar de View 2.

---

## 1. View 8 — SpecHealthView

### Navegación

- **REQ-10** `[Event]` When the user presses `H` in View 1 (EpicsView), the system SHALL open `SpecHealthView` via `push_screen`, passing the current `_show_archived` state.

- **REQ-11** `[Event]` When the user presses `Esc` in `SpecHealthView`, the system SHALL return to View 1 via `pop_screen`.

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ sdd-tui — spec health                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ CHANGE            REQ  EARS%  TASKS   ARTIFACTS          INACTIVE        │
│ view-8-spec-health  5   80%   3/6    P S D T           2d               │
│ view-9-delta-specs  0   —     0/4    P . . .           !12d             │
│ core-reader         3   67%   6/6    P S R D T          —               │
├─────────────────────────────────────────────────────────────────────────┤
│ [H] health   [Esc] ← changes                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Columnas del DataTable

| Columna | Contenido | Fuente |
|---------|-----------|--------|
| `CHANGE` | Nombre del directorio del change | `change.name` |
| `REQ` | `req_count` o `—` si 0 | `ChangeMetrics.req_count` |
| `EARS%` | `{pct}%` si req_count > 0, `—` si 0 | `ears_count / req_count * 100` |
| `TASKS` | `done/total` (ej: `3/6`) o `—` si sin tasks | `change.tasks` |
| `ARTIFACTS` | Letras iniciales presentes/ausentes | `ChangeMetrics.artifacts` |
| `INACTIVE` | `{N}d` (días), `—` si sin commits, `!{N}d` si > threshold | `ChangeMetrics.inactive_days` |

### Columna ARTIFACTS

Muestra iniciales en posición fija. Presentes en mayúscula, ausentes como `.`:

| Posición | Artefacto | Letra |
|----------|-----------|-------|
| 1 | proposal | `P` |
| 2 | spec | `S` |
| 3 | research | `R` (solo si existe en algún change) |
| 4 | design | `D` |
| 5 | tasks | `T` |

> **Nota:** La columna `R` solo aparece si al menos un change tiene `research.md`.
> Si ningún change en la lista tiene research, la columna se omite para no ocupar espacio.

### Alertas visuales

- **REQ-12** `[State]` While a change has `req_count == 0`, the system SHALL render its row with a warning style (Rich `yellow` o similar).

- **REQ-13** `[State]` While a change has `inactive_days > INACTIVE_THRESHOLD_DAYS (7)`, the system SHALL prefix the inactive value with `!` (ej: `!10d`) y renderizar la celda con estilo de alerta.

- **REQ-14** `[Ubiquitous]` The DataTable in `SpecHealthView` SHALL use `cursor_type="row"` and `show_header=True`.

### Scope de changes

- **REQ-15** `[Event]` When `SpecHealthView` is opened, the system SHALL load changes respecting the `include_archived` parameter:
  - `include_archived=False` → solo activos
  - `include_archived=True` → activos + archivados (con separador `── archived ──` como en View 1)

### Casos alternativos — View 8

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin changes activos | Lista vacía | Mensaje `No active changes` en lugar de DataTable |
| Change sin specs | `req_count=0` | REQ=`—`, EARS%=`—`, fila en amarillo |
| Change sin tasks | `change.tasks == []` | TASKS=`—` |
| git no disponible | `inactive_days=None` | INACTIVE=`—` (sin alerta) |
| Change sin commits | `inactive_days=None` | INACTIVE=`—` (sin alerta) |

### Escenario de verificación

**REQ-12/13** — Alertas visuales

**Dado** View 8 con un change que tiene `req_count=0` y `inactive_days=10`
**Cuando** se renderiza la fila
**Entonces** `REQ=—` en amarillo, `INACTIVE=!10d` con estilo de alerta

---

## 2. Badge REQ en View 2 (PipelinePanel)

### Layout extendido

```
  PIPELINE

  ✓  propose
  ✓  spec
  ·  design
  ·  tasks
 2/4 apply
  ·  verify

  REQ: 5 (80%)
```

### Comportamiento

- **REQ-16** `[Event]` When `ChangeDetailScreen` (View 2) is opened, the system SHALL compute `ChangeMetrics` for the current change and display the REQ badge in `PipelinePanel` below the phase list.

- **REQ-17** `[State]` While the `spec` phase is `PENDING` (no specs exist for the change), the system SHALL display `REQ: —` in the pipeline sidebar.

- **REQ-18** `[State]` While `req_count > 0`, the system SHALL display `REQ: {req_count} ({pct}%)` where `pct = round(ears_count / req_count * 100)`.

- **REQ-19** `[Event]` When `r` (refresh) is pressed in View 2, the system SHALL recompute `ChangeMetrics` and update the REQ badge alongside the pipeline refresh.

### Casos alternativos — badge REQ

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin specs | `spec=PENDING` | `REQ: —` |
| Specs sin REQ-XX | `req_count=0` | `REQ: 0 (—%)` |
| Todos tipificados | `ears_count == req_count` | `REQ: 5 (100%)` |
| git no disponible | `inactive_days=None` | Badge sin cambio (REQ no depende de git) |

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `push_screen` con parámetro `include_archived` | Leer estado de EpicsView en runtime | Más explícito; SpecHealthView no depende de EpicsView internals |
| DataTable `show_header=True` | Sin header | Las columnas no son obvias por contenido en una tabla de métricas |
| Columna `R` dinámica (solo si algún change tiene research) | Siempre presente con `.` | Evita columna vacía en el 99% de los casos actuales |
| Badge REQ en PipelinePanel, no en TaskListPanel | Columna extra en DataTable | El pipeline sidebar tiene espacio natural; no satura las tareas |
| `!{N}d` para alertas en INACTIVE | Color solo | El prefijo `!` distingue la alerta incluso en terminales sin color |
| `INACTIVE_THRESHOLD_DAYS = 7` hardcoded en `core/metrics.py` | `config.yaml` | Sin casos de uso reales de personalización en v1 |

## Abierto / Pendiente

Ninguno.
