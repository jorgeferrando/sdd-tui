# Spec: TUI — velocity-metrics (VelocityView)

## Metadata
- **Dominio:** tui
- **Change:** velocity-metrics
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Nueva pantalla `VelocityView` accesible desde View 1 (EpicsView) con `V`.
Muestra throughput semanal y lead time sobre los changes archivados, usando
datos de `core/velocity.py`.

Extensión de la spec TUI existente (versión 1.7).

---

## Comportamiento Actual

No existe pantalla de métricas de velocidad.

---

## Requisitos (EARS)

### Navegación

- **REQ-V01** `[Event]` When el usuario pulsa `V` en View 1, the app SHALL hacer `push_screen(VelocityView)`.
- **REQ-V02** `[Event]` When el usuario pulsa `Esc` en `VelocityView`, the app SHALL hacer `pop_screen` volviendo a View 1.
- **REQ-V03** `[Event]` When el usuario pulsa `j` en `VelocityView`, the screen SHALL hacer scroll hacia abajo.
- **REQ-V04** `[Event]` When el usuario pulsa `k` en `VelocityView`, the screen SHALL hacer scroll hacia arriba.

### Contenido — Throughput

- **REQ-V05** `[Ubiquitous]` VelocityView SHALL mostrar una sección `THROUGHPUT` con una barra Unicode por semana para las últimas 8 semanas ISO.
- **REQ-V06** `[Ubiquitous]` Cada barra SHALL escalar proporcionalmente al máximo de la semana con más changes archivados en el período.
- **REQ-V07** `[Unwanted]` If no hay changes archivados en las últimas 8 semanas, the section SHALL mostrar `No archived changes in the last 8 weeks`.

### Contenido — Lead Time

- **REQ-V08** `[Ubiquitous]` VelocityView SHALL mostrar una sección `LEAD TIME` con `Median`, `P90`, total de changes usados, y el change más lento.
- **REQ-V09** `[Unwanted]` If `median_lead_time is None` (menos de 2 changes con datos), the section SHALL mostrar `Not enough data (need at least 2 archived changes)`.

### Export Markdown

- **REQ-V10** `[Event]` When el usuario pulsa `E`, the app SHALL copiar al portapapeles un reporte Markdown con throughput y lead time.
- **REQ-V11** `[Event]` When el clipboard action completes, the app SHALL mostrar un toast `Report copied to clipboard`.

### Degradación

- **REQ-V12** `[Unwanted]` If `compute_velocity` falla o git no está disponible, VelocityView SHALL mostrar `No data available`.

---

## Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ sdd-tui — velocity                                               │
├─────────────────────────────────────────────────────────────────┤
│ THROUGHPUT (últimas 8 semanas)                                   │
│                                                                  │
│  2026-W03   ██████  3 changes                                    │
│  2026-W04   ████    2 changes                                    │
│  2026-W05   ██████████  5 changes                                │
│  2026-W06   ██  1 change                                         │
│  2026-W07   ·   0 changes                                        │
│  2026-W08   ████████  4 changes                                  │
│  2026-W09   ██████  3 changes                                    │
│  2026-W10   ██  1 change                                         │
│                                                                  │
│ LEAD TIME (sobre 23 changes archivados)                          │
│                                                                  │
│  Median: 8.0d                                                    │
│  P90:   14.2d                                                    │
│  Slowest: view-3-commit-diff (21d)                               │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ [E] export   [j/k] scroll   [Esc] ← changes                     │
└─────────────────────────────────────────────────────────────────┘
```

### Formato de barras

- Ancho máximo: 20 bloques `█` (U+2588)
- Semanas sin changes: `.` (sin bloque, solo punto indicativo)
- Label de semana: `YYYY-WNN` (ISO week)
- Count: `N changes` / `1 change` (singular/plural)
- Escalado: `bar_width = round(count / max_count * 20)`

---

## Export Markdown — formato

```markdown
## Velocity Report — {project} — {date}

### Throughput (últimas 8 semanas)
- 2026-W03: 3 changes
- 2026-W04: 2 changes
...
- Total: 19 changes (avg 2.4/week)

### Lead Time
- Changes with data: 23
- Median: 8.0 days
- P90: 14.2 days
- Slowest: view-3-commit-diff (21 days)
```

En multi-project: `{project}` = lista de proyectos separados por coma.

---

## Casos Alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin changes archivados | `report.changes` vacío | Mostrar `No data available` en ambas secciones |
| Datos solo en throughput | `median_lead_time is None` | Throughput visible; lead time muestra `Not enough data` |
| `E` sin datos | `report.changes` vacío | El reporte exportado indica `No data` |
| Multi-project | N archive dirs | Datos agregados; proyectos listados en header |

---

## Implementación

- `VelocityView` en `tui/velocity.py` — `Screen` de Textual
- `on_mount`: llama `compute_velocity(archive_dirs, cwd)` — síncrono (no worker, ya que el cálculo es ligero)
- `archive_dirs` construidos desde `self.app.changes` → `change.project_path / "openspec" / "changes" / "archive"` (deduplicado)
- Patrón `action_scroll_down/up` → `ScrollableContainer` (igual que otros viewers)
- `E` → `_build_markdown_report(report)` → `self.app.copy_to_clipboard`

### Binding en EpicsView

```python
Binding("V", "velocity", "Velocity")
```

`action_velocity`: `self.app.push_screen(VelocityView(archive_dirs))`

---

## Reglas de negocio

- **RB-VV01:** `VelocityView` recibe `archive_dirs: list[Path]` al construirse — no los recalcula internamente.
- **RB-VV02:** Deduplicar `archive_dirs` por path real — evitar contar el mismo proyecto dos veces.
- **RB-VV03:** El reporte exportado siempre incluye la fecha del día en el header.
- **RB-VV04:** El binding `V` (mayúscula) distingue de `v` (sin uso actual) — consistente con `H`, `X` existentes.
- **RB-VV05:** `on_mount` es síncrono — `compute_velocity` solo hace `git log` por change; no hay diff ni operaciones pesadas.

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Carga síncrona en `on_mount` | Worker async | Operación ligera (git log por cada change, no diff); evitar complejidad de worker |
| `ScrollableContainer` con `Static` | `DataTable` | No hay selección de filas; contenido es puramente de lectura |
| `archive_dirs` como parámetro del constructor | Calcular en `on_mount` | Testable de forma aislada; `VelocityView` no necesita conocer `app.changes` |
| `V` mayúscula | `v` minúscula | Patrón del proyecto: pantallas nuevas usan mayúscula (`H` SpecHealth, `X` Timeline) |
| Sin worker para carga de datos | `@work(thread=True)` | Lead time es O(n_changes × git log) — rápido en práctica; evitar complejidad extra |

## Abierto / Pendiente

Ninguno.
