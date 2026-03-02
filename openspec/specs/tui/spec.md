# Spec: TUI — View 2 (Change detail) + Navegación

## Metadata
- **Dominio:** tui
- **Change:** view-2-change-detail
- **Fecha:** 2026-03-02
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Primera spec del dominio `tui`. Define la navegación entre vistas y el
comportamiento de View 2 (detalle de un change seleccionado).

---

## 1. Navegación View 1 → View 2

### Comportamiento esperado

**Dado** View 1 con la lista de changes
**Cuando** el usuario pulsa Enter sobre una fila
**Entonces** se navega a View 2 mostrando el detalle del change seleccionado

**Dado** View 2 abierto
**Cuando** el usuario pulsa Esc
**Entonces** se vuelve a View 1

### Casos alternativos — navegación

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Lista vacía | No hay changes en View 1 | Enter no hace nada |
| `tasks.md` ausente | Change sin tareas | View 2 muestra "No tasks defined" |

- **RB-N1:** La navegación usa `push_screen` / `pop_screen` de Textual.
- **RB-N2:** View 1 mantiene el cursor en la fila seleccionada al volver con Esc.

---

## 2. View 2 — Change detail

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — {change-name}                                      │
├──────────────────────────────────┬──────────────────────────┤
│ TASKS                            │ PIPELINE                  │
│                                  │                           │
│  ✓ a1b2c3  T01  Create models   │   ✓  propose              │
│  ✓ d4e5f6  T02  Add reader      │   ✓  spec                 │
│  ·         T03  Add pipeline    │   ·  design               │
│  ── amendment: fix ──           │   ·  tasks                │
│  ·         T04  Fix bug         │   ·  apply                │
│                                  │   ·  verify               │
│                                  │                           │
├──────────────────────────────────┴──────────────────────────┤
│ [Esc] ← changes   [r] refresh                               │
└─────────────────────────────────────────────────────────────┘
```

### Panel izquierdo — Tasks

Cada tarea se muestra en una línea con formato:

```
  {state} {hash_or_pad}  {id}  {description}
```

| Campo | Committed | Pending |
|-------|-----------|---------|
| `state` | `✓` | `·` |
| `hash_or_pad` | hash 7 chars (ej: `a1b2c3d`) | 7 espacios |
| `id` | `T01` | `T01` |
| `description` | texto completo | texto completo |

Los separadores de amendment se muestran como línea de texto con estilo diferenciado:
```
  ── amendment: {nombre} ──
```

**Dado** un change sin `tasks.md`
**Cuando** se muestra View 2
**Entonces** el panel izquierdo muestra `No tasks defined yet`

### Panel derecho — Pipeline sidebar

Lista vertical con las 6 fases del pipeline:
```
  ✓  propose
  ✓  spec
  ·  design
  ·  tasks
  ·  apply
  ·  verify
```

`✓` = `PhaseState.DONE`, `·` = `PhaseState.PENDING`.

### Casos alternativos — View 2

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin tasks.md | `change.tasks == []` | Panel izq: "No tasks defined yet" |
| Tarea committed | `git_state == COMMITTED` | `✓ a1b2c3  T01  ...` |
| Tarea pending | `git_state == PENDING` | `·         T01  ...` |
| Con amendments | `task.amendment != None` | Separador `── amendment: X ──` antes del grupo |

### Reglas de presentación

- **RB-T1:** El hash se muestra siempre con exactamente 7 caracteres o 7 espacios (alineado).
- **RB-T2:** Los amendments se agrupan visualmente — el separador precede al primer task del grupo.
- **RB-T3:** El panel izquierdo es scrollable si hay más tareas que altura disponible.
- **RB-T4:** El panel derecho es fijo (no scrollable — máximo 6 fases).

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `push_screen` / `pop_screen` | Swap de widget en mismo screen | Patrón Textual estándar, mantiene historial |
| Panel split horizontal (izq/der) | Layout vertical | Permite ver tasks + pipeline simultáneamente |
| No seleccionable por ahora | ListView con cursor | View 3 (diff) va en siguiente change |
| Header con nombre del change | Header genérico | Orientación al usuario sin breadcrumb |

## Abierto / Pendiente

Ninguno.
