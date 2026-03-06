# Proposal: progress-dashboard

## Descripción

Añadir una pantalla global de progreso (`ProgressDashboard`) que agrega el estado
de todos los changes activos: tareas completadas, fase del pipeline actual, y
resumen numérico global. Se accede desde `EpicsView` con el binding `P`.

## Motivación

La `EpicsView` muestra el estado por change (una fila por change), pero no hay
ninguna vista que responda a la pregunta: **¿cuánto del trabajo total está hecho?**

- Para un solo change es trivial mirarlo.
- Con varios changes activos (multi-project), saber el % global de avance requiere
  sumar mentalmente filas y columnas.

El `progress-dashboard` llena ese hueco: una sola pantalla con agregados y
barras de progreso visuales.

## Alternativas consideradas

1. **Expandir EpicsView con una fila de totales** — no es escalable para multi-project;
   mezcla navegación con métricas.
2. **Añadir columna % a EpicsView** — demasiado denso; la tabla ya tiene 8 columnas.
3. **Progress screen separada** (este approach) — composable, exportable, patrón
   consistente con VelocityView y SpecHealthScreen.

## Impacto

### Archivos nuevos
- `src/sdd_tui/core/progress.py` — `ProgressReport`, `compute_progress()`
- `src/sdd_tui/tui/progress.py` — `ProgressDashboard(Screen)`

### Archivos modificados
- `src/sdd_tui/tui/epics.py` — binding `P` → `ProgressDashboard`

### Tests
- `tests/test_progress.py` — unit tests de `compute_progress()`
- `tests/tui/test_progress_tui.py` — TUI tests de `ProgressDashboard`

## Contenido de la pantalla

```
PROGRESS DASHBOARD

GLOBAL
  Changes activos:  5
  Tasks totales:   23  (17 done / 6 pending)
  Completado:      74%  ████████████████████░░░░░

BY CHANGE
  change-name-1    ████████░░░  8/10   apply 6/8
  change-name-2    ████████████  4/4   verify
  change-name-3    ░░░░░░░░░░░  0/5   design
  ...

PIPELINE DISTRIBUTION
  propose  ■■■■■  5
  spec     ■■■■■  5
  design   ■■■    3
  tasks    ■■     2
  apply    ■      1
  verify   ·      0
```

- Binding `e` exporta el reporte como Markdown al clipboard (consistente con VelocityView)
- Binding `escape` vuelve a EpicsView

## Criterios de éxito

- [ ] `compute_progress()` calcula totales correctamente con 0, 1, N changes
- [ ] `ProgressDashboard` se monta sin errores con lista vacía
- [ ] `P` desde EpicsView navega a la pantalla
- [ ] Escape vuelve a EpicsView
- [ ] Export copia Markdown al clipboard
- [ ] Tests: >= 10 unit tests + >= 2 TUI tests
