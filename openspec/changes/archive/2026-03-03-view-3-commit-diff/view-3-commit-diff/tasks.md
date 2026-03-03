# Tasks: View 3 — Commit diff inline

## Metadata
- **Change:** view-3-commit-diff
- **Jira:** N/A
- **Rama:** main
- **Fecha:** 2026-03-03

## Tareas de Implementación

- [x] **T01** Modificar `tests/test_git_reader.py` — añadir tests para `get_diff()` (RED)
  - Commit: `[view-3] Add tests for GitReader.get_diff`

- [x] **T02** Modificar `src/sdd_tui/core/git_reader.py` — añadir `get_diff()` (GREEN)
  - Commit: `[view-3] Add GitReader.get_diff`
  - Depende de: T01

- [x] **T03** Modificar `src/sdd_tui/tui/change_detail.py` — TaskListPanel → DataTable, añadir DiffPanel, event handler en ChangeDetailScreen
  - Commit: `[view-3] Add interactive task list with commit diff panel`
  - Depende de: T02

## Bugs post-T03

- [x] **BUG01** `src/sdd_tui/core/git_reader.py` — `find_commit` usa regex por defecto; `[view-3]` se interpreta como clase de caracteres, nunca encuentra los commits
  - Detectado: todas las tareas mostraban el mismo diff (todas quedaban PENDING)
  - Fix: añadir flag `-F` (fixed-strings) al `git log --grep`
  - Commit: `[view-3] Fix find_commit using fixed-string grep`

## Mejoras post-T03

- [x] **MEJ01** `src/sdd_tui/tui/change_detail.py` — panel de tareas tenía demasiado espacio vacío abajo; panel diff demasiado pequeño
  - Fix: `TaskListPanel { height: auto; max-height: 40% }`, `DiffPanel { height: 1fr }`
  - Commit: `[view-3] Auto-size task panel and expand diff panel`

- [x] **MEJ02** `src/sdd_tui/tui/change_detail.py` — diff se mostraba como texto plano sin coloreado
  - Fix: `Rich.Syntax` con lexer `"diff"` y tema `"monokai"`
  - Commit: `[view-3] Add syntax highlighting to diff panel`

- [x] **MEJ03** `src/sdd_tui/core/git_reader.py` + `change_detail.py` — tareas PENDING mostraban "Not committed yet" sin información útil
  - Fix: añadir `get_working_diff()` y mostrar `git diff HEAD` para tareas pendientes
  - Commit: `[view-3] Show working tree diff for pending tasks`

- [x] **MEJ04** `src/sdd_tui/core/pipeline.py` + `tests/test_pipeline.py` — TaskParser ignora IDs `BUG01`/`MEJ01` (regex solo acepta `T\d+`)
  - Fix: cambiar `_TASK_RE` a `[A-Z]+\d+` para aceptar cualquier prefijo de letras mayúsculas
  - Commit: `[view-3] Extend TaskParser to recognize BUG and MEJ task IDs`

- [x] **BUG02** `src/sdd_tui/tui/change_detail.py` — `height: auto` en `TaskListPanel` colapsa el `DataTable` (ScrollView); filas BUG/MEJ existen en el modelo pero no son visibles
  - Fix: calcular altura en `on_mount` basándose en número de filas; máximo 40% de pantalla
  - Commit: `[view-3] Fix TaskListPanel height to fit row count`

- [x] **BUG03** `src/sdd_tui/tui/change_detail.py` — `RowHighlighted` se dispara durante `on_mount` de `TaskListPanel` antes de que `DiffPanel` esté montado; `query_one(DiffPanel)` falla silenciosamente
  - Detectado: tras el fix de BUG02 el DataTable emite eventos correctamente, pero DiffPanel aún no existe en el DOM en ese momento
  - Fix: usar `self.query(DiffPanel)` con guard `if not diff_panels: return` antes de acceder al panel
  - Commit: `[view-3] Fix RowHighlighted firing before DiffPanel is mounted`

- [x] **BUG04** `src/sdd_tui/tui/change_detail.py` — diff seguía sin mostrarse tras BUG03; tres causas combinadas
  - Causa A: `call_after_refresh` no forzaba focus en `DataTable` → flechas no disparaban `RowHighlighted`
  - Causa B: scroll de `DiffPanel` podía quedar en posición incorrecta tras carga de diff
  - Causa C: `DiffPanel` arrancaba vacío sin indicación visual
  - Fix: `call_after_refresh(DataTable.focus())` en `ChangeDetailScreen.on_mount`; `scroll_home(animate=False)` en `show_diff`/`show_message`; placeholder "Select a task to view its diff"
  - Commit: `[view-3] Fix DataTable focus and DiffPanel scroll after mount`

- [x] **BUG05** `src/sdd_tui/tui/change_detail.py` — `DiffPanel` tenía altura 0 porque `PipelinePanel { height: 1fr }` dentro de `.top-panel { height: auto }` crea dependencia circular; Textual resuelve expandiendo `.top-panel` a toda la pantalla
  - Detectado: screenshot muestra 5 tareas y espacio vacío sin `DiffPanel` ni border-top
  - Fix: cambiar `PipelinePanel { height: 1fr }` → `{ height: auto }` para que se ajuste al texto
  - Commit: `[view-3] Fix PipelinePanel height causing DiffPanel to collapse`

- [x] **BUG06** `src/sdd_tui/tui/change_detail.py` — `self.app.size.height` durante `on_mount` devuelve 0 (terminal no inicializado); lista capada a 6 filas en vez de adaptarse al tamaño real
  - Fix: mover cálculo de altura a `call_after_refresh` cuando el tamaño del terminal ya es correcto; aumentar límite a `screen_h - 10` (reserva mínima de 10 filas para diff + bordes + header/footer)
  - Commit: `[view-3] Fix task list height using call_after_refresh`

## Quality Gate Final

- [x] **QG** Ejecutar tests y smoke test de navegación
  - `uv run pytest`
  - `uv run sdd-tui` → Enter en un change → seleccionar tarea committed → ver diff → Esc

## Notas

- T01 y T02 siguen el patrón TDD ya establecido (test RED → implementación GREEN)
- T03 es el cambio más grande: reemplaza `TaskListPanel` completo y añade `DiffPanel`
- El `cwd` para `get_diff()` es `Path.cwd()` — coherente con `_load_tasks()` en `app.py`
- Verificar que los separadores de amendment (sin `key`) no bloqueen el `RowHighlighted`
