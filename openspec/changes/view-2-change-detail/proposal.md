# Proposal: View 2 — Change detail con task states y git info

## Metadata
- **Change:** view-2-change-detail
- **Jira:** N/A
- **Fecha:** 2026-03-02
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

View 1 muestra el estado del pipeline por change (a nivel de fase SDD).
Pero no permite ver qué tareas concretas hay dentro de un change ni si
están commiteadas en git. Al navegar a un change, el usuario quiere saber:
- ¿Qué tareas tiene este change?
- ¿Cuáles están commiteadas? ¿Con qué hash?
- ¿Cuáles están pendientes?
- ¿En qué fase del pipeline SDD está?

## Solución Propuesta

Al pulsar Enter sobre un change en View 1, se navega a View 2:
un layout de dos paneles.

**Panel izquierdo — Task list:**
```
  ✓ a1b2c3  T01  Create pyproject.toml
  ✓ d4e5f6  T02  Add core models
  ·         T03  Add EpicsView
  ── amendment: fix refresh ──
  ·         T04  Fix refresh bug
```

**Panel derecho — Pipeline sidebar:**
```
PIPELINE
  ✓  propose
  ✓  spec
  ✓  design
  ✓  tasks
  ~  apply
  ·  verify
```

Esc vuelve a View 1.

Para detectar si una tarea está commiteada, se busca en `git log` usando
el hint de commit documentado en tasks.md (`- Commit: ...`).

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Estado solo desde tasks.md (`[x]`/`[ ]`) | Simple | No muestra hash real de git | Descartada |
| Buscar por descripción libre en git log | Sin cambios en formato | Impreciso, falsos positivos | Descartada |
| **Hint de commit en tasks.md + git log** | Preciso, hash real | Requiere formato en tasks.md | **Elegida** |
| Buscar por TXX en mensaje de commit | Sencillo | No es nuestro formato de commit | Descartada |

## Impacto Estimado

- **Dominio:** core/models, core/pipeline, core/git_reader, tui
- **Archivos:** 9 → Proceder
- **Tests nuevos:** ~5 (git_reader.find_commit + task git state + bold format fix)
- **Breaking changes:** Sí — `Task` gana campos nuevos con defaults, tests actualizados
- **Ramas dependientes:** No

### Archivos afectados

```
Modificar:
  src/sdd_tui/core/models.py      ← CommitInfo, TaskGitState, Task extendido
  src/sdd_tui/core/pipeline.py    ← fix bold **TXX**, capturar commit hints
  src/sdd_tui/core/git_reader.py  ← añadir find_commit()
  src/sdd_tui/core/reader.py      ← poblar task git states al cargar
  src/sdd_tui/tui/epics.py        ← binding Enter → navegar
  src/sdd_tui/tui/app.py          ← push_screen / pop_screen
  tests/test_pipeline.py          ← actualizar para bold format + commit hints

Crear:
  src/sdd_tui/tui/change_detail.py  ← ChangeDetailView (dos paneles)
  tests/test_git_reader.py          ← tests de find_commit()
```

## Criterios de Éxito

- [ ] Enter en View 1 navega a View 2 del change seleccionado
- [ ] Esc en View 2 vuelve a View 1
- [ ] Tasks commiteadas muestran `✓ <hash>` (7 chars)
- [ ] Tasks pendientes muestran `·`
- [ ] Amendments se muestran como separadores visuales
- [ ] Pipeline sidebar muestra el estado de las 6 fases
- [ ] Tests pasan (`uv run pytest`)

## Preguntas Abiertas

- [x] ¿Qué muestra si tasks.md no existe?
  → Mensaje "No tasks defined yet" en el panel izquierdo
- [x] ¿Hash corto de cuántos caracteres?
  → 7 (estándar git)

## Notas

- Bug detectado: TaskParser actual no maneja `**TXX**` (negrita en tasks.md).
  Se corrige en este change como parte de la extensión del parser.
- El hint de commit en tasks.md tiene formato: `  - Commit: \`[change] Message\``
- Textual navigation: push_screen() / pop_screen() — patrón estándar
