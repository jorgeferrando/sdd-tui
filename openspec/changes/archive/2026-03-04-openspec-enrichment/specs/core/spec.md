# Spec: Core — openspec enrichment (steering + requirements + spec.json)

## Metadata
- **Dominio:** core
- **Change:** openspec-enrichment
- **Fecha:** 2026-03-04
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Añade tres artefactos opcionales al formato `openspec/`:
- `steering.md` — contexto global del proyecto (nivel raíz de openspec)
- `requirements.md` — requisitos EARS separados del spec (nivel change, opcional)
- `spec.json` — metadata estructurada por change (nivel change, opcional)

Ninguno rompe compatibilidad hacia atrás. El reader existente no necesita cambios
de interfaz — se añaden funciones nuevas.

## Comportamiento Actual

El reader detecta `proposal.md`, `specs/*/spec.md`, `design.md`, `tasks.md`
para pipeline, y `research.md` como artefacto en métricas.

No existe ningún mecanismo para contexto global del proyecto ni para metadata
estructurada por change.

## Requisitos (EARS)

### 9. Steering Reader

- **REQ-S01** `[Optional]` Where `openspec/steering.md` exists, `load_steering(openspec_path)` SHALL return its full content as `str`
- **REQ-S02** `[Unwanted]` If `openspec/steering.md` does not exist, `load_steering` SHALL return `None` without raising any exception
- **REQ-S03** `[Ubiquitous]` The reader SHALL use `errors="replace"` when reading steering.md — never raise `UnicodeDecodeError`

### 10. Requirements Reader

- **REQ-R01** `[Optional]` Where `requirements.md` exists in a change directory, `parse_metrics` SHALL include `"requirements"` in `ChangeMetrics.artifacts`
- **REQ-R02** `[Optional]` Where `requirements.md` exists, `parse_metrics` SHALL also search it for `**REQ-XX**` patterns (in addition to `specs/*/spec.md`)
- **REQ-R03** `[Ubiquitous]` The presence of `requirements.md` SHALL NOT affect pipeline phase inference — `spec` phase still requires `specs/*/spec.md`
- **REQ-R04** `[Unwanted]` If `requirements.md` does not exist, `parse_metrics` behavior is unchanged (fully retrocompatible)

### Escenarios de verificación — REQ-R02

**REQ-R02** — REQs encontrados tanto en requirements.md como en specs/
**Dado** un change con `requirements.md` que contiene REQ-01 y REQ-02,
  y `specs/core/spec.md` que también referencia REQ-01
**Cuando** se llama a `parse_metrics`
**Entonces** `req_count = 2` (IDs únicos: REQ-01, REQ-02, no duplicados)

### 11. spec.json Reader

- **REQ-J01** `[Optional]` Where `spec.json` exists in a change directory, `load_spec_json(change_path)` SHALL return the parsed dict
- **REQ-J02** `[Unwanted]` If `spec.json` does not exist, `load_spec_json` SHALL return `None` without raising any exception
- **REQ-J03** `[Unwanted]` If `spec.json` exists but contains malformed JSON, `load_spec_json` SHALL return `None` without raising any exception
- **REQ-J04** `[Ubiquitous]` `spec.json` SHALL be informational only — the TUI and pipeline inference SHALL always recompute from disk state and SHALL NOT use spec.json as authoritative source

## Interfaces / Contratos

### `load_steering(openspec_path: Path) -> str | None`

```python
def load_steering(openspec_path: Path) -> str | None:
    """Returns content of openspec/steering.md or None if not present."""
```

Ubicación del archivo: `{openspec_path}/steering.md`

### `load_spec_json(change_path: Path) -> dict | None`

```python
def load_spec_json(change_path: Path) -> dict | None:
    """Returns parsed spec.json or None if not present or malformed."""
```

Ubicación del archivo: `{change_path}/spec.json`

### spec.json — Formato

```json
{
  "format": "openspec",
  "version": "1.0",
  "change": "string — nombre del change",
  "generated_at": "ISO 8601 timestamp",
  "pipeline": {
    "propose": "done|pending",
    "spec": "done|pending",
    "design": "done|pending",
    "tasks": "done|pending",
    "apply": "done|pending",
    "verify": "done|pending"
  },
  "tasks": {
    "total": 0,
    "done": 0,
    "pending": 0
  },
  "requirements": ["REQ-01", "REQ-02"]
}
```

### Cambios en `ChangeMetrics.artifacts`

Orden fijo de artefactos (nuevo orden con `requirements`):

| Artefacto | Huella en disco | Letra en SpecHealthScreen |
|-----------|----------------|--------------------------|
| `proposal` | `proposal.md` | `P` |
| `spec` | `specs/*/spec.md` (al menos uno) | `S` |
| `research` | `research.md` (opcional) | `R` |
| `requirements` | `requirements.md` (opcional, NUEVO) | `Q` |
| `design` | `design.md` | `D` |
| `tasks` | `tasks.md` | `T` |

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin steering.md | `openspec/steering.md` no existe | `load_steering()` → `None` |
| Steering vacío | Archivo existe pero vacío | `load_steering()` → `""` (string vacío) |
| Sin requirements.md | Change sin el archivo | Artefacto `requirements` no aparece en artifacts; REQs solo de specs/ |
| spec.json no existe | Archivo ausente | `load_spec_json()` → `None` |
| spec.json corrupto | JSON inválido | `load_spec_json()` → `None` (excepción capturada) |
| requirements.md vacío | Archivo existe sin REQs | Artefacto `requirements` aparece en artifacts; `req_count` sin cambio |

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| steering.md como markdown libre | YAML/JSON estructurado | Editable por humanos y agentes sin schema; rich.Markdown lo renderiza nativamente |
| requirements.md no afecta pipeline | Contar como fase `spec` | Mantiene retrocompatibilidad total; spec.md sigue siendo el artefacto de spec |
| spec.json no es authoritative | Usar spec.json como fuente de verdad | La fuente de verdad sigue siendo el disco; spec.json es snapshot para consumidores externos |
| `load_spec_json` en `core/reader.py` | Módulo separado `core/spec_json.py` | Funciones de lectura relacionadas en un módulo; no hay lógica compleja |
| `requirements` entre `research` y `design` en el orden de artefactos | Al final | Refleja la posición conceptual en el flujo SDD: spec → requirements → design |
| REQs únicos (union) de requirements.md + specs/ | Solo requirements.md | Un REQ puede aparecer en ambos (definición + referencia) — contar solo IDs únicos es más correcto |

## Abierto / Pendiente

Ninguno.
