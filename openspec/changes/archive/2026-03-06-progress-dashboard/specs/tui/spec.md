# Spec: TUI — Progress Dashboard

## Metadata
- **Dominio:** tui
- **Change:** progress-dashboard
- **Fecha:** 2026-03-06
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Añade `ProgressDashboard`, una pantalla de solo lectura que agrega el estado de
progreso de todos los changes visibles. Responde a la pregunta: "¿cuánto del
trabajo total está hecho?" sin necesidad de sumar mentalmente las filas de EpicsView.

Recibe la misma lista de changes que EpicsView (respeta el flag `show_archived`).

---

## Requisitos (EARS)

### Acceso

- **REQ-PD-01** `[Event]` When el usuario pulsa `P` en EpicsView,
  the app SHALL navegar a ProgressDashboard mostrando los changes actualmente visibles.

- **REQ-PD-02** `[Event]` When el usuario pulsa `Escape` en ProgressDashboard,
  the app SHALL volver a EpicsView sin modificar su estado.

### Contenido — Sección GLOBAL

- **REQ-PD-03** `[Ubiquitous]` The ProgressDashboard SHALL mostrar una sección GLOBAL con:
  - número de changes incluidos
  - total de tareas (done + pending)
  - porcentaje completado (done / total × 100), redondeado a entero
  - barra de progreso visual proporcional al porcentaje

- **REQ-PD-04** `[Unwanted]` If no hay changes, the ProgressDashboard SHALL mostrar
  "No changes to display" en lugar de las secciones de contenido.

- **REQ-PD-05** `[Unwanted]` If el total de tareas es 0 (todos los changes sin tasks.md),
  the ProgressDashboard SHALL mostrar 0% y barra vacía (no dividir por cero).

### Contenido — Sección BY CHANGE

- **REQ-PD-06** `[Ubiquitous]` The ProgressDashboard SHALL mostrar una sección BY CHANGE
  con una línea por change, incluyendo:
  - nombre del change
  - barra de progreso de tareas (proporcional a done/total)
  - ratio numérico `done/total`
  - fase más avanzada completada del pipeline (la última fase DONE),
    o `—` si ninguna fase está DONE

- **REQ-PD-07** `[Ubiquitous]` The ProgressDashboard SHALL mostrar `0/0` para un change
  sin `tasks.md` (no omitirlo).

### Contenido — Sección PIPELINE DISTRIBUTION

- **REQ-PD-08** `[Ubiquitous]` The ProgressDashboard SHALL mostrar una sección
  PIPELINE DISTRIBUTION contando, para cada fase (propose/spec/design/tasks/apply/verify),
  cuántos changes tienen esa fase como su **fase más avanzada completada** (última DONE).

- **REQ-PD-09** `[Ubiquitous]` The ProgressDashboard SHALL mostrar una barra visual
  proporcional al número de changes en cada fase (ancho máx. 20 caracteres).

- **REQ-PD-10** `[Unwanted]` If ningún change tiene una fase determinada como la más
  avanzada, the ProgressDashboard SHALL mostrar `·` (sin barra) para esa fase.

### Export

- **REQ-PD-11** `[Event]` When el usuario pulsa `e` en ProgressDashboard,
  the app SHALL copiar el reporte en formato Markdown al clipboard y mostrar
  una notificación "Report copied to clipboard".

### Scroll

- **REQ-PD-12** `[Event]` When el usuario pulsa `j` en ProgressDashboard,
  the app SHALL hacer scroll hacia abajo en el contenido.

- **REQ-PD-13** `[Event]` When el usuario pulsa `k` en ProgressDashboard,
  the app SHALL hacer scroll hacia arriba en el contenido.

---

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — progress dashboard                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ GLOBAL                                                       │
│   Changes:   5                                               │
│   Tasks:    23  (17 done / 6 pending)                        │
│   Progress: 74%  ████████████████░░░░                        │
│                                                              │
│ BY CHANGE                                                     │
│   change-name-1    ████████░░░  8/10   apply                 │
│   change-name-2    ████████████  4/4   verify                │
│   change-name-3    ░░░░░░░░░░░  0/0   design                 │
│   change-name-4    ░░░░░░░░░░░  0/5   —                      │
│                                                              │
│ PIPELINE DISTRIBUTION                                        │
│   propose  ·       0                                         │
│   spec     ■       1                                         │
│   design   ■■      2                                         │
│   tasks    ■       1                                         │
│   apply    ■       1                                         │
│   verify   ·       0                                         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ [Esc] Back   [e] Export   [j/k] Scroll                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Contratos de datos

### Entrada

`ProgressDashboard` recibe `list[Change]` — la misma lista que EpicsView ya tiene
cargada (no recalcula desde disco).

### `ProgressReport` (modelo interno)

```python
@dataclass
class ChangeProgress:
    name: str
    tasks_done: int
    tasks_total: int
    furthest_phase: str | None  # última fase DONE, o None

@dataclass
class ProgressReport:
    changes: list[ChangeProgress]
    total_done: int
    total_tasks: int
    percent: int  # 0-100, 0 si total_tasks == 0
    pipeline_distribution: dict[str, int]  # fase → count de changes
```

### `compute_progress(changes: list[Change]) -> ProgressReport`

Función pura en `core/progress.py`. No accede a disco ni a git.

---

## Escenarios de verificación

**REQ-PD-05** — sin tasks, no divide por cero
**Dado** 3 changes sin tasks.md
**Cuando** se llama `compute_progress(changes)`
**Entonces** `percent == 0` y `total_tasks == 0`

**REQ-PD-08** — distribución de pipeline
**Dado** change-A con pipeline hasta `apply` DONE, change-B con `spec` DONE
**Cuando** se llama `compute_progress(changes)`
**Entonces** `pipeline_distribution["apply"] == 1`, `pipeline_distribution["spec"] == 1`

**REQ-PD-04** — lista vacía
**Dado** lista vacía de changes
**Cuando** se monta ProgressDashboard
**Entonces** se muestra "No changes to display"

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Recibe `list[Change]` (ya cargada) | Leer desde disco | Evita I/O duplicado; EpicsView ya tiene los datos |
| `furthest_phase` = última DONE | Primera PENDING | Muestra avance, no bloqueo (para eso existe `HINT` en SpecHealth) |
| Respeta `show_archived` | Solo activos siempre | Consistencia con el estado de EpicsView que el usuario ya configuró |
| `compute_progress` es función pura | Método de clase | Testeable sin mocks |
| Barra de 12 chars para by-change, 20 para global | Ancho fijo | Proporcional al espacio disponible |

## Abierto / Pendiente

- [ ] ¿Multi-project: separar secciones por proyecto o agregar todo junto? (no bloquea — agregar todo junto como V1)
