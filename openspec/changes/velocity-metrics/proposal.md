# Proposal: velocity-metrics — Métricas de Throughput y Lead Time

## Metadata
- **Change:** velocity-metrics
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema / Motivación

No hay forma de medir la velocidad del proceso SDD: cuánto tardamos en completar
un change, dónde se acumula tiempo, cuántos changes archivamos por semana.
Esta información está latente en los timestamps de los commits pero no se agrega.

**Nota:** Tercera de tres features del "observatory":
1. `observatory-v1` — Multi-project
2. `pr-status` — GitHub PR status
3. `velocity-metrics` — Métricas de throughput y lead time (este change)

## Solución Propuesta

### VelocityView — nueva pantalla (`V` desde View 1)

```
┌─────────────────────────────────────────────────────────────────┐
│ sdd-tui — velocity                                               │
├─────────────────────────────────────────────────────────────────┤
│ THROUGHPUT (últimas 8 semanas)                                   │
│                                                                  │
│  Week of 2026-01-13   ██████  3 changes                         │
│  Week of 2026-01-20   ████    2 changes                         │
│  Week of 2026-01-27   ██████████  5 changes                     │
│  Week of 2026-02-03   ██  1 change                              │
│  ...                                                             │
│                                                                  │
│ LEAD TIME POR FASE (media sobre archivados)                      │
│                                                                  │
│  propose →  1.2d                                                 │
│  spec    →  0.5d                                                 │
│  design  →  2.1d  ← BOTTLENECK                                  │
│  tasks   →  0.3d                                                 │
│  apply   →  3.8d  ← BOTTLENECK                                  │
│  verify  →  0.1d                                                 │
│                                                                  │
│  Total lead time: median 8.0d / P90 14.2d                       │
├─────────────────────────────────────────────────────────────────┤
│ [E] export markdown   [j/k] scroll   [Esc] ← changes            │
└─────────────────────────────────────────────────────────────────┘
```

### Fuente de datos

Timestamps inferidos de `git log` sobre los changes archivados:
- **Inicio del change**: primer commit con `[{change-name}]` en el mensaje
- **Fin del change (archive)**: último commit con `[{change-name}]`

Lead time por fase: no es computable con exactitud desde git (no hay timestamp
por fase). Se usa la aproximación: `total_lead_time / n_fases` ponderado
por número de tareas en `apply`.

**Nota:** Si el futuro `spec.json` incluye timestamps por fase, se puede refinar.
Por ahora: aproximación git log.

### Export Markdown (`E`)

Copia al clipboard un reporte en Markdown:

```markdown
## Velocity Report — sdd-tui — 2026-03-05

### Throughput
- Last 8 weeks: 19 changes archived (avg 2.4/week)

### Lead Time
- Median: 8.0 days
- P90: 14.2 days
- Bottleneck: apply (avg 3.8 days)
```

### Core — `core/velocity.py`

```python
@dataclass
class ChangeVelocity:
    name: str
    start_date: date | None   # primer commit del change
    end_date: date | None     # último commit del change
    lead_time_days: int | None

@dataclass
class VelocityReport:
    changes: list[ChangeVelocity]
    weekly_throughput: list[tuple[date, int]]  # (week_start, count)
    median_lead_time: float | None
    p90_lead_time: float | None
```

## Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|---------------|
| Timestamps en `spec.json` | `spec.json` es opcional/informacional; depender de él sería frágil |
| Lead time exacto por fase | No es inferible de git sin instrumentación adicional |
| Barras de progreso con widgets Textual | `rich.Text` con bloques Unicode es suficiente y más simple |

## Impacto Estimado

| Archivo | Cambio |
|---------|--------|
| `core/velocity.py` | Nuevo: `compute_velocity(archive_dir, cwd) -> VelocityReport` |
| `tui/velocity.py` | Nuevo: `VelocityView` screen |
| `tui/epics.py` | Binding `V` → `push_screen(VelocityView)` |
| `tests/test_velocity.py` | Nuevo: tests unitarios con fixtures de archive |
| `tests/test_tui_epics.py` | Caso binding `V` |

Estimación: ~5 archivos, ~15 tests nuevos.

## Criterios de Exito

- [ ] `V` desde View 1 abre `VelocityView`
- [ ] Throughput muestra barras por semana (últimas 8)
- [ ] Lead time muestra media y P90 sobre changes archivados
- [ ] Bottleneck (fase/etapa con más tiempo) destacado en amarillo
- [ ] `E` copia reporte Markdown al clipboard
- [ ] Degrada a "No archived changes" si no hay datos
- [ ] Tests >= 141 (tras `observatory-v1` y `pr-status`)
