# Design: View 5 — Clipboard command launcher

## Metadata
- **Change:** view-5-clipboard
- **Fecha:** 2026-03-03
- **Estado:** draft

## Resumen Técnico

Un único método `action_copy_next_command()` en `ChangeDetailScreen` recorre
el pipeline del change activo, construye el comando SDD correspondiente a la
primera fase pendiente, y lo copia al portapapeles via `self.app.copy_to_clipboard()`.
La notificación post-copia usa `self.notify()`. Un helper `_build_next_command()`
encapsula la lógica de construcción.

## Arquitectura

```
[Space] → ChangeDetailScreen.action_copy_next_command()
              │
              ├── _build_next_command()
              │     └── pipeline state → comando string
              │
              ├── self.app.copy_to_clipboard(cmd)
              └── self.notify(f"Copied: {cmd}")
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | Añadir binding `Space` + `action_copy_next_command` + `_build_next_command` | Toda la lógica vive en ChangeDetailScreen |

## Scope

- **Total archivos:** 1
- **Resultado:** Ideal

## Detalle de Implementación

### Binding

```python
Binding("space", "copy_next_command", "Copy cmd", priority=True)
```

`priority=True` es necesario para que `Space` se procese antes de que el
`DataTable` enfocado lo capture (DataTable usa Space para `select_cursor`).

### `_build_next_command(self) -> str`

```python
def _build_next_command(self) -> str:
    p = self._change.pipeline
    name = self._change.name

    if p.propose == PhaseState.PENDING:
        return f'/sdd-propose "{name}"'
    if p.spec == PhaseState.PENDING:
        return f"/sdd-spec {name}"
    if p.design == PhaseState.PENDING:
        return f"/sdd-design {name}"
    if p.tasks == PhaseState.PENDING:
        return f"/sdd-tasks {name}"
    if p.apply == PhaseState.PENDING:
        next_task = next((t for t in self._change.tasks if not t.done), None)
        if next_task:
            return f"/sdd-apply {next_task.id}"
        return f"/sdd-apply {name}"
    if p.verify == PhaseState.PENDING:
        return f"/sdd-verify {name}"
    return f"/sdd-archive {name}"
```

### `action_copy_next_command(self) -> None`

```python
def action_copy_next_command(self) -> None:
    cmd = self._build_next_command()
    self.app.copy_to_clipboard(cmd)
    self.notify(f"Copied: {cmd}")
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `priority=True` en binding | Sin priority | DataTable consume Space antes de que llegue al Screen |
| Helper `_build_next_command` separado | Lógica inline en action | Testable de forma aislada si se añaden tests más adelante |
| `copy_to_clipboard` de `self.app` | `pyperclip` o `subprocess pbcopy` | API nativa de Textual, sin deps nuevas |
| `notify()` sin timeout custom | Toast propio | `notify()` nativo es suficiente, desaparece solo |

## Tests Planificados

Sin tests automatizados nuevos — `copy_to_clipboard` y `notify` requieren
`Pilot` async (TUI testing) que el proyecto no tiene todavía. Cobertura
via smoke test en QG.

## Notas de Implementación

- `PhaseState` ya está importado en `change_detail.py` — sin imports nuevos
- `copy_to_clipboard` disponible en Textual ≥ 0.70.0 (proyecto usa 8.0.1) ✓
- El footer mostrará automáticamente `[Space] Copy cmd` gracias al binding
