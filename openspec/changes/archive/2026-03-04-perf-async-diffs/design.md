# Design: Async Diff Loading con run_worker

## Metadata
- **Change:** perf-async-diffs
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

Refactorizar `on_data_table_row_highlighted` en `ChangeDetailScreen` para que la
carga del diff ocurra en un hilo separado via el decorator `@work(thread=True, exclusive=True)`
de Textual, en lugar de bloquear el event loop con `subprocess.run`.

El handler síncrono queda reducido a dos operaciones: mostrar el placeholder
`"[dim]Loading diff…[/dim]"` y llamar al método worker. El worker corre en un
hilo, ejecuta git, y usa `call_from_thread` para actualizar el `DiffPanel`
cuando termina. `exclusive=True` cancela automáticamente cualquier worker previo
si el usuario navega antes de que el anterior complete.

## Arquitectura

```
on_data_table_row_highlighted (sync, event loop)
  │
  ├─► diff_panel.show_message("[dim]Loading diff…[/dim]")   ← inmediato
  │
  └─► _load_diff_worker(task_id)    ← @work(thread=True, exclusive=True)
        │  [hilo separado — git subprocess bloqueante]
        │
        ├─► GitReader().get_diff(hash, cwd)
        │   o GitReader().get_working_diff(cwd)
        │
        └─► call_from_thread(_update_diff_panel, content)
              │  [de vuelta al event loop]
              └─► diff_panel.show_diff(content)
                  o diff_panel.show_message(msg)
```

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | Refactorizar `on_data_table_row_highlighted` + añadir `_load_diff_worker` + `_update_diff_panel` | Núcleo del change |
| `tests/test_tui_change_detail.py` | Añadir tests para comportamiento async | Cobertura del nuevo flujo |

## Scope

- **Total archivos:** 2
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Textual `@work` decorator — disponible desde Textual 0.27+; ya es dependencia del proyecto.
- `call_from_thread` — API pública de Textual para actualizar UI desde hilos worker.
- Sin nuevas dependencias.

## Patrones Aplicados

- **`@work(thread=True, exclusive=True)`**: decorator de Textual para workers en hilo. `thread=True`
  indica que el método es síncrono (corre en `ThreadPoolExecutor`). `exclusive=True` cancela el
  worker anterior del mismo nombre antes de lanzar uno nuevo.
- **`call_from_thread`**: único mecanismo seguro para modificar widgets desde un hilo worker en Textual.
  Acceder a widgets directamente desde el hilo causaría race conditions.

## Implementación Detallada

### `on_data_table_row_highlighted` (después)

```python
def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    if event.row_key is None or event.row_key.value is None:
        return
    task = self.query_one(TaskListPanel).get_task(event.row_key.value)
    if task is None:
        return
    try:
        diff_panel = self.query_one(DiffPanel)
    except Exception:
        return
    diff_panel.show_message("[dim]Loading diff…[/dim]")
    self._load_diff_worker(event.row_key.value)
```

### `_load_diff_worker` (nuevo)

```python
@work(thread=True, exclusive=True)
def _load_diff_worker(self, task_id: str) -> None:
    task = self.query_one(TaskListPanel).get_task(task_id)
    if task is None:
        return
    if task.git_state == TaskGitState.COMMITTED and task.commit:
        diff = GitReader().get_diff(task.commit.hash, Path.cwd())
        if diff:
            content: RenderableType = Syntax(diff, "diff", theme="monokai", word_wrap=False)
        else:
            content = "Could not load diff"
    else:
        diff = GitReader().get_working_diff(Path.cwd())
        if diff:
            content = Syntax(diff, "diff", theme="monokai", word_wrap=False)
        else:
            content = "No uncommitted changes"
    self.call_from_thread(self._update_diff_panel, content)
```

### `_update_diff_panel` (nuevo)

```python
def _update_diff_panel(self, content: RenderableType | str) -> None:
    try:
        diff_panel = self.query_one(DiffPanel)
    except Exception:
        return
    if isinstance(content, str):
        diff_panel.show_message(content)
    else:
        diff_panel.show_diff_renderable(content)
```

> **Nota:** `DiffPanel` necesita un método `show_diff_renderable` que acepta un
> `Syntax` ya construido (para no re-construirlo en el hilo principal).
> Alternativa: pasar el texto raw + flag, construir `Syntax` en `_update_diff_panel`.
> **Decisión:** pasar el texto raw y construir `Syntax` en el hilo principal para
> mantener `DiffPanel.show_diff` con la misma firma. Ver decisiones de diseño.

### Revisión: interfaz final decidida

Para evitar añadir método nuevo a `DiffPanel` y mantener la firma pública:

```python
# En _load_diff_worker — construye el Syntax en el HILO (ok, rich.Syntax es thread-safe):
content = Syntax(diff, "diff", theme="monokai", word_wrap=False)
self.call_from_thread(self._update_diff_panel, content, True)  # True = is_syntax

# En _update_diff_panel:
def _update_diff_panel(self, content, is_syntax: bool = False) -> None:
    diff_panel = self.query_one(DiffPanel)
    if is_syntax:
        diff_panel.query_one("#diff-content", Static).update(content)
        diff_panel.scroll_home(animate=False)
    else:
        diff_panel.show_message(content)
```

**Decisión final:** mantener la construcción del `Syntax` en el worker (hilo),
ya que `rich.Syntax` es seguro para construir fuera del event loop, y así
`call_from_thread` solo pasa el objeto ya listo. `_update_diff_panel` actualiza
el widget directamente (sin depender de métodos de `DiffPanel`).

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `@work(thread=True)` vs `run_worker(coro)` | `run_worker` con coroutine + `run_in_executor` | `@work` es más idiomático en Textual; menos boilerplate; el método queda auto-documentado |
| `exclusive=True` en `@work` | Cancelación manual | Textual lo gestiona automáticamente — sin código extra |
| Construir `Syntax` en el hilo worker | Construir en `_update_diff_panel` (event loop) | `rich.Syntax` es thread-safe; reduce trabajo en el event loop; consistente con el objetivo del change |
| `call_from_thread` para actualizar DiffPanel | Post mensaje/evento a la app | `call_from_thread` es la API oficial de Textual para este patrón |
| No añadir método nuevo a `DiffPanel` | `show_diff_renderable(Syntax)` | Menor superficie de API; `_update_diff_panel` actualiza el Static directamente |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_diff_panel_shows_loading_placeholder` | Unit (async) | `show_message("Loading diff…")` se llama antes del worker |
| `test_diff_loads_after_worker_completes` | Integration (pilot) | Después de `row_highlighted` + espera, el DiffPanel tiene contenido real |
| `test_rapid_navigation_shows_last_diff` | Integration (pilot) | Navegación rápida muestra solo el diff de la última tarea seleccionada |

> **Nota sobre testeo de workers:** Los tests de Textual con `run_test()` y `pilot`
> procesan el event loop; los workers thread-based requieren `await pilot.pause()`
> o `await asyncio.sleep(0.1)` para dejar que el hilo complete antes de assertar.
> Alternativamente, mockear `_load_diff_worker` para testear el comportamiento
> del placeholder y el worker por separado.

## Notas de Implementación

- Añadir `from textual import work` al import block de `change_detail.py`
- `RenderableType` viene de `rich.console` — añadir al import si se usa como type hint
- El worker accede a `self.query_one(TaskListPanel)` desde el hilo — esto es técnicamente
  un acceso al widget desde fuera del event loop. **Alternativa más segura:** pasar el
  objeto `Task` directamente al worker en lugar del `task_id`, capturándolo en el handler
  síncrono (que sí está en el event loop). Esta es la implementación recomendada.

### Implementación más segura (recomendada):

```python
def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    ...
    task = self.query_one(TaskListPanel).get_task(event.row_key.value)
    if task is None:
        return
    diff_panel.show_message("[dim]Loading diff…[/dim]")
    self._load_diff_worker(task)   # pasar Task, no task_id

@work(thread=True, exclusive=True)
def _load_diff_worker(self, task: Task) -> None:
    # No accede a widgets — solo usa el objeto Task ya capturado
    ...
    self.call_from_thread(self._update_diff_panel, content)
```

Esto elimina el acceso a `query_one` desde el hilo — más limpio y thread-safe.
