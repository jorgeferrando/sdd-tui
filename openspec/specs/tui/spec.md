# Spec: TUI — Navegación + View 2 (Change detail) + View 4 (Document viewer) + View 5 (Clipboard launcher)

## Metadata
- **Dominio:** tui
- **Change:** observatory-v1
- **Fecha:** 2026-03-05
- **Versión:** 1.6
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
- **RB-V3-01:** El diff panel se actualiza en `on_data_table_row_highlighted` (hover), no en `RowSelected` (Enter). La carga ocurre en un worker asíncrono (`@work(thread=True, exclusive=True)`); el handler síncrono solo muestra el placeholder y lanza el worker.
- **RB-V3-02:** Las filas de separador de amendment no tienen `key` → no disparan carga de diff.
- **RB-V3-03:** El diff muestra syntax highlighting con `rich.Syntax` (lexer=`diff`, tema=`monokai`).
- **RB-V3-04:** `DataTable` recibe focus explícito via `call_after_refresh` al montar la pantalla.
- **RB-ASYNC-01:** `on_data_table_row_highlighted` muestra `"[dim]Loading diff…[/dim]"` inmediatamente y llama `_load_diff_worker(task)` (recibe el objeto `Task`, no el `task_id`).
- **RB-ASYNC-02:** `exclusive=True` garantiza que solo hay un worker de diff activo; Textual cancela el anterior automáticamente al lanzar uno nuevo.
- **RB-ASYNC-03:** El worker actualiza el DiffPanel via `self.app.call_from_thread(_update_diff_panel, text, as_diff)` — `Screen` no expone `call_from_thread`, solo `App`.
- **RB-ASYNC-04:** El contenido del diff (syntax highlighting con `rich.Syntax`) es idéntico al comportamiento pre-async — la construcción de `Syntax` ocurre en `DiffPanel.show_diff` (event loop).
- **RB-ASYNC-05:** Las filas de separador no tienen key → no llaman `_load_diff_worker` — comportamiento idéntico al actual.

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
| `@work(thread=True, exclusive=True)` para diff | `subprocess` síncrono | Desbloquea event loop; `exclusive=True` cancela workers anteriores en nav rápida |
| `self.app.call_from_thread` | `self.call_from_thread` | `Screen` no hereda `call_from_thread`; solo `App` lo expone en Textual 8.x |
| Pasar `Task` al worker (no `task_id`) | Lookup `query_one` desde hilo | Evita acceso a widgets fuera del event loop — más thread-safe |
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

---

## 13. UX Feedback — Estado Visual y Notificaciones

### View 1 — Toggle archived label dinámico

El binding `a` en `EpicsView` muestra un label dinámico según el estado:

| Estado `_show_archived` | Label en footer |
|------------------------|-----------------|
| `False` (por defecto) | `Show archived` |
| `True` | `Hide archived` |

Implementación: `action_toggle_archived` asigna `self.BINDINGS` como atributo de instancia con el nuevo label y llama `self.refresh_bindings()` para invalidar el caché del footer.

- **RB-UX01:** El label se actualiza de forma inmediata (sin delay) tras el toggle.
- **RB-UX02:** `self.BINDINGS` de instancia sombrea el `BINDINGS` de clase — patrón Textual estándar para labels dinámicos.

### View 1 — Notify en refresh

`action_refresh` emite una notificación tras completar la recarga:

```
"{n_active} changes loaded ({n_archived} archived)"
```

donde `n_active` = changes con `archived == False` y `n_archived` = changes con `archived == True`.

- **RB-UX03:** La notificación se emite siempre tras un refresh exitoso.
- **RB-UX04:** `action_toggle_archived` NO emite notify — el cambio de label ya comunica el estado.

### View 2 — Notify al abrir documento

`ChangeDetailScreen._open_doc(filename, label)` emite `self.notify(f"Opening {label}")` si el archivo existe antes de hacer `push_screen`.

- Aplica a: `p` (proposal), `d` (design), `t` (tasks), `q` (requirements).
- `action_view_spec` (single domain) también emite `self.notify("Opening spec")`.
- Si el archivo **no existe**: no se emite notify en `ChangeDetailScreen` (el warning lo emite `DocumentViewerScreen`).

- **RB-UX05:** El label en el notify es el nombre semántico corto ("proposal", "design", "tasks", "requirements", "spec"), no la ruta ni el filename.
- **RB-UX06:** Notify solo si `path.exists()` — sin notify para documentos ausentes desde View 2.

### DocumentViewerScreen — Warning archivo no encontrado

Cuando el archivo solicitado no existe, `DocumentViewerScreen.on_mount` emite:

```python
self.app.notify(f"{self._path.name} not found", severity="warning")
```

Además del mensaje `[dim]{filename} not found[/dim]` ya existente en el cuerpo.

- **RB-UX07:** El warning es adicional al mensaje en el cuerpo — ambos se muestran simultáneamente.
- **RB-UX08:** `severity="warning"` para distinguirlo de notificaciones informativas.

### SpecSelectorScreen — Binding `q`

`SpecSelectorScreen.BINDINGS` incluye `Binding("q", "app.pop_screen", "Close")` además del `Escape` existente.

- **RB-UX09:** `q` y `Esc` son equivalentes en `SpecSelectorScreen` — ambos hacen `pop_screen`.
- **RB-UX10:** Consistente con la expectativa del usuario de que `q` cierra pantallas modales/selectores.

---

## 14. UX Navigation — Scroll, Drill-down y Paths

### Bindings `j/k` en viewers de texto

`DocumentViewerScreen`, `SpecEvolutionScreen` y `DecisionsTimeline` exponen `j` y `k` para scroll.

- **REQ-01** `[Event]` When el usuario pulsa `j`, la pantalla SHALL hacer scroll hacia abajo.
- **REQ-02** `[Event]` When el usuario pulsa `k`, la pantalla SHALL hacer scroll hacia arriba.
- **REQ-03** `[Ubiquitous]` The bindings `j/k` SHALL estar disponibles en todas las pantallas de solo lectura.

Implementación: cada Screen define `action_scroll_down` y `action_scroll_up` que delegan a `self.query_one(ScrollableContainer).scroll_down/up()`. Las acciones nativas de `ScrollableContainer` no se propagan automáticamente al Screen.

- **RB-NAV01:** `scroll_down`/`scroll_up` definidos explícitamente en cada Screen viewer — no heredados del Screen base.

### Drill-down desde SpecHealthScreen

- **REQ-04** `[Event]` When el usuario pulsa Enter sobre una fila de change en `SpecHealthScreen`, la app SHALL hacer `push_screen(ChangeDetailScreen(change))`.
- **REQ-05** `[Unwanted]` If la fila seleccionada no tiene key (separador), Enter SHALL no hacer nada.
- **REQ-06** `[Event]` When `ChangeDetailScreen` se abre desde `SpecHealthScreen`, `Esc` SHALL volver a `SpecHealthScreen`.

`SpecHealthScreen` mantiene un `_change_map: dict[str, Change]` poblado durante `_populate()`. El handler `on_data_table_row_selected` hace lookup por `row_key.value`.

- **RB-NAV02:** Stack de navegación de 3 niveles: View1 → SpecHealthScreen → ChangeDetailScreen. Patrón consistente con el resto de la app.
- **RB-NAV03:** El separador `── archived ──` no tiene key → `_change_map.get()` devuelve `None` → no navega.

### Propiedad pública `SddTuiApp.changes`

- **REQ-07** `[Ubiquitous]` The `SddTuiApp` SHALL exponer los changes como `@property changes` (sin prefijo `_`).

La lista de changes vive en `EpicsView._changes`. La propiedad delega: `return self.query_one(EpicsView)._changes`.

### Paths centralizados

- **REQ-08** `[Ubiquitous]` The paths de `openspec/` SHALL calcularse desde `self.app._openspec_path`, no desde `Path.cwd() / "openspec"`.

Afecta: `EpicsView.action_steering`, `EpicsView.action_decisions_timeline`, `SpecEvolutionScreen._render_domain`.

- **RB-NAV04:** `EpicsView` elimina el import de `Path` (queda sin uso tras el fix).


---

## 15. Help Screen — Referencia de Keybindings

### Binding global `?`

- **REQ-01** `[Event]` When el usuario pulsa `?` en cualquier pantalla, la app SHALL hacer `push_screen(HelpScreen)`.
- **REQ-02** `[Ubiquitous]` The binding `?` SHALL estar disponible en todas las pantallas con `priority=True`.
- **REQ-03** `[Event]` When el usuario pulsa `Esc` en `HelpScreen`, la app SHALL hacer `pop_screen`.
- **REQ-04** `[Ubiquitous]` The `HelpScreen` SHALL mostrar todos los keybindings agrupados en 6 secciones: View 1, View 2, View 8, View 9, Viewers, Global.
- **REQ-06** `[State]` While el contenido supera la altura de pantalla, el usuario SHALL poder hacer scroll con `j`/`k`.

### Implementación

- `HelpScreen` en `tui/help.py` — contenido `HELP_CONTENT` como `rich.Text` constante generada por `_build_help_content()`.
- Binding en `SddTuiApp.BINDINGS` + `action_help` con import local de `HelpScreen`.
- Patrón `action_scroll_down/up` → `ScrollableContainer` (igual que viewers).

- **RB-HELP01:** Contenido estático — no generado dinámicamente desde BINDINGS de Textual.
- **RB-HELP02:** `priority=True` en `?` — capturado antes que cualquier Screen o Widget hijo.
- **RB-HELP03:** Import local en `action_help` — evita importaciones circulares.

---

## 16. View 1 — Search & Filter (binding `/`)

### Activación del modo búsqueda

- **REQ-01** `[Event]` When el usuario pulsa `/` en View 1, the app SHALL activar el modo búsqueda mostrando un `Input` en el pie de pantalla.
- **REQ-02** `[State]` While el modo búsqueda está activo, the `Input` SHALL recibir las teclas del teclado y filtrar el `DataTable` en tiempo real.
- **REQ-03** `[Event]` When el usuario escribe en el input, the `DataTable` SHALL actualizar sus filas mostrando solo los changes cuyo nombre contiene el texto (substring case-insensitive).
- **REQ-04** `[Event]` When el usuario pulsa `Esc` con modo búsqueda activo, the app SHALL desactivar el modo, limpiar el filtro y restaurar la lista completa.
- **REQ-05** `[Event]` When el usuario pulsa `Enter` con modo búsqueda activo, the app SHALL desactivar el modo, mantener el filtro y devolver el foco al `DataTable` con el cursor en el primer resultado.
- **REQ-06** `[Unwanted]` If el filtro produce 0 resultados, the `DataTable` SHALL mostrar una fila `No matches for "{query}"` sin key.
- **REQ-07** `[State]` While el filtro está confirmado, the `app.sub_title` SHALL mostrar `filtered: "{query}"`.
- **REQ-08** `[Event]` When el usuario pulsa `r` (refresh) con filtro activo, the app SHALL limpiar el filtro antes de recargar.
- **REQ-09** `[State]` While el filtro está activo y el usuario pulsa `a` (toggle archivados), the filtro SHALL persistir aplicándose al nuevo scope.
- **REQ-10** `[Ubiquitous]` The filtrado SHALL respetar `_show_archived`: los archivados solo aparecen en resultados si el toggle está activo.
- **REQ-11** `[Ubiquitous]` The separador `── archived ──` SHALL mantenerse si hay archivados en los resultados filtrados.
- **REQ-12** `[Event]` When el `DataTable` muestra resultados filtrados, the nombre del change SHALL mostrar el substring coincidente en `bold cyan`.

### Layout del Input

El widget `Input` (id=`search-input`) está compuesto entre el `DataTable` y el `Footer`. Por defecto `display: none`; se muestra al activar modo búsqueda.

### Implementación

- `EpicsView._search_mode: bool` — estado del modo búsqueda
- `EpicsView._search_query: str` — query actual (vacío = sin filtro)
- `_filter_changes(changes, query) → list[Change]` — substring case-insensitive
- `_highlight_match(name, query) → rich.Text` — bold cyan en el match
- `_populate()` lee `_search_query` — el filtro persiste automáticamente en `update()`
- `on_key` intercepta Escape con `event.stop()` para evitar propagación a la pila de pantallas
- `app.sub_title` indica filtro activo cuando está confirmado

### Reglas de negocio

- **RB-SEARCH01:** `Input.value = text` + `pilot.pause()` es el patrón correcto para tests en Textual 8.x (`pilot.type()` no existe).
- **RB-SEARCH02:** `on_key` con guard `if self._search_mode` — Esc solo interceptado en modo búsqueda.
- **RB-SEARCH03:** `_populate()` siempre lee `self._search_query` — no hay parámetro externo; el filtro es transparente para `update()`.
- **RB-SEARCH04:** Highlight usa `rich.Text` con `_spans`; `DataTable` acepta `Text` como valor de celda nativo.

---

## 17. Startup — Dependency Check

### Flujo de startup

- **REQ-01** `[Event]` When the app mounts, the system SHALL call `check_deps()` before the main view is usable.
- **REQ-02** `[Event]` When required deps are missing, the app SHALL push `ErrorScreen` with the list of missing deps.
- **REQ-03** `[Unwanted]` If `ErrorScreen` is displayed, the main view SHALL NOT be interactable.
- **REQ-04** `[Event]` When optional deps are missing, the app SHALL emit one `notify()` per dep with `severity="warning"` and `timeout=15`.
- **REQ-05** `[Event]` When all deps are present, the app SHALL mount normally without any notification.

### `ErrorScreen`

- Layout: `Header` + `ScrollableContainer(Static(...))` + `Footer`
- Título: `"sdd-tui — dependency error"`
- Muestra un bloque por dep: nombre, instrucciones por plataforma, `docs_url`
- Binding `q` → `self.app.exit()`
- Sin binding `Esc` — no hay pantalla previa válida

### Notify toast — optional missing

Formato: `"{name} not found — {feature} disabled  |  Install: {hint}  |  {docs_url}"`
Plataforma detectada con `sys.platform`: `darwin` → key `"macOS"`, `linux` → key `"Ubuntu"`.

### Reglas de negocio

- **RB-SD1:** `on_mount` usa imports locales para `check_deps` y `ErrorScreen` — patrón establecido en `app.py`.
- **RB-SD2:** `Esc` NO tiene binding en `ErrorScreen` — Textual haría `pop_screen` por defecto, lo cual es incorrecto sin pantalla previa.
- **RB-SD3:** Los warnings de optional deps se emiten solo una vez por sesión (en `on_mount`), no en refresh ni navegación.

---

## 18. Observatory v1 — Multi-project Support

### View 1 — Separadores de proyecto

- **REQ-01** `[Optional]` Where multi-project config is active, `EpicsView` SHALL show changes grouped by project with a separator row per project.
- **REQ-02** `[Ubiquitous]` The system SHALL NOT show project separators in single-project (legacy) mode.
- **REQ-03** `[Event]` When the user presses `Enter` on any change (from any project), the app SHALL push `ChangeDetailScreen`.
- **REQ-04** `[Event]` When the user presses `r`, the app SHALL reload all projects defined in config.
- **REQ-05** `[Unwanted]` If a project becomes unavailable after startup, the system SHALL skip it silently during reload.

Multi-proyecto detectado cuando `len(active_projects) > 1` donde `active_projects = list(dict.fromkeys(c.project for c in active))`. En single-project no se renderizan separadores.

### SpecHealthScreen — Multi-proyecto

- **REQ-06** `[Optional]` Where multi-project config is active, `SpecHealthScreen` SHALL show changes from all projects, grouped with separator rows.
- **REQ-07** `[Ubiquitous]` In single-project mode, `SpecHealthScreen` behavior SHALL be identical to the current spec.

`parse_metrics(change_path, change.project_path)` — usa `change.project_path` en lugar de `Path.cwd()`.

### DecisionsTimeline — Multi-proyecto

- **REQ-08** `[Optional]` Where multi-project config is active, `DecisionsTimeline` SHALL aggregate decisions from `archive/` of all configured projects.
- **REQ-09** `[Ubiquitous]` Decisions SHALL be ordered chronologically (ascending) across all projects combined.

`DecisionsTimeline.__init__(archive_dirs: list[Path])` — recibe lista de dirs; en single-project, lista de un elemento.

### Reglas de negocio

- **RB-MP01:** Los separadores de proyecto son filas sin key — Enter no navega.
- **RB-MP02:** `is_multi = len(active_projects) > 1` — derivado de los changes presentes, no del config.
- **RB-MP03:** El nombre en el separador = `change.project` (basename del proyecto).
- **RB-MP04:** `SddTuiApp.__init__` acepta `config: AppConfig | None = None` — retrocompatible.
- **RB-MP05:** `action_decisions_timeline` construye `archive_dirs` desde `change.project_path` de los changes cargados.

### Fuera de scope

- Binding `s` (steering) sigue usando `_openspec_path` single-project — extensión diferida a v2.
