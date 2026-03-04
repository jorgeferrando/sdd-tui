# Spec: TUI — Navegación + View 2 (Change detail) + View 4 (Document viewer) + View 5 (Clipboard launcher)

## Metadata
- **Dominio:** tui
- **Change:** openspec-enrichment
- **Fecha:** 2026-03-04
- **Versión:** 0.9
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

Lista vertical con las 6 fases del pipeline más badge REQ:
```
  PIPELINE

  ✓  propose
  ✓  spec
  ·  design
  ·  tasks
 2/4 apply    ← si apply está PENDING y hay tareas hechas
  ·  verify

  REQ: 5 (80%)   ← o "REQ: —" si no hay specs
```

`✓` = `PhaseState.DONE`, `·` = `PhaseState.PENDING`, `N/M` = progreso parcial.

**Badge REQ:** línea extra bajo las fases, calculada con `parse_metrics()`:
- `req_count == 0` → `REQ: —`
- `req_count > 0` → `REQ: {req_count} ({pct}%)` donde `pct = round(ears_count / req_count * 100)`
- Se recomputa en cada refresh (`r`) de View 2.

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
| `priority=True` en binding Space | Sin priority | DataTable consume Space antes de que llegue al Screen |
| `_build_next_command` separado de la action | Lógica inline | Testable de forma aislada |
| `copy_to_clipboard` nativo de Textual | `pyperclip` / `subprocess pbcopy` | Sin deps nuevas; API nativa ≥ 0.70.0 |
| `.remove()` + `.mount()` para refresh | Re-compose completa | Quirúrgico; Textual soporta mount/remove en widgets montados |
| `refresh_changes()` retorna `list[Change]` | Segunda llamada a `_load_changes()` | Evita doble carga del filesystem |
| `row_key` para selección en EpicsView | Índice de fila | El separador `── archived ──` rompe la correspondencia índice→change |
| `Change.archived: bool` | Path-based detection | El modelo conoce su origen; EpicsView no necesita inspeccionar paths |
| Separator row sin key | Fila con key especial | `_change_map.get()` devuelve None para rows sin key — comportamiento natural |

## Abierto / Pendiente

Ninguno.

---

## 4. View 5 — Clipboard command launcher

### Keybinding en View 2

| Tecla | Acción |
|-------|--------|
| `Space` | Copia al portapapeles el comando SDD correspondiente a la siguiente fase pendiente |

El binding usa `priority=True` para que el `Screen` lo capture antes que el `DataTable` (que usaría `Space` para `select_cursor`).

### `action_copy_next_command`

**Dado** View 2 abierto con un change en cualquier estado de pipeline
**Cuando** el usuario pulsa `Space`
**Entonces:**
- Se calcula el comando SDD de la siguiente fase pendiente
- El comando se copia al portapapeles (`self.app.copy_to_clipboard`)
- Aparece una notificación `Copied: {cmd}` (toast nativo de Textual)

### `_build_next_command` — lógica de resolución

| Fase pendiente | Comando generado |
|----------------|-----------------|
| `propose` | `/sdd-propose "{name}"` (con comillas) |
| `spec` | `/sdd-spec {name}` |
| `design` | `/sdd-design {name}` |
| `tasks` | `/sdd-tasks {name}` |
| `apply` (con tarea pendiente) | `/sdd-apply {next_task.id}` |
| `apply` (sin tarea pendiente) | `/sdd-apply {name}` |
| `verify` | `/sdd-verify {name}` |
| todas DONE | `/sdd-archive {name}` |

La resolución es secuencial — se evalúa la primera fase con `PhaseState.PENDING`.

### Reglas de negocio

- **RB-V5-01:** `Space` con `priority=True` — siempre capturado por `ChangeDetailScreen`, no por `DataTable`.
- **RB-V5-02:** El comando usa el ID de la primera tarea pendiente (no del change) cuando `apply` está pendiente.
- **RB-V5-03:** La notificación desaparece sola (toast nativo de Textual, sin timeout custom).
- **RB-V5-04:** Cuando todas las fases están DONE, el comando es `/sdd-archive` (cierre del ciclo).

---

## 5. View 6 — Refresh in-place

### Comportamiento de `r` en View 2

**Dado** View 2 (ChangeDetailScreen) abierto con un change seleccionado
**Cuando** el usuario pulsa `r`
**Entonces:**
- Los datos del change se recargan desde disco y git
- `TaskListPanel` y `PipelinePanel` se reemplazan con instancias frescas (`.remove()` + `.mount()`)
- `DiffPanel` muestra el placeholder `Select a task to view its diff`
- La pantalla sigue siendo View 2 (no hay `pop_screen`)
- `EpicsView` (View 1) también se actualiza con los datos frescos
- El `DataTable` recupera el foco vía `call_after_refresh`

### Caso — change desaparecido

**Dado** View 2 abierto con un change que ha sido eliminado del filesystem
**Cuando** el usuario pulsa `r`
**Entonces** aparece `Change not found — returning to list` y se hace `pop_screen`

### Reglas de negocio

- **RB-V6-01:** `r` recarga en sitio — no cierra View 2.
- **RB-V6-02:** El DiffPanel se resetea al placeholder tras cada refresh.
- **RB-V6-03:** View 1 se actualiza en el mismo refresh (`refresh_changes()` retorna `list[Change]`).
- **RB-V6-04:** Si el change no existe tras recargar → `pop_screen` + notify.
- **RB-V6-05:** El DataTable recupera el foco después del refresh vía `call_after_refresh`.

---

## 6. View 7 — Mostrar/ocultar archivados en View 1

### Toggle `a` en View 1

**Dado** View 1 mostrando solo changes activos (estado por defecto)
**Cuando** el usuario pulsa `a`
**Entonces** la lista se recarga mostrando activos + archivados, separados por `── archived ──`

**Dado** View 1 mostrando activos + archivados
**Cuando** el usuario pulsa `a`
**Entonces** la lista vuelve a mostrar solo activos

### Selección de archivados

**Dado** View 1 con archivados visibles
**Cuando** el usuario pulsa Enter sobre un archivado
**Entonces** se abre View 2 (ChangeDetailScreen) con ese change

### Reglas de negocio

- **RB-V7-01:** El estado del toggle es local a la sesión (no persiste).
- **RB-V7-02:** Por defecto, los archivados están ocultos.
- **RB-V7-03:** Los archivados se cargan desde `openspec/changes/archive/*/`.
- **RB-V7-04:** El separador `── archived ──` no tiene key → Enter sobre él no hace nada.
- **RB-V7-05:** La selección usa `row_key` (no índice) para soportar la fila separadora.
- **RB-V7-06:** `r` recarga respetando el estado del toggle (`_show_archived`).
- **RB-V7-07:** `Change.archived: bool = False` marca el origen; activos tienen `False`, archivados `True`.

---

## 7. View 8 — Spec Health Dashboard

### Navegación

| Tecla | Desde | Acción |
|-------|-------|--------|
| `H` | View 1 (EpicsView) | Abre `SpecHealthScreen` via `push_screen` |
| `Esc` | SpecHealthScreen | Vuelve a View 1 |

`SpecHealthScreen` recibe `include_archived: bool` (estado del toggle `a` de View 1).

### Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ sdd-tui — spec health                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ CHANGE              REQ  EARS%  TASKS   ARTIFACTS    INACTIVE            │
│ view-8-spec-health   19  100%   6/6    P S D T       0d                 │
│ view-9-delta-specs    0   —     0/4    P . . .       —                  │
├─────────────────────────────────────────────────────────────────────────┤
│ [H] health   [Esc] ← changes                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Columnas

| Columna | Contenido | Fuente |
|---------|-----------|--------|
| `CHANGE` | Nombre del change | `change.name` |
| `REQ` | Requisitos únicos, `—` si 0 | `ChangeMetrics.req_count` |
| `EARS%` | `{pct}%` si req > 0, `—` si 0 | `ears_count / req_count * 100` |
| `TASKS` | `done/total`, `—` si sin tasks | `change.tasks` |
| `ARTIFACTS` | Iniciales P/S/R/D/T (`.` si ausente) | `ChangeMetrics.artifacts` |
| `INACTIVE` | `{N}d`, `!{N}d` si > 7, `—` si None | `ChangeMetrics.inactive_days` |

**Columna R (research):** solo aparece si al menos un change tiene `research.md`.

### Alertas

- `req_count == 0` → fila completa en amarillo (`Rich.Text style="yellow"`)
- `inactive_days > INACTIVE_THRESHOLD_DAYS` → celda INACTIVE con prefijo `!` + amarillo

### Casos alternativos

| Escenario | Resultado |
|-----------|-----------|
| Sin changes visibles | `Static("No active changes")` en lugar de DataTable |
| Archivados visibles | Separador `── archived ──` sin key (igual que View 1) |
| Change sin tasks | `TASKS = —` |
| git no disponible | `INACTIVE = —` (sin alerta) |

### Reglas de negocio

- **RB-V8-01:** `H` usa `push_screen(SpecHealthScreen(changes, _show_archived))` — respeta estado del toggle.
- **RB-V8-02:** `DataTable` con `cursor_type="row"` y `show_header=True`.
- **RB-V8-03:** Métricas computadas en `on_mount` — una llamada a `parse_metrics()` por change.
- **RB-V8-04:** El separador `── archived ──` no tiene key → Enter no hace nada.

---

## 8. View 9 — Spec Evolution Viewer + Decisions Timeline

### Navegación

| Tecla | Desde | Acción |
|-------|-------|--------|
| `E` | View 2 (ChangeDetailScreen) | Abre `SpecEvolutionScreen` via `push_screen` con el change actual |
| `X` | View 1 (EpicsView) | Abre `DecisionsTimeline` via `push_screen` |
| `Esc` | SpecEvolutionScreen / DecisionsTimeline | Vuelve a la vista anterior |

### SpecEvolutionScreen

Muestra el delta spec del change activo con secciones ADDED/MODIFIED/REMOVED coloreadas.
Toggle `D` alterna entre vista delta y spec canónica completa.

#### Layout condicional

| Condición | Layout |
|-----------|--------|
| 0 dominios | `Static("No specs found for this change")` |
| 1 dominio | Sin panel izquierdo — diff full-width |
| N dominios | Panel izquierdo (lista de dominios) + panel derecho (diff) |

#### Coloreado de secciones (delta mode)

| Sección | Estilo Rich |
|---------|-------------|
| `## ADDED` | `bold green` header + `green` líneas |
| `## MODIFIED` | `bold yellow` header + `yellow` líneas |
| `## REMOVED` | `bold red` header + `red` líneas |

Si `fallback=True` (sin marcadores) → renderizar como `rich.Markdown` sin colores.

#### Toggle `D` — canonical mode

Alterna entre delta view (`parse_delta`) y spec canónica en `openspec/specs/{domain}/spec.md`.
Si la canónica no existe → `"No canonical spec found for {domain}"`.

El título refleja el modo: `sdd-tui — {change} / spec evolution [delta]` / `[canonical]`.

### DecisionsTimeline

Pantalla scrollable que agrega todas las decisiones de los changes archivados.

- Lee `openspec/changes/archive/` via `collect_archived_decisions`
- Muestra solo los changes que tienen al menos una decisión
- Orden: fecha ascendente (más antiguo primero)

#### Formato de cada change

```
── {change_name} ({archive_date}) ──    (bold cyan)
  • {decision}                          (white)
    vs: {alternative}                   (dim)
    why: {reason}                       (italic)
```

Si no hay decisions en ningún archivado → `"No archived decisions found"`.

### Reglas de negocio

- **RB-V9-01:** `SpecEvolutionScreen` omite panel izquierdo si el change tiene exactamente 1 dominio.
- **RB-V9-02:** `D` toggle es estado local de la pantalla — no persiste entre aperturas.
- **RB-V9-03:** `DecisionsTimeline` filtra changes sin decisiones (`cd.decisions` vacío).
- **RB-V9-04:** `archive_dir` calculado como `Path.cwd() / "openspec" / "changes" / "archive"`.
- **RB-V9-05:** `SpecEvolutionScreen` inicia en modo delta (`_canonical_mode = False`).

---

## 10. View 1 — Steering viewer (binding S)

### Navegación

| Tecla | Desde | Acción |
|-------|-------|--------|
| `s` | View 1 (EpicsView) | Abre `DocumentViewerScreen` con `openspec/steering.md` |
| `Esc` | Steering viewer | Vuelve a View 1 |

### Comportamiento

**Dado** View 1 abierto
**Cuando** el usuario pulsa `s`
**Entonces** se abre `DocumentViewerScreen` con path `Path.cwd() / "openspec" / "steering.md"`
y título `"sdd-tui — steering"`

**Dado** Steering viewer abierto con `steering.md` inexistente
**Cuando** se monta la pantalla
**Entonces** muestra `"steering.md not found"` (comportamiento heredado de `DocumentViewerScreen`)

### Reglas de negocio

- **RB-S01:** No se crea una nueva clase `SteeringScreen` — se reutiliza `DocumentViewerScreen(path, title)`.
- **RB-S02:** El path se calcula como `Path.cwd() / "openspec" / "steering.md"` (consistente con otros paths en EpicsView).
- **RB-S03:** `DocumentViewerScreen` ya maneja el caso "not found" con mensaje `"steering.md not found"`.

---

## 11. View 2 — Requirements binding (q)

### Keybinding

| Tecla | Documento | Archivo |
|-------|-----------|---------|
| `q` | Requirements | `requirements.md` |

Añadido a los bindings existentes de View 2 (`p`, `d`, `s`, `t`).

### Comportamiento

**Dado** View 2 abierto con un change
**Cuando** el usuario pulsa `q`
**Entonces** se abre `DocumentViewerScreen` con `requirements.md` del change

**Dado** View 2 abierto y `requirements.md` ausente
**Cuando** el usuario pulsa `q`
**Entonces** el viewer muestra `"requirements.md not found"`

### Reglas de negocio

- **RB-RB01:** `q` sigue la convención de View 2 — letras minúsculas para documentos del change.
- **RB-RB02:** Implementado vía `_open_doc("requirements.md", "requirements")` — mismo patrón que `p`, `d`, `t`.

---

## 12. View 8 — SpecHealthScreen columna Q

### Columna ARTIFACTS actualizada

| Letra | Artefacto | Condición de aparición |
|-------|-----------|------------------------|
| `P` | proposal | siempre en el orden |
| `S` | spec | siempre en el orden |
| `R` | research | solo si algún change tiene `research.md` |
| `Q` | requirements | solo si algún change tiene `requirements.md` |
| `D` | design | siempre en el orden |
| `T` | tasks | siempre en el orden |

Ejemplo con R y Q presentes:
```
ARTIFACTS
P S R Q D T
P S . Q . .
P . . . D T
```

### Reglas de negocio

- **RB-HQ01:** La columna `Q` aparece solo si `any(change has requirements.md)` — mismo comportamiento que `R`.
- **RB-HQ02:** La letra para `requirements` es `Q` (de reQueriments) — no `R`, que ya está reservada para research.
- **RB-HQ03:** El orden de columnas es fijo: `P S [R] [Q] D T` donde `[R]` y `[Q]` son condicionales.

