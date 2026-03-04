# Spec: Core — Metrics module

## Metadata
- **Dominio:** core
- **Change:** view-8-spec-health
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** draft

## Contexto

`view-8-spec-health` necesita extraer métricas de calidad de cada change:
número de requisitos EARS en sus specs, artefactos presentes, y días de
inactividad git. Este módulo es puro Python, sin dependencias de la TUI,
testable de forma aislada.

## Comportamiento Actual

No existe. `core/metrics.py` es un módulo nuevo.

## Requisitos (EARS)

- **REQ-01** `[Event]` When `parse_metrics(change_path, repo_cwd)` is called, the system SHALL return a `ChangeMetrics` dataclass with `req_count`, `ears_count`, `artifacts`, and `inactive_days`.

- **REQ-02** `[Ubiquitous]` The parser SHALL detect REQ-XX by scanning all lines in spec files under `{change_path}/specs/` that match the pattern `\*\*REQ-\d+\*\*\s+\[`.

- **REQ-03** `[Ubiquitous]` A REQ SHALL be counted as EARS-typed if its line contains one of: `[Event]`, `[State]`, `[Unwanted]`, `[Optional]`, `[Ubiquitous]`.

- **REQ-04** `[Unwanted]` If no spec files exist under `{change_path}/specs/`, the system SHALL return `req_count=0` and `ears_count=0`.

- **REQ-05** `[Ubiquitous]` The system SHALL detect artifacts by checking file presence:
  - `proposal.md` → `proposal`
  - `specs/*/spec.md` (al menos uno) → `spec`
  - `research.md` → `research` (opcional — incluido solo si existe)
  - `design.md` → `design`
  - `tasks.md` → `tasks`

- **REQ-06** `[Event]` When computing `inactive_days`, the system SHALL execute `git log --oneline -F --grep="{change_name}"` against `repo_cwd` and return the number of days elapsed since the most recent matching commit.

- **REQ-07** `[Unwanted]` If no git commit matches the change name, the system SHALL return `inactive_days=None`.

- **REQ-08** `[Unwanted]` If git is unavailable or the directory is not a git repo, the system SHALL return `inactive_days=None` (silent degradation — no exception).

- **REQ-09** `[Ubiquitous]` The inactivity alert threshold SHALL be 7 days (hardcoded constant `INACTIVE_THRESHOLD_DAYS = 7`).

### Escenarios de verificación

**REQ-02/03** — Parser de requisitos EARS

**Dado** un spec con estas líneas:
```
- **REQ-01** `[Event]` When X, the Y SHALL Z
- **REQ-02** `[Unwanted]` If A, the B SHALL C
- **REQ-03** `[State]` While D, the E SHALL F
```
**Cuando** se llama a `parse_metrics`
**Entonces** `req_count=3`, `ears_count=3`

**REQ-04** — Sin specs

**Dado** un change sin directorio `specs/`
**Cuando** se llama a `parse_metrics`
**Entonces** `req_count=0`, `ears_count=0`

**REQ-06** — Días de inactividad

**Dado** un change con último commit hace 10 días
**Cuando** se llama a `parse_metrics`
**Entonces** `inactive_days=10`

## Interfaces / Contratos

### `ChangeMetrics` (dataclass)

```python
@dataclass
class ChangeMetrics:
    req_count: int           # total REQ-XX encontrados
    ears_count: int          # REQ-XX con tipo EARS válido
    artifacts: list[str]     # lista de artefactos presentes, en orden: proposal, spec, research, design, tasks
    inactive_days: int | None  # días desde último commit del change (None si no hay commit o git falla)

INACTIVE_THRESHOLD_DAYS: int = 7
```

### `parse_metrics(change_path: Path, repo_cwd: Path) -> ChangeMetrics`

Función pública del módulo. No lanza excepciones — errores se degradan silenciosamente.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Regex simple `\*\*REQ-\d+\*\*\s+\[` | Parser Markdown completo | Solo necesitamos detección de líneas, no AST |
| `git log --grep` con `-F` | regex por defecto | Los nombres de change contienen `[` que rompería el grep |
| `inactive_days` desde último commit del change | Mtime del archivo | git es la fuente de verdad del tiempo de actividad |
| `artifacts` como `list[str]` en orden fijo | `dict[str, bool]` | Más simple para el display; el orden importa para el render |
| `research` solo si existe | Siempre en la lista | `research.md` es opcional en el flujo SDD |

## Abierto / Pendiente

Ninguno.
