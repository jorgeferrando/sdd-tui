# Design: spec-health-hints

## Metadata
- **Change:** spec-health-hints
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** draft

## Resumen Técnico

Dos cambios ortogonales conectados por una función nueva:

1. **`core/metrics.py`** — añadir `repair_hints(metrics, change) -> list[str]`. Función pura
   que usa `change.pipeline` (ya calculado) y `metrics` para devolver hints ordenados por
   prioridad. Requiere importar `Change` y `PhaseState` desde `core/models`.

2. **`tui/spec_health.py`** — añadir columna `HINT` al final de la tabla. `_add_row()`
   llama a `repair_hints()`, toma el primer elemento, y lo pasa a `_hint_cell()` que
   aplica el color según el tipo. Los separadores reciben `""` como sexto argumento adicional.

## Arquitectura

```
SpecHealthScreen._add_row()
  → repair_hints(metrics, change)      ← core/metrics.py (nueva)
      uses change.pipeline (PhaseState)
      uses metrics.req_count / ears_count
  → _hint_cell(hint: str) -> Text      ← tui/spec_health.py (nueva helper)
      "/sdd-*"  → cyan
      "add ..." → yellow
      "✓"       → green
```

## Implementación de `repair_hints`

```python
def repair_hints(metrics: ChangeMetrics, change: Change) -> list[str]:
    hints: list[str] = []
    p = change.pipeline

    if p.propose == PhaseState.PENDING:
        hints.append(f"/sdd-propose {change.name}")
    if p.spec == PhaseState.PENDING:
        hints.append(f"/sdd-spec {change.name}")
        return hints  # REQ-RH-05: skip quality hints if spec is missing

    if p.design == PhaseState.PENDING:
        hints.append(f"/sdd-design {change.name}")
    if p.tasks == PhaseState.PENDING:
        hints.append(f"/sdd-tasks {change.name}")
    if p.apply == PhaseState.PENDING:
        hints.append(f"/sdd-apply {change.name}")
    if p.verify == PhaseState.PENDING:
        hints.append(f"/sdd-verify {change.name}")

    if metrics.req_count == 0:
        hints.append("add REQ-XX tags")
    elif metrics.ears_count < metrics.req_count:
        hints.append("add EARS tags")

    return hints if hints else ["✓"]
```

## Implementación de `_hint_cell`

```python
def _hint_cell(hint: str) -> Text:
    if hint == "✓":
        return Text(hint, style="green")
    if hint.startswith("/sdd-"):
        return Text(hint, style="cyan")
    return Text(hint, style="yellow")
```

## Cambios en `_add_row` y separadores

```python
# _add_row: añadir al final
hints = repair_hints(metrics, change)
hint_cell = _hint_cell(hints[0])
table.add_row(..., hint_cell, key=change.name)

# separadores: añadir "" al final
table.add_row(f"─── {project_name} ───", "", "", "", "", "", "")
table.add_row("── archived ──", "", "", "", "", "", "")
```

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `src/sdd_tui/core/metrics.py` | Añadir `repair_hints()`, importar `Change` y `PhaseState` |
| `src/sdd_tui/tui/spec_health.py` | Añadir columna `HINT`, helper `_hint_cell()`, actualizar separadores |
| `tests/test_metrics.py` | Tests para `repair_hints()` (todos los casos de la spec) |
| `tests/test_tui_spec_health.py` | Tests TUI: columna HINT visible con el hint correcto |

## Scope

- **Total archivos:** 4 (todos modificaciones)
- **Resultado:** Ideal < 10

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `repair_hints` en `core/metrics.py` | Archivo nuevo `core/hints.py` | No justifica nuevo módulo; `metrics.py` ya agrupa lógica de calidad de change |
| Early return si `spec == PENDING` | Condicional complejo | REQ-RH-05 explícito; claridad > brevedad |
| `_hint_cell` como helper module-level | Inline en `_add_row` | Testable y reutilizable; consistente con `_inactive_cell`, `_tasks_cell` |
| Color por prefijo del string | Enum de tipo de hint | El string ya es autodescriptivo; añadir enum sería sobreingeniería |
| Retorna lista completa, TUI toma `[0]` | Retorna solo el primero | Lista permite tests de orden completo sin abrir TUI |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_repair_hints_propose_pending` | Unit | Prioridad 1: `/sdd-propose` |
| `test_repair_hints_spec_pending` | Unit | Prioridad 2: `/sdd-spec`, no quality hints |
| `test_repair_hints_design_pending` | Unit | Prioridad 3: `/sdd-design` |
| `test_repair_hints_apply_pending` | Unit | Prioridad 5: `/sdd-apply` |
| `test_repair_hints_verify_pending` | Unit | Prioridad 6: `/sdd-verify` |
| `test_repair_hints_no_reqs` | Unit | Prioridad 7: `add REQ-XX tags` |
| `test_repair_hints_partial_ears` | Unit | Prioridad 8: `add EARS tags` |
| `test_repair_hints_all_ok` | Unit | Retorna `["✓"]` |
| `test_repair_hints_spec_pending_no_quality_hints` | Unit | REQ-RH-05: sin spec, sin quality hints |
| `test_spec_health_hint_column_visible` | TUI | Columna HINT en tabla |
| `test_spec_health_hint_sdd_apply` | TUI | Hint `/sdd-apply` cuando apply pending |
