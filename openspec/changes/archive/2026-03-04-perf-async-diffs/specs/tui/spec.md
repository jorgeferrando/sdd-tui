# Spec: TUI — Async Diff Loading (perf-async-diffs)

## Metadata
- **Dominio:** tui
- **Change:** perf-async-diffs
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

La spec canónica (`openspec/specs/tui/spec.md §2 — DiffPanel`) define que el diff se carga
en `on_data_table_row_highlighted`. La carga actual es síncrona (`subprocess.run`),
bloqueando el event loop de Textual mientras git ejecuta.

Este delta cambia **cómo** se carga el diff — no **qué** se muestra.
El comportamiento visible final (contenido, colores) es idéntico.

## Comportamiento Actual

`ChangeDetailScreen.on_data_table_row_highlighted` llama directamente a
`git_reader.get_diff()` / `get_working_diff()`, que ejecutan `subprocess.run`
de forma síncrona. Esto bloquea el event loop mientras git responde.

## Requisitos (EARS)

- **REQ-01** `[Event]` When el cursor se mueve a una tarea en View 2, el DiffPanel SHALL mostrar `"[dim]Loading diff…[/dim]"` de forma inmediata (antes de que git responda).
- **REQ-02** `[Event]` When el worker de diff completa, el DiffPanel SHALL actualizarse con el contenido del diff (mismo formato y colores que el comportamiento actual).
- **REQ-03** `[State]` While el worker de diff está corriendo, el event loop de Textual SHALL permanecer desbloqueado (acepta input de teclado y redibuja normalmente).
- **REQ-04** `[Event]` When el usuario navega a una nueva tarea antes de que el worker anterior complete, el worker anterior SHALL cancelarse automáticamente.
- **REQ-05** `[Ubiquitous]` The DiffPanel SHALL mostrar únicamente el diff de la tarea actualmente seleccionada — nunca el de una tarea anterior que cargó más tarde.
- **REQ-06** `[Unwanted]` If `git show` o `git diff` falla dentro del worker, el DiffPanel SHALL mostrar `"Could not load diff"` (comportamiento idéntico al actual).
- **REQ-07** `[Ubiquitous]` The contenido final del diff (syntax highlighting con `rich.Syntax`, lexer=`diff`, tema=`monokai`) SHALL ser idéntico al comportamiento actual.

### Escenarios de verificación

**REQ-04 — Cancelación de worker previo (navegación rápida)**
**Dado** View 2 con varias tareas
**Cuando** el usuario pulsa ↓ rápidamente tres veces (T01 → T02 → T03)
**Entonces** solo se muestra el diff de T03; los diffs de T01 y T02 son cancelados antes de escribir al DiffPanel

**REQ-03 — UI no congela**
**Dado** View 2 con una tarea cuyo diff tarda > 200ms
**Cuando** el cursor se mueve a esa tarea
**Entonces** la TUI responde a input de teclado durante la carga (no hay freeze perceptible)

## Cambios a la Spec Canónica

### §2 DiffPanel — comportamiento de carga (REEMPLAZA RB-V3-01)

**Antes:**
> `RB-V3-01`: El diff panel se actualiza en `on_data_table_row_highlighted` (hover), no en `RowSelected` (Enter).

**Después:**
> `RB-V3-01`: El diff panel se actualiza en `on_data_table_row_highlighted` (hover), no en `RowSelected` (Enter).
> La carga se realiza en un worker asíncrono (`run_worker`, `exclusive=True`). El handler sincrónico
> solo muestra el placeholder `"Loading diff…"` y lanza el worker.

**Reglas nuevas:**

- **RB-ASYNC-01:** `on_data_table_row_highlighted` es síncrono: actualiza el DiffPanel con `"[dim]Loading diff…[/dim]"` y llama `self.run_worker(self._load_diff_worker(task_id), exclusive=True)`.
- **RB-ASYNC-02:** `exclusive=True` garantiza que solo hay un worker de diff activo a la vez. Textual cancela el anterior automáticamente al lanzar uno nuevo.
- **RB-ASYNC-03:** El worker actualiza el DiffPanel via `self.call_from_thread(...)` — no accede a widgets directamente desde el hilo del worker.
- **RB-ASYNC-04:** El contenido del diff (después de cargar) es idéntico al comportamiento actual: `rich.Syntax` con lexer=`diff` y tema=`monokai`.
- **RB-ASYNC-05:** Las filas de separador de amendment (sin key) no lanzan worker — comportamiento idéntico al actual.

## Interfaces / Contratos

### `ChangeDetailScreen._load_diff_worker(task_id: str) → None`

Método worker (ejecutado en hilo separado por Textual):
1. Busca la tarea por `task_id` en `self._change.tasks`
2. Llama a `get_diff(hash)` o `get_working_diff()` según el estado de la tarea
3. Construye el `rich.Syntax` o `str` de resultado
4. Llama `self.call_from_thread(self._update_diff_panel, content)` para actualizar la UI

### `ChangeDetailScreen._update_diff_panel(content) → None`

Método llamado desde el hilo del worker via `call_from_thread`:
- Actualiza el `Static` interior del `DiffPanel` con el nuevo contenido
- Llama `scroll_home()` en el `DiffPanel`

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `run_worker` de Textual con `exclusive=True` | `asyncio.create_task` con subprocess async | Patrón idiomático de Textual; cancela automáticamente workers previos |
| Placeholder `"Loading diff…"` en texto plano | Spinner / ProgressBar | Suficiente para diffs < 500ms; sin dependencias nuevas |
| Cache de diffs en memoria | Sin cache | Diferido a iteración futura — scope mínimo en este change |
| Debounce antes de lanzar worker | Sin debounce | Debounce añade latencia percibida; `exclusive=True` ya maneja la navegación rápida |

## Abierto / Pendiente

- [ ] Cache de diffs en memoria (dict hash→content) — reducción de git calls al re-visitar tareas. Diferido a change separado.
- [ ] Timeout visible si git tarda > 2s — diferido.
