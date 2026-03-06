# Spec: TUI — Pipeline Next Action

## Metadata
- **Dominio:** tui
- **Change:** pipeline-next-action
- **Fecha:** 2026-03-06
- **Versión:** 1.0
- **Estado:** draft

## Contexto

`PipelinePanel` en View 2 muestra el estado de cada fase SDD. El usuario
sabe qué está hecho pero no qué debe hacer a continuación sin pulsar `Space`
(que copia el comando al portapapeles con una notificación).

Este cambio hace visible la siguiente acción directamente en el panel,
eliminando la fricción de descubrir el binding.

## Comportamiento Actual

`PipelinePanel._build_content()` genera texto con PIPELINE + fases + REQ + PR + CI.
La lógica de "qué sigue" existe en `ChangeDetailScreen._build_next_command()`
(privada al Screen, no expuesta en el panel).

---

## Requisitos (EARS)

- **REQ-NA-01** `[Ubiquitous]` The `PipelinePanel` SHALL display a `NEXT` line showing the next recommended SDD command for the active change.

- **REQ-NA-02** `[Ubiquitous]` The `NEXT` line SHALL follow the same resolution logic as `_build_next_command()`: first pending phase wins; if all phases DONE, shows `/sdd-archive {name}`.

- **REQ-NA-03** `[Ubiquitous]` The `NEXT` line SHALL be positioned after the CI line, separated by a blank line.

- **REQ-NA-04** `[Ubiquitous]` The `NEXT` line format SHALL be `  NEXT  {command}` — aligned with other panel rows.

- **REQ-NA-05** `[Unwanted]` If the pipeline has all phases DONE, the `NEXT` line SHALL show `/sdd-archive {name}`.

- **REQ-NA-06** `[State]` While `pipeline.apply == PENDING` and tasks exist, the `NEXT` line SHALL show the first uncompleted task: `/sdd-apply {task_id}` if found, else `/sdd-apply {name}`.

- **REQ-NA-07** `[Ubiquitous]` The `_build_next_command` function SHALL be extractable and testable in isolation (pure function — no TUI state needed).

- **REQ-NA-08** `[Unwanted]` The `NEXT` line SHALL NOT update when PR or CI status loads — it only depends on pipeline phase state and tasks.

### Escenarios de verificación

**REQ-NA-02** — resolución en orden

| Estado de pipeline | NEXT mostrado |
|-------------------|---------------|
| `propose=PENDING` | `/sdd-propose {name}` |
| `propose=DONE`, `spec=PENDING` | `/sdd-spec {name}` |
| `spec=DONE`, `design=PENDING` | `/sdd-design {name}` |
| `design=DONE`, `tasks=PENDING` | `/sdd-tasks {name}` |
| `tasks=DONE`, `apply=PENDING`, primera tarea pendiente `T03` | `/sdd-apply T03` |
| `tasks=DONE`, `apply=PENDING`, todas las tareas done | `/sdd-apply {name}` |
| `apply=DONE`, `verify=PENDING` | `/sdd-verify {name}` |
| todo DONE | `/sdd-archive {name}` |

**REQ-NA-04** — formato visual

```
PIPELINE

  ✓    propose
  ✓    spec
  ✓    design
  ✓    tasks
  3/5  apply
  ·    verify

  REQ: 12 (83%)

  …    PR
  ✓    CI

  NEXT  /sdd-apply T04
```

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| NEXT al final del panel | NEXT al inicio | Pipeline top→down es el diseño; NEXT es conclusión natural |
| Separador de línea en blanco antes de NEXT | Sin separador | Visualmente agrupa PR/CI juntos y NEXT como sección propia |
| `  NEXT  {cmd}` (label + cmd) | Icono como `  ▶    {cmd}` | Más legible; sin necesidad de recordar icono |
| La lógica permanece en `tui/change_detail.py` | Mover a `core/pipeline.py` | Es TUI-concern (genera comandos de skill, no lógica de dominio) |
| No actualizar NEXT en update_pr/update_ci | Recalcular siempre | NEXT no depende de PR/CI — recalcular sería over-engineering |

## Abierto / Pendiente

Ninguno.
