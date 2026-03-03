# Spec: TUI — View 3 (Commit diff inline)

## Metadata
- **Dominio:** tui
- **Change:** view-3-commit-diff
- **Fecha:** 2026-03-03
- **Versión:** 0.1
- **Estado:** draft

## Contexto

View 2 muestra las tareas de un change con su estado git. Actualmente el panel
de tareas no es interactivo. View 3 añade selección de tareas y muestra el diff
del commit asociado en un panel inferior de la misma pantalla.

---

## Comportamiento Actual (View 2)

- `TaskListPanel` es un `Static` — no interactivo, solo lectura.
- El layout de `ChangeDetailScreen` es horizontal: tasks (izq) + pipeline (der).
- No hay forma de inspeccionar el contenido de un commit.

---

## Comportamiento Esperado (Post-Cambio)

### Layout

```
┌──────────────────────────────────┬──────────────────────────┐
│ TASKS                            │ PIPELINE                  │
│                                  │                           │
│ > ✓ a1b2c3  T01  Create models  │   ✓  propose              │
│   ✓ d4e5f6  T02  Add reader     │   ✓  spec                 │
│   ·         T03  Add pipeline   │   ·  design               │
│   ── amendment: fix ──          │   ·  tasks                │
│   ·         T04  Fix bug        │  1/4  apply               │
│                                  │   ·  verify               │
├──────────────────────────────────┴──────────────────────────┤
│ DIFF — [view-2] Create models                               │
│                                                              │
│  diff --git a/src/sdd_tui/core/models.py ...               │
│  +++ b/src/sdd_tui/core/models.py                          │
│  @@ -1,3 +1,18 @@                                          │
│  +from dataclasses import dataclass                         │
│  +                                                          │
│  (scrollable)                                               │
├─────────────────────────────────────────────────────────────┤
│ [Esc] ← changes   [r] refresh                              │
└─────────────────────────────────────────────────────────────┘
```

El área superior (tasks + pipeline) ocupa aprox. 60% de altura.
El panel de diff inferior ocupa el 40% restante y es scrollable.

### Caso Principal — Tarea committed

**Dado** View 2 con una tarea COMMITTED seleccionada
**Cuando** el cursor se mueve a esa tarea (RowHighlighted)
**Entonces** el panel de diff muestra la salida de `git show {hash}` para ese commit

### Caso Alternativo — Tarea pending

**Dado** View 2 con una tarea PENDING seleccionada
**Cuando** el cursor se mueve a esa tarea (RowHighlighted)
**Entonces** el panel de diff muestra el output de `git diff HEAD` (working tree actual)
Si no hay cambios pendientes, muestra `No uncommitted changes`

### Caso Alternativo — Change sin tareas

**Dado** un change sin `tasks.md`
**Cuando** se abre View 2
**Entonces** el DataTable muestra "No tasks defined yet" y el panel diff está vacío

### Casos de edge

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| `git show` falla | Hash inválido o git no disponible | Diff panel: `Could not load diff` |
| Tarea pending, repo limpio | `git diff HEAD` vacío | Diff panel: `No uncommitted changes` |
| Primera carga | Al montar la pantalla sin cursor | Diff panel vacío o primera tarea seleccionada automáticamente |
| Separador de amendment | Fila de separador en DataTable | No se selecciona (fila no interactiva) |

---

## Componentes Afectados

### `TaskListPanel` — Reemplazar Static por DataTable

- Deja de ser un `ScrollableContainer` con `Static`
- Pasa a ser un `DataTable` con `cursor_type="row"` y `show_header=False`
- Columnas: `state` (1), `hash` (7), `id` (4), `description` (resto)
- Los separadores de amendment se añaden como filas no seleccionables (sin key)

### `DiffPanel` — Nuevo widget

- `ScrollableContainer` con un `Static` interior
- El contenido se actualiza con cada selección del DataTable
- Altura: ~40% de la pantalla (CSS `height: 2fr` en el panel superior, `height: 1fr` en diff)

### `ChangeDetailScreen` — Layout vertical

Layout nuevo: `Vertical` exterior con dos zonas:
1. `Horizontal` (tasks + pipeline) — zona superior
2. `DiffPanel` — zona inferior

---

## Reglas de Presentación

- **RB-V3-01:** El diff panel se actualiza en `on_data_table_row_highlighted`, no en `RowSelected` (más fluido al navegar con teclado).
- **RB-V3-02:** Las filas de separador de amendment no tienen `key` en el DataTable — no disparan eventos de selección.
- **RB-V3-03:** El diff panel muestra el output raw de `git show {hash}` (sin coloreado ANSI por ahora).
- **RB-V3-04:** Si al montar hay al menos una tarea, el cursor se posiciona en la primera tarea automáticamente, mostrando su diff (o "Not committed yet").

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Panel inferior (inline) | Push nueva screen | Permite navegar tareas y ver diffs sin perder contexto del pipeline |
| `RowHighlighted` en lugar de `RowSelected` | Enter para seleccionar | Experiencia más fluida — diff aparece al mover cursor, no requiere Enter |
| DataTable sin header | DataTable con header | Más compacto — las columnas son obvias por el contenido |
| `git show` raw | Parsear y colorear | Simplicidad; colorear puede añadirse en View 4+ |
| Separadores como filas sin key | Filtrar separadores fuera del DataTable | Mantiene la posición visual correcta entre tareas |

## Abierto / Pendiente

Ninguno.
