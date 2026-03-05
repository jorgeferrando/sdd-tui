# Proposal: Perf — Async Diff Loading

## Metadata
- **Change:** perf-async-diffs
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

La carga de diffs en View 2 bloquea el event loop de Textual.

### Detalle técnico

`ChangeDetailScreen.on_data_table_row_highlighted` es el handler que se dispara
cada vez que el cursor se mueve en la lista de tasks. Dentro de este handler
se llama directamente a `get_diff()` o `get_working_diff()` de `git_reader.py`,
que ejecutan `subprocess.run(..., capture_output=True)` de forma síncrona.

`subprocess.run` es bloqueante: mientras git ejecuta, el event loop de Textual
no puede procesar ningún otro evento (input de teclado, redibujado, animaciones).

En repos con historial largo o diffs grandes esto produce un freeze perceptible
al navegar por las tasks con las flechas. El usuario ve la TUI congelada durante
la carga.

### Magnitud del problema

- Diffs pequeños (< 100 líneas): imperceptible (~10ms)
- Diffs medianos (100-500 líneas): perceptible (~50-150ms)
- Diffs grandes (> 500 líneas, binarios, renombrados): freeze notable (> 200ms)

Para el caso de uso habitual de sdd-tui (changes con tasks de 1-3 archivos),
el impacto es bajo-medio. Sin embargo, el patrón bloqueante es técnicamente
incorrecto para una TUI reactiva y empeorará a medida que el proyecto crezca.

## Solución Propuesta

Mover la carga del diff a un worker de Textual usando `self.run_worker`.

### Flujo propuesto

1. Al recibir `RowHighlighted`, mostrar inmediatamente `"[dim]Loading diff…[/dim]"`
   en el `DiffPanel` (feedback instantáneo al usuario)
2. Lanzar `self.run_worker(self._load_diff_worker(task_id), exclusive=True)`
3. En el worker (hilo separado), ejecutar `get_diff()` o `get_working_diff()`
4. Actualizar el `DiffPanel` con el resultado via `self.call_from_thread`

El flag `exclusive=True` cancela automáticamente cualquier worker previo si el
usuario navega rápido — evita que diffs de tasks anteriores sobreescriban
el resultado de la task actual.

### Indicador de carga

Mientras el worker corre, el DiffPanel muestra `"[dim]Loading diff…[/dim]"`.
Este texto reemplaza el anterior contenido inmediatamente, dando feedback visual
de que algo está ocurriendo.

No se añade un spinner o ProgressBar — el mensaje de texto es suficiente para
diffs que tardan < 500ms, que es el caso esperado.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| `asyncio.create_task` con `subprocess` async | Nativo de Python | `subprocess` async requiere `asyncio.create_subprocess_exec`, más verboso | Descartada |
| Cache de diffs en memoria (dict hash→diff) | Evita re-ejecutar git | Invalida en cada refresh; complejidad de cache invalidation | Descartada por ahora |
| **`run_worker` de Textual con `exclusive=True`** | Patrón idiomático de Textual; cancela automáticamente workers previos | Requiere `call_from_thread` para actualizar UI | **Elegida** |
| Mantener síncrono con debounce (100ms delay antes de cargar) | Reduce git calls en navegación rápida | El freeze sigue existiendo; debounce añade latencia percibida | Descartada |

## Impacto Estimado

- **Dominio:** tui (UI layer) + core/git_reader
- **Archivos modificados:**
  - `tui/change_detail.py` — refactorizar `on_data_table_row_highlighted` + `_load_diff_worker`
- **Breaking changes:** Ninguno (comportamiento idéntico, ejecución asíncrona)
- **Tests afectados:** Tests del handler necesitarán mockear el worker o testear el método `_load_diff_worker` directamente

## Criterios de Éxito

- [ ] Navegar por tasks en View 2 no congela la TUI en ningún caso
- [ ] El DiffPanel muestra `"Loading diff…"` mientras el diff se carga
- [ ] Navegar rápidamente (múltiples flechas) solo carga el diff de la task final (exclusive=True funciona)
- [ ] El comportamiento del diff es idéntico al actual (mismo contenido, mismos colores)

## Preguntas Abiertas

- [ ] ¿Añadir cache de diffs en memoria en una segunda iteración? Reduciría git calls al re-visitar tasks.
- [ ] ¿El indicador `"Loading diff…"` debería tener un timeout visible si git tarda más de 2s?
