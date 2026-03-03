# Spec: TUI — Navegación + View 2 (Change detail) + View 4 (Document viewer)

## Metadata
- **Dominio:** tui
- **Change:** view-4-doc-viewer
- **Fecha:** 2026-03-03
- **Versión:** 0.3
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
│ TASKS (interactivo, DataTable)   │ PIPELINE                  │
│                                  │                           │
│ > ✓ a1b2c3  T01  Create models  │   ✓  propose              │
│   ✓ d4e5f6  T02  Add reader     │   ✓  spec                 │
│   ·         T03  Add pipeline   │   ·  design               │
│   ── amendment: fix ──          │   ·  tasks                │
│   ·         T04  Fix bug        │  2/4 apply                │
│                                  │   ·  verify               │
├──────────────────────────────────┴──────────────────────────┤
│ DIFF (scrollable)                                            │
│                                                              │
│  diff --git a/src/... b/src/...                             │
│  --- a/src/models.py                                         │
│  +++ b/src/models.py                                         │
│  (syntax highlighted, monokai)                              │
├─────────────────────────────────────────────────────────────┤
│ [Esc] ← changes   [r] refresh   [p] proposal   [d] design   │
│ [s] spec(s)   [t] tasks                                      │
└─────────────────────────────────────────────────────────────┘
```

### Panel izquierdo — Tasks (DataTable interactivo)

`TaskListPanel` es un `Widget` con `DataTable` interno (`cursor_type="row"`, `show_header=False`).

Cada tarea se muestra en una línea con formato:

```
  {state} {hash_or_pad}  {id}  {description}
```

| Campo | Committed | Pending |
|-------|-----------|---------|
| `state` | `✓` | `·` |
| `hash_or_pad` | hash 7 chars (ej: `a1b2c3d`) | 7 espacios |
| `id` | `T01`, `BUG01`, `MEJ01`… | ídem |
| `description` | texto completo | texto completo |

Los separadores de amendment se añaden como filas sin key:
```
  ── amendment: {nombre} ──
```

**Dado** un change sin `tasks.md`
**Cuando** se muestra View 2
**Entonces** el DataTable muestra `No tasks defined yet`

La altura del `TaskListPanel` se calcula dinámicamente después del primer render (`call_after_refresh`): muestra todas las tareas si caben, dejando al menos 10 filas para el panel inferior.

### Panel derecho — Pipeline sidebar

Lista vertical con las 6 fases del pipeline:
```
  PIPELINE

  ✓  propose
  ✓  spec
  ·  design
  ·  tasks
 2/4 apply    ← si apply está PENDING y hay tareas hechas
  ·  verify
```

`✓` = `PhaseState.DONE`, `·` = `PhaseState.PENDING`, `N/M` = progreso parcial.

### Panel inferior — DiffPanel

`DiffPanel` es un `ScrollableContainer` con un `Static` interior.

**Dado** View 2 abierto
**Cuando** el cursor se mueve a una tarea (`DataTable.RowHighlighted`)
**Entonces:**
- Si la tarea es `COMMITTED`: muestra `git show {hash}` con syntax highlighting (lexer=`diff`, tema=`monokai`)
- Si la tarea es `PENDING`: muestra `git diff HEAD` (working tree actual)
- Si no hay cambios pendientes: muestra `No uncommitted changes`
- Si `git show` falla: muestra `Could not load diff`

**Dado** View 2 recién abierto
**Cuando** no hay cursor activo
**Entonces** el panel muestra `Select a task to view its diff`

El contenido se resetea al top (`scroll_home`) en cada actualización.

### Casos alternativos — View 2

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin tasks.md | `change.tasks == []` | DataTable: "No tasks defined yet", diff: placeholder |
| Tarea committed | `git_state == COMMITTED` | `✓ a1b2c3  T01  ...` → diff del commit |
| Tarea pending | `git_state == PENDING` | `·         T01  ...` → working diff o mensaje |
| Con amendments | `task.amendment != None` | Separador `── amendment: X ──` antes del grupo |
| Fila de separador | Sin key en DataTable | No se procesa en el diff handler |

### Reglas de presentación

- **RB-T1:** El hash se muestra siempre con exactamente 7 caracteres o 7 espacios (alineado).
- **RB-T2:** Los amendments se agrupan visualmente — el separador precede al primer task del grupo.
- **RB-T3:** El panel de tareas es scrollable si hay más tareas que espacio visible.
- **RB-T4:** El panel derecho es fijo (no scrollable — máximo 6 fases + header).
- **RB-V3-01:** El diff panel se actualiza en `on_data_table_row_highlighted` (hover), no en `RowSelected` (Enter).
- **RB-V3-02:** Las filas de separador de amendment no tienen `key` → no disparan carga de diff.
- **RB-V3-03:** El diff muestra syntax highlighting con `rich.Syntax` (lexer=`diff`, tema=`monokai`).
- **RB-V3-04:** `DataTable` recibe focus explícito via `call_after_refresh` al montar la pantalla.

---

---

## 3. View 4 — Document viewer

### Keybindings en View 2

| Tecla | Documento | Archivo |
|-------|-----------|---------|
| `p` | Proposal | `proposal.md` |
| `d` | Design | `design.md` |
| `s` | Spec(s) | `specs/{dominio}/spec.md` |
| `t` | Tasks | `tasks.md` |

### `DocumentViewerScreen`

Pantalla de solo lectura para visualizar un archivo markdown.

- **Layout:** `Header` + `ScrollableContainer(Static)` + `Footer`
- **Título:** `sdd-tui — {change-name} / {doc-label}`
- **Contenido:** `rich.Markdown` renderizado dentro de un `Static`
- **Binding:** solo `Esc` (volver a View 2)

**Dado** View 2 con un change que tiene `proposal.md`
**Cuando** el usuario pulsa `p`
**Entonces** se abre `DocumentViewerScreen` con el contenido de `proposal.md` y título `sdd-tui — {change} / proposal`

**Dado** `DocumentViewerScreen` abierto
**Cuando** el usuario pulsa `Esc`
**Entonces** vuelve a View 2 con el estado previo intacto (tarea seleccionada, diff visible)

### `SpecSelectorScreen`

Pantalla de selección cuando hay múltiples dominios de spec.

- **Layout:** `Header` + `ListView` (un item por dominio) + `Footer`
- **Título:** `sdd-tui — {change-name} / specs`
- **Enter:** abre `DocumentViewerScreen` con el spec del dominio seleccionado
- **Esc:** vuelve a View 2

### Lógica de `[s]` en View 2

| Condición | Resultado |
|-----------|-----------|
| 0 dominios | `notify("No specs found")` — sin abrir pantalla |
| 1 dominio | Abre `DocumentViewerScreen` directamente |
| N dominios | Abre `SpecSelectorScreen` |

### Casos de edge

| Escenario | Resultado |
|-----------|-----------|
| Documento no existe | `DocumentViewerScreen` muestra `{archivo} not found` |
| Specs ausentes | Mensaje `No specs found` sin abrir selector |
| Documento vacío | Viewer muestra el archivo vacío sin error |

### Reglas de negocio

- **RB-V4-01:** El viewer es de solo lectura.
- **RB-V4-02:** Si el documento no existe → mensaje informativo; no lanzar excepción.
- **RB-V4-03:** Estado de View 2 preservado al volver con Esc (`push_screen`, no replace).
- **RB-V4-04:** Contenido renderizado con `rich.Markdown`.
- **RB-V4-05:** Un solo dominio de spec → abre viewer directo (sin selector).
- **RB-V4-06:** Bindings `p`, `d`, `s`, `t` siempre disponibles en View 2.

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `push_screen` / `pop_screen` | Swap de widget en mismo screen | Patrón Textual estándar, mantiene historial |
| Panel split horizontal (izq/der) + diff inferior | Solo layout horizontal | Permite ver tasks + pipeline + diff simultáneamente |
| `RowHighlighted` para cargar diff | Enter (`RowSelected`) | Más fluido — diff aparece al mover cursor |
| DataTable sin header | DataTable con header | Más compacto — columnas obvias por contenido |
| `rich.Syntax` para coloreado | Output raw / ANSI | Syntax highlighting correcto sin dependencias extra (rich ya es dependencia de Textual) |
| Altura dinámica via `call_after_refresh` | CSS `height: auto` | `height: auto` colapsa DataTable (ScrollView) en Textual |
| `PipelinePanel { height: auto }` | `height: 1fr` | `1fr` dentro de contenedor `height: auto` crea dependencia circular en Textual |
| `push_screen` para viewer | Panel inline en View 2 | Pantalla completa = mejor lectura; patrón ya establecido |
| `rich.Markdown` para viewer | `rich.Syntax` con lexer markdown | Renderiza semánticamente (headers, tablas, listas) |
| Actions separadas por doc | Action parametrizada | Más explícito; Textual action params tienen edge cases |
| `id="domain-{name}"` en ListItem | Indexar por posición | Más robusto que asumir orden en el evento |

## Abierto / Pendiente

Ninguno.
