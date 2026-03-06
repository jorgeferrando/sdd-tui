# Spec: Core — Complexity Score en ChangeMetrics

## Metadata
- **Dominio:** core
- **Change:** complexity-badge
- **Fecha:** 2026-03-06
- **Versión:** 1.2
- **Estado:** approved

## Contexto

Extensión del módulo `core/metrics.py`. Añade dos campos a `ChangeMetrics`:
`complexity_score` (entero) y `complexity_label` (XS/S/M/L/XL), calculados
a partir de datos ya disponibles sin introducir dependencias nuevas.

## Comportamiento Actual

`parse_metrics` retorna `ChangeMetrics` con `req_count`, `ears_count`,
`artifacts`, e `inactive_days`. No existe ninguna métrica de tamaño o complejidad.

---

## Requisitos (EARS)

- **REQ-CB-01** `[Event]` When `parse_metrics(change_path, repo_cwd)` is called, the system SHALL compute `complexity_score` as `task_count * 3 + spec_lines // 50 + git_files`.

- **REQ-CB-02** `[Ubiquitous]` The system SHALL derive `task_count` from `len(change.tasks)` passed implicitly via the number of task lines parsed from `tasks.md`; if `tasks.md` is absent, `task_count = 0`.

- **REQ-CB-03** `[Ubiquitous]` The system SHALL derive `spec_lines` by counting total lines across all `specs/*/spec.md` files under `change_path`; if none exist, `spec_lines = 0`.

- **REQ-CB-04** `[Ubiquitous]` The system SHALL derive `git_files` as the count of distinct files appearing in all git commits whose message contains `[{change_name}]`, using `git log --name-only --format= -F --grep=[{change_name}]`; empty lines are excluded.

- **REQ-CB-05** `[Unwanted]` If git is unavailable or the directory is not a git repo, the system SHALL use `git_files = 0` without raising.

- **REQ-CB-06** `[Ubiquitous]` The system SHALL map `complexity_score` to `complexity_label` using these ranges:

  | Score | Label |
  |-------|-------|
  | 0–5   | XS    |
  | 6–12  | S     |
  | 13–24 | M     |
  | 25–40 | L     |
  | 41+   | XL    |

- **REQ-CB-07** `[Ubiquitous]` The system SHALL add `complexity_score: int` and `complexity_label: str` to `ChangeMetrics`.

### Escenarios de verificación

**REQ-CB-01** — score calculation
**Dado** un change con 3 tareas, 100 líneas de spec, y 5 archivos en commits
**Cuando** se llama a `parse_metrics`
**Entonces** `complexity_score = 3*3 + 100//50 + 5 = 9 + 2 + 5 = 16`, `complexity_label = "M"`

**REQ-CB-04** — git_files con historial
**Dado** un change con commits `[my-change] T01` y `[my-change] T02` que tocan 3 y 4 archivos respectivamente (2 compartidos)
**Cuando** se calcula `git_files`
**Entonces** `git_files = 5` (archivos distintos, sin repetir)

**REQ-CB-05** — degradación silenciosa
**Dado** un directorio que no es repo git
**Cuando** se llama a `parse_metrics`
**Entonces** `git_files = 0`, no se lanza excepción, `complexity_score` se calcula con las otras dos componentes

## Interfaces / Contratos

```python
@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str]
    inactive_days: int | None
    complexity_score: int    # nuevo
    complexity_label: str    # nuevo: "XS" | "S" | "M" | "L" | "XL"
```

```python
def parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics: ...

def _get_complexity(change_path: Path, repo_cwd: Path) -> tuple[int, str]:
    """Retorna (score, label)."""
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `task_count * 3` como peso mayor | Peso igual para los tres inputs | Las tareas son el predictor más directo de esfuerzo de revisión |
| `spec_lines // 50` | Contar párrafos o REQs | Líneas es un proxy simple; `//50` normaliza a unidades comparables con tareas |
| `git log --name-only` para git_files | `git diff --name-only HEAD~N..HEAD` | El grep por change_name funciona para archivados y activos; no requiere conocer el rango exacto de commits |
| Labels XS/S/M/L/XL | Score numérico crudo en display | Más legible; comunica intención (tamaño) mejor que un número |
| XL en amarillo (warning) | Rojo o sin color | Amarillo = advertencia, no bloqueo; el usuario decide si dividir |

## Abierto / Pendiente

Ninguno.
