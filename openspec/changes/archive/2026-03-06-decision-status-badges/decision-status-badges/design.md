# Design: decision-status-badges

## Metadata
- **Change:** decision-status-badges
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-06
- **Estado:** approved

## Resumen Técnico

Dos cambios mínimos e independientes:

1. **`core/spec_parser.py`** — extender `Decision` con `status: str = "locked"` y actualizar
   el parseo de filas para detectar tablas de 3 o 4 columnas. Las tablas de 3 columnas
   (todos los archives existentes) mantienen compatibilidad con `status = "locked"` automático.

2. **`tui/spec_evolution.py`** — en `DecisionsTimeline._populate()`, añadir un badge coloreado
   antes del texto de cada decisión usando `_status_badge()`, función module-level pura.

No se crean archivos nuevos. El cambio no afecta ninguna otra pantalla ni módulo.

## Arquitectura

```
design.md (4 cols)          spec_parser.py          spec_evolution.py
┌──────────────────┐        ┌──────────────────┐    ┌───────────────────┐
│ | Dec | Alt | Why│        │ Decision          │    │ DecisionsTimeline │
│ | Estado |       │──────▶ │   .decision       │──▶ │  _populate()      │
│ | locked |       │        │   .alternative    │    │                   │
│ | open   |       │        │   .reason         │    │ [locked] Use X    │
│ | deferred|      │        │   .status="locked"│    │ [open] Schema v2  │
└──────────────────┘        └──────────────────┘    │ [deferred] Cache  │
                                                     └───────────────────┘
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/spec_parser.py` | Añadir `Decision.status`, actualizar parseo de filas | REQ-DSB-01/02/03 |
| `src/sdd_tui/tui/spec_evolution.py` | `_status_badge()` + badges en `_populate()` | REQ-DSB-06/07/08/09 |
| `tests/test_spec_parser.py` | Tests de parseo 4 cols y backwards compat 3 cols | Cobertura REQ-DSB-02/03 |
| `tests/test_tui_spec_evolution.py` | Tests de render de badges por status | Cobertura REQ-DSB-06/07/08/09 |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal (< 10)

## Patrones Aplicados

- **Función pura module-level para lógica de badge**: consistente con `next_command()` en `change_detail.py` y `repair_hints()` en `metrics.py` — lógica extraída para facilitar tests
- **Split de columnas en lugar de regex fijo**: más robusto para columnas variables; evita tener dos regexes `_TABLE_ROW_3` / `_TABLE_ROW_4`
- **Default en dataclass**: `status: str = "locked"` como campo con valor por defecto — backwards compat sin cambios en código llamador

## Implementación Detallada

### `core/spec_parser.py`

```python
@dataclass
class Decision:
    decision: str
    alternative: str
    reason: str
    status: str = "locked"
```

En `extract_decisions()`, reemplazar el bloque `if header_seen:` para usar split de columnas:

```python
if header_seen and line.startswith("|") and line.endswith("|"):
    if _SEPARATOR_ROW.match(line):
        continue
    cols = [c.strip() for c in line.split("|")[1:-1]]
    if len(cols) >= 3:
        result.decisions.append(Decision(
            decision=cols[0],
            alternative=cols[1],
            reason=cols[2],
            status=cols[3] if len(cols) >= 4 else "locked",
        ))
```

Eliminar `_TABLE_ROW` del módulo (ya no se usa) o dejar si otros tests dependen de él.
> Verificar con grep antes de eliminar.

### `tui/spec_evolution.py`

Añadir función module-level antes de `DecisionsTimeline`:

```python
_STATUS_STYLES: dict[str, tuple[str, str]] = {
    "locked": ("[locked]", "dim"),
    "open": ("[open]", "yellow"),
    "deferred": ("[deferred]", "cyan"),
}

def _status_badge(status: str) -> tuple[str, str]:
    """Return (badge_text, rich_style) for a decision status."""
    return _STATUS_STYLES.get(status, (f"[{status}]", "dim"))
```

En `_populate()`, cambiar la línea de decisión:

```python
# Antes:
content.append(f"  • {decision.decision}\n", style="white")

# Después:
badge, badge_style = _status_badge(decision.status)
content.append("  • ", style="white")
content.append(f"{badge} ", style=badge_style)
content.append(f"{decision.decision}\n", style="white")
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Split de columnas en lugar de regex doble | `_TABLE_ROW_3` + `_TABLE_ROW_4` | Una sola lógica cubre N columnas; menos código duplicado |
| `_status_badge()` función pura module-level | Método de instancia en `DecisionsTimeline` | Testable en aislamiento sin instanciar la pantalla |
| Eliminar `_TABLE_ROW` del módulo tras refactor | Mantener ambos | Si nadie más lo usa, eliminar reduce deuda; verificar con grep |
| Badge `dim` para status desconocido | `red` / raise | El usuario ve el valor; no bloquea el render |

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_extract_decisions_with_status_column` | `test_spec_parser.py` | Tabla 4 cols → `Decision.status` correcto |
| `test_extract_decisions_three_cols_defaults_locked` | `test_spec_parser.py` | Tabla 3 cols → `status = "locked"` (REQ-DSB-03) |
| `test_extract_decisions_mixed_status_values` | `test_spec_parser.py` | Valores `open`, `deferred`, desconocido |
| `test_status_badge_locked` | `test_tui_spec_evolution.py` | `_status_badge("locked")` → `("[locked]", "dim")` |
| `test_status_badge_open` | `test_tui_spec_evolution.py` | `_status_badge("open")` → `("[open]", "yellow")` |
| `test_status_badge_deferred` | `test_tui_spec_evolution.py` | `_status_badge("deferred")` → `("[deferred]", "cyan")` |
| `test_status_badge_unknown` | `test_tui_spec_evolution.py` | `_status_badge("foo")` → `("[foo]", "dim")` |
| `test_decisions_timeline_renders_badge` | `test_tui_spec_evolution.py` | Badge aparece en el content del timeline |

## Notas de Implementación

- Verificar con grep si `_TABLE_ROW` se usa en tests antes de eliminar; si aparece en `test_spec_parser.py`, actualizar los tests que lo importen directamente (poco probable — los tests usan `extract_decisions`, no el regex directamente).
- El campo `status` en `Decision` tiene default → los tests existentes que construyen `Decision("X", "Y", "Z")` siguen compilando sin cambios.
- `_status_badge()` exportar desde el módulo `spec_evolution` para poder importarlo en tests sin instanciar la TUI.
