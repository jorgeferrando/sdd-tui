# Proposal: pr-status — GitHub PR Status en Pipeline Sidebar

## Metadata
- **Change:** pr-status
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema / Motivación

El Pipeline sidebar de View 2 muestra el estado del flujo SDD (propose → verify),
pero no el estado de revisión del código en GitHub. Un change puede tener `verify = DONE`
y su PR en "changes requested" o sin reviewers. Esa información hoy requiere salir de la TUI.

**Nota:** Segunda de tres features del "observatory":
1. `observatory-v1` — Multi-project
2. `pr-status` — GitHub PR status (este change)
3. `velocity-metrics` — Métricas de throughput y lead time

**Prerequisito:** `startup-deps-check` — la detección de `gh` CLI y la notificación
al usuario si no está disponible se implementan allí. Este change asume que ese
mecanismo ya existe.

## Solución Propuesta

### Fila extra en PipelinePanel

Cuando `gh` CLI está disponible y hay PR asociado al change, el Pipeline sidebar añade:

```
  PIPELINE

  ✓  propose
  ✓  spec
  ✓  design
  ✓  tasks
  ✓  apply
  ✓  verify

  ⧗  PR #1234  2✓ 1✗
```

| Símbolo | Significado |
|---------|-------------|
| `⧗` | PR abierto |
| `✓` | PR mergeado |
| `✗` | PR cerrado sin merge |
| `—` | Sin PR / gh no disponible |

El conteo `2✓ 1✗` indica: 2 approvals, 1 changes_requested.

### Resolución del PR

Para asociar un PR a un change se usa la rama git asociada al change.
Estrategia: `gh pr list --json number,title,headRefName,state,reviews` filtrado
por `headRefName` que contenga el nombre del change.

Degradación silenciosa en esta capa si:
- No hay PR abierto para el change (muestra `—`)
- El comando `gh` falla por razón de red o permisos (muestra `—`)

La ausencia de `gh` CLI se comunica al usuario en startup via `startup-deps-check`,
no en esta capa.

### Carga asíncrona

La fila de PR se carga en un worker async (`@work(thread=True)`) al abrir View 2.
Mientras carga: `…  PR`. Si falla o no hay PR: `—`.

## Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|---------------|
| GitHub API directa | Requiere token management; `gh` CLI ya autentica |
| Polling periódico en View 2 | Demasiado intrusivo; carga manual con `r` es suficiente |
| Nuevo binding `P` para abrir PR en browser | Complementario, no excluyente; scope de v2 |

## Impacto Estimado

| Archivo | Cambio |
|---------|--------|
| `core/github.py` | Nuevo: `get_pr_status(change_name, cwd) -> PrStatus \| None` via `gh` CLI |
| `tui/change_detail.py` | `PipelinePanel` añade fila PR; worker async para cargarlo |
| `tests/test_github.py` | Nuevo: tests unitarios con subprocess mock |
| `tests/test_tui_change_detail.py` | Casos con PR status |

Estimación: ~4 archivos, ~15 tests nuevos.

## Criterios de Exito

- [ ] `PipelinePanel` muestra fila PR cuando `gh` devuelve resultado
- [ ] La fila muestra `—` cuando no hay PR o `gh` no está disponible
- [ ] La carga es asíncrona (no bloquea la apertura de View 2)
- [ ] `r` recarga también el PR status
- [ ] Tests >= 126 (actualmente 111 + los de `observatory-v1`)
