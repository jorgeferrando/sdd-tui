# Design: Pipeline Next Action

## Metadata
- **Change:** pipeline-next-action
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** draft

## Resumen Técnico

`PipelinePanel` recibirá el nombre del change (`name: str`) como parámetro adicional.
`_build_content()` añadirá una línea `NEXT` al final usando una función pura
`next_command(pipeline, tasks, name) -> str` extraída de `_build_next_command()`.

`ChangeDetailScreen.action_copy_next_command()` delegará a esa misma función,
eliminando la duplicación lógica actual.

## Arquitectura

```
ChangeDetailScreen
  ├── compose() → PipelinePanel(pipeline, tasks, metrics, name=change.name)
  ├── action_copy_next_command() → next_command(pipeline, tasks, name)  ← función pura
  └── action_refresh_view() → PipelinePanel(..., name=change.name)

PipelinePanel
  └── _build_content()
        └── ...existing lines...
            + ""
            + f"  NEXT  {next_command(pipeline, tasks, name)}"
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | Extraer `next_command()` como función module-level; añadir `name` a `PipelinePanel.__init__`; añadir línea NEXT en `_build_content()` | REQ-NA-01..08 |
| `tests/test_tui_change_detail.py` | Tests unitarios de `next_command()` + tests de `PipelinePanel._text` con NEXT | Cobertura de la nueva funcionalidad |

## Scope

- **Total archivos:** 2
- **Resultado:** Ideal

## Cambios detallados en `change_detail.py`

### 1. Nueva función module-level `next_command`

```python
def next_command(pipeline: Pipeline, tasks: list[Task], name: str) -> str:
    if pipeline.propose == PhaseState.PENDING:
        return f'/sdd-propose "{name}"'
    if pipeline.spec == PhaseState.PENDING:
        return f"/sdd-spec {name}"
    if pipeline.design == PhaseState.PENDING:
        return f"/sdd-design {name}"
    if pipeline.tasks == PhaseState.PENDING:
        return f"/sdd-tasks {name}"
    if pipeline.apply == PhaseState.PENDING:
        next_task = next((t for t in tasks if not t.done), None)
        if next_task:
            return f"/sdd-apply {next_task.id}"
        return f"/sdd-apply {name}"
    if pipeline.verify == PhaseState.PENDING:
        return f"/sdd-verify {name}"
    return f"/sdd-archive {name}"
```

### 2. `PipelinePanel.__init__` — nuevo param `name`

```python
def __init__(
    self,
    pipeline: Pipeline,
    tasks: list[Task],
    metrics: ChangeMetrics | None = None,
    pr_status: PrStatus | None | object = _PR_LOADING,
    ci_status: CiStatus | None | object = _CI_LOADING,
    name: str = "",                         # ← nuevo, con default para BC
) -> None:
    self._name = name
    ...
```

### 3. `_build_content` — línea NEXT al final

```python
lines.append("")
lines.append(f"  NEXT  {next_command(pipeline, tasks, name)}")
return "\n".join(lines)
```

La línea NEXT se añade **después** de CI, separada por línea en blanco.
`name` se pasa como parámetro adicional a `_build_content`.

### 4. `update_pr` / `update_ci` — pasar `self._name`

Internamente ya llaman a `_build_content(self._pipeline, self._tasks, self._metrics, ...)`.
Solo hay que añadir `self._name` a esas llamadas.

### 5. `action_copy_next_command` — delegar a la función pura

```python
def action_copy_next_command(self) -> None:
    cmd = next_command(self._change.pipeline, self._change.tasks, self._change.name)
    self.app.copy_to_clipboard(cmd)
    self.notify(f"Copied: {cmd}")
```

Eliminar `_build_next_command` (ahora redundante).

### 6. Instanciación de `PipelinePanel` — añadir `name`

Dos lugares:
- `ChangeDetailScreen.compose()`: `PipelinePanel(..., name=self._change.name)`
- `ChangeDetailScreen.action_refresh_view()`: `PipelinePanel(..., name=self._change.name)`

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_next_command_propose_pending` | Unit | `next_command` retorna `/sdd-propose "foo"` cuando propose PENDING |
| `test_next_command_spec_pending` | Unit | `/sdd-spec foo` cuando spec PENDING |
| `test_next_command_design_pending` | Unit | `/sdd-design foo` |
| `test_next_command_tasks_pending` | Unit | `/sdd-tasks foo` |
| `test_next_command_apply_pending_with_task` | Unit | `/sdd-apply T03` cuando primera tarea pendiente es T03 |
| `test_next_command_apply_pending_no_task` | Unit | `/sdd-apply foo` cuando tasks list vacía o todas done |
| `test_next_command_verify_pending` | Unit | `/sdd-verify foo` |
| `test_next_command_all_done` | Unit | `/sdd-archive foo` |
| `test_pipeline_panel_shows_next_line` | Unit | `PipelinePanel._text` contiene `NEXT` |
| `test_pipeline_panel_next_shows_correct_command` | Unit | `NEXT  /sdd-spec foo` cuando spec PENDING |
| `test_pipeline_panel_next_not_updated_on_pr` | Unit | NEXT no cambia tras `update_pr()` |

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `next_command` como función module-level | Método de `PipelinePanel` | Pura, testable sin TUI, reutilizada por Screen |
| `name` con default `""` en PipelinePanel | Sin default | Backwards-compatible con tests existentes que instancian sin name |
| Eliminar `_build_next_command` (redundante) | Mantener ambas | DRY — una sola fuente de verdad para la lógica |
| NEXT no depende de PR/CI | Recalcular en update_pr/update_ci | Solo depende de pipeline state y tasks; no hay que propagarlo |

## Notas de Implementación

- `next_command` debe exportarse para poder importarla en tests directamente
- El default `name=""` en `PipelinePanel` evita romper tests existentes que no pasan `name`
- Los tests unitarios de `next_command` no necesitan Textual — son pytest puros
