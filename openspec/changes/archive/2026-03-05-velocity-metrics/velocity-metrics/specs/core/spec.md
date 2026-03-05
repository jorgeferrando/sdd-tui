# Spec: Core — velocity-metrics

## Metadata
- **Dominio:** core
- **Change:** velocity-metrics
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Nuevo módulo `core/velocity.py` que infiere métricas de throughput y lead time
del proceso SDD a partir de commits en git. Sin estado propio — solo `git log`
sobre los changes archivados.

Extensión del dominio core existente. Sin dependencias nuevas.

---

## Comportamiento Actual

No existe. Esta sección es nueva.

---

## Requisitos (EARS)

- **REQ-VM01** `[Event]` When `compute_velocity(archive_dirs, cwd)` is called, the system SHALL return a `VelocityReport` with throughput and lead time aggregated from all archived changes across all provided archive dirs.
- **REQ-VM02** `[Ubiquitous]` The system SHALL infer the start date of a change as the date of the first git commit whose message contains `[{change_name}]`.
- **REQ-VM03** `[Ubiquitous]` The system SHALL infer the end date of a change as the date of the last git commit whose message contains `[{change_name}]`.
- **REQ-VM04** `[Ubiquitous]` The lead time of a change SHALL be `end_date - start_date` in days (integer).
- **REQ-VM05** `[Unwanted]` If no commits are found for a change, the system SHALL set `start_date = None`, `end_date = None`, and `lead_time_days = None` — without raising.
- **REQ-VM06** `[Ubiquitous]` Throughput SHALL be computed as changes-per-week, grouped by the ISO week of `end_date`, for the last 8 weeks relative to today.
- **REQ-VM07** `[Unwanted]` If a change has no `end_date`, it SHALL be excluded from throughput and lead time calculations.
- **REQ-VM08** `[Ubiquitous]` `median_lead_time` and `p90_lead_time` SHALL be computed over all changes with non-None `lead_time_days`, across all projects.
- **REQ-VM09** `[Unwanted]` If fewer than 2 changes have lead time data, `median_lead_time` and `p90_lead_time` SHALL be `None`.
- **REQ-VM10** `[Optional]` Where multi-project config provides N archive dirs, the system SHALL aggregate changes from all dirs into a single `VelocityReport`.
- **REQ-VM11** `[Unwanted]` If `git log` fails or git is not available, the system SHALL return an empty `VelocityReport` without raising.
- **REQ-VM12** `[Ubiquitous]` git log queries SHALL use `-F` (fixed-strings) to prevent `[change-name]` from being interpreted as regex.

### Escenarios de verificación

**REQ-VM04** — lead time de 2 días
**Dado** un change cuyo primer commit fue el 2026-03-01 y el último el 2026-03-03
**Cuando** se computa el lead time
**Entonces** `lead_time_days = 2`

**REQ-VM06** — throughput semanal
**Dado** 3 changes archivados con `end_date` en la semana 2026-W09 y 1 en 2026-W08
**Cuando** se computa el throughput de las últimas 8 semanas
**Entonces** `weekly_throughput` incluye `(2026-W09-start, 3)` y `(2026-W08-start, 1)` y 0 para el resto

**REQ-VM09** — sin datos suficientes
**Dado** solo 1 change con lead time
**Cuando** se computa `median_lead_time`
**Entonces** `median_lead_time = None` y `p90_lead_time = None`

---

## Modelo de Datos

```python
@dataclass
class ChangeVelocity:
    name: str                      # nombre del change (sin prefijo de fecha)
    project: str                   # basename del proyecto
    start_date: date | None        # fecha del primer commit del change
    end_date: date | None          # fecha del último commit del change
    lead_time_days: int | None     # end_date - start_date en días

@dataclass
class VelocityReport:
    changes: list[ChangeVelocity]
    weekly_throughput: list[tuple[date, int]]  # (week_start_monday, count), últimas 8 semanas
    median_lead_time: float | None
    p90_lead_time: float | None
    slowest_change: ChangeVelocity | None  # change con mayor lead_time_days
```

---

## Interfaz

```python
def compute_velocity(
    archive_dirs: list[Path],    # lista de openspec/changes/archive/ de cada proyecto
    cwd: Path,                   # usado como cwd para git log en single-project
) -> VelocityReport
```

### Implementación de git queries

Para cada change en `archive_dir`:
1. Extraer `change_name` = nombre del directorio sin prefijo `YYYY-MM-DD-`
2. Ejecutar `git -C {project_path} log --format=%ad --date=short -F --grep=[{change_name}]`
3. Primera línea = `end_date` (git log orden inverso: más reciente primero)
4. Última línea = `start_date`

`project_path` para cada archive_dir = `archive_dir.parent.parent` (raíz del repo).

### Percentiles

`p90_lead_time = sorted_values[int(0.9 * len(sorted_values))]` (sin librerías extra).
`median_lead_time = statistics.median(lead_times)` (stdlib).

---

## Casos Alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| archive/ vacío | Sin subdirectorios con prefijo fecha | `VelocityReport(changes=[], ...)` vacío |
| Subdirectorio sin prefijo fecha | Nombre sin `YYYY-MM-DD-` | Ignorado silenciosamente |
| Change sin commits | `git log` devuelve vacío | `ChangeVelocity` con fechas `None` |
| Un solo change con datos | `len(lead_times) == 1` | `median=None`, `p90=None` |
| git no instalado | `FileNotFoundError` | `VelocityReport` vacío sin excepción |
| Directorio archive no existe | `archive_dir` ausente | Se omite silenciosamente |

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Lead time total (sin desglose por fase) | Estimación ponderada por tareas | No inferible con precisión desde git; aproximación sería engañosa |
| `git log` por change_name | `git log` por archivo de change | Nombre del change es más discriminante; archivos de spec también se commiten con el mismo prefijo |
| `statistics.median` (stdlib) | numpy/scipy | Sin dependencias nuevas |
| `archive_dirs: list[Path]` (multi-project) | `archive_dir: Path` single | Alineado con `observatory-v1`; degradación natural a lista de 1 elemento |
| `slowest_change` en el report | Solo nombre en la TUI | El core provee los datos; la TUI decide cómo mostrarlos |
| Percentil 90 manual sin librería | `statistics.quantiles` (Python 3.8+) | `statistics.quantiles` no está en todas las versiones; implementación trivial |

## Abierto / Pendiente

Ninguno.
