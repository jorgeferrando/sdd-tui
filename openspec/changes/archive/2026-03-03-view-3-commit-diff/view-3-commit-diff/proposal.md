# Proposal: View 3 — Commit diff inline

## Metadata
- **Change:** view-3-commit-diff
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Proyecto:** sdd-tui
- **Estado:** approved

## Problema / Motivación

View 2 muestra qué tareas están commiteadas y con qué hash, pero no permite
inspeccionar el contenido del commit. El usuario quiere poder navegar por las
tareas de un change y ver el diff de cada una sin salir de la TUI.

Para tareas pendientes, es útil ver el diff del working tree actual — así el
usuario sabe qué cambios llevan asociados aunque aún no estén commiteados.

## Solución Propuesta

Dentro de View 2, el panel de tareas pasa a ser interactivo (DataTable con
cursor). Al mover el cursor sobre una tarea, un panel inferior muestra el diff:

```
┌──────────────────────────────────┬──────────────────────────┐
│ > ✓ a1b2c3  T01  Create models  │ PIPELINE                  │
│   ✓ d4e5f6  T02  Add reader     │   ✓  propose              │
│   ·         T03  Add pipeline   │   ·  apply                │
├──────────────────────────────────┴──────────────────────────┤
│ DIFF — [view-3] Create models                               │
│  diff --git a/core/models.py ...                            │
│  +@dataclass                                                │
│  +class CommitInfo: ...                                     │
│  (scrollable)                                               │
└─────────────────────────────────────────────────────────────┘
```

- **Tarea committed** → `git show {hash}` del commit asociado
- **Tarea pending** → `git diff HEAD` (working tree actual)
- **Sin cambios pendientes** → mensaje `No uncommitted changes`

El panel de tareas se ajusta al número de tareas (`height: auto`) y el panel
de diff ocupa el espacio restante (`height: 1fr`).

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Nueva screen (push_screen) | Pantalla completa para el diff | Pierde contexto del pipeline | Descartada |
| Panel inline (View 2 ampliado) | Contexto completo visible | Layout más complejo | **Elegida** |
| Solo committed, pending = nada | Más simple | Menos útil | Descartada |
| Pending → `git diff HEAD` | Muestra cambios actuales | Diff global, no filtrado por tarea | **Elegida** |

## Impacto Estimado

- **Dominio:** core/git_reader, tui/change_detail
- **Archivos:** 3 → Proceder
- **Tests nuevos:** 4 (GitReader.get_diff)
- **Breaking changes:** No — View 2 se amplía, sin cambios de interfaz externa

### Archivos afectados

```
Modificar:
  tests/test_git_reader.py            ← tests para get_diff() (RED)
  src/sdd_tui/core/git_reader.py      ← añadir get_diff() y get_working_diff()
  src/sdd_tui/tui/change_detail.py    ← TaskListPanel → DataTable + DiffPanel
```

## Criterios de Éxito

- [x] Navegar con cursor por las tareas en View 2
- [x] Tarea committed → muestra diff del commit en panel inferior
- [x] Tarea pending → muestra `git diff HEAD` (o mensaje si está limpio)
- [x] Panel de tareas se ajusta al número de tareas (sin espacio vacío excesivo)
- [x] Panel de diff ocupa el espacio restante
- [x] Tests pasan (`uv run pytest`)

## Notas

- `get_working_diff()` usa `git diff HEAD --no-color` para incluir staged + unstaged
- El diff de tarea pending es global (todo el repo), no filtrado por archivos
- Separadores de amendment en el DataTable: filas sin `key`, cursor puede pasar
  por ellas pero no actualizan el diff panel
