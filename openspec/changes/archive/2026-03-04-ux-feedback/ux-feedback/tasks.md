# Tasks: UX Feedback — Estado Visual y Notificaciones

## Metadata
- **Change:** ux-feedback
- **Jira:** N/A
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-04

## Tareas de Implementación

- [x] **T01** Modificar `src/sdd_tui/tui/epics.py` — label dinámico en binding `a` + notify en refresh
  - Fix 1: `action_toggle_archived` asigna `self.BINDINGS` con label dinámico y llama `refresh_bindings()`
  - Fix 2: `action_refresh` cuenta activos/archivados y emite `self.notify(...)`
  - Commit: `[ux-feedback] Dynamic archived label and refresh notify in EpicsView`

- [x] **T02** Modificar `src/sdd_tui/tui/change_detail.py` — notify al abrir documento existente
  - Fix 3: `_open_doc` llama `self.notify(f"Opening {label}")` si el archivo existe
  - Fix 3b: `action_view_spec` (single domain path) también notifica
  - Commit: `[ux-feedback] Notify on document open in ChangeDetailScreen`

- [x] **T03** Modificar `src/sdd_tui/tui/doc_viewer.py` — warning not found + binding q en selector
  - Fix 4: `DocumentViewerScreen.on_mount` llama `self.app.notify(..., severity="warning")` si el path no existe
  - Fix 5: `SpecSelectorScreen.BINDINGS` añade `Binding("q", "app.pop_screen", "Close")`
  - Commit: `[ux-feedback] Warning notify on missing file and q binding in SpecSelectorScreen`

- [x] **T04** Modificar `tests/test_tui_epics.py` — tests label dinámico y notify refresh
  - `test_toggle_archived_label_changes`: tras `a`, BINDINGS instancia contiene "Hide archived"
  - `test_toggle_archived_label_reverts`: tras dos `a`, BINDINGS instancia contiene "Show archived"
  - `test_refresh_emits_notify`: tras `r`, la notificación contiene el conteo de changes
  - Commit: `[ux-feedback] Tests for dynamic archived label and refresh notify`

- [x] **T05** Modificar `tests/test_tui_change_detail.py` — tests notify al abrir doc
  - `test_open_existing_doc_notifies`: `_open_doc` con archivo existente emite notify "Opening proposal"
  - `test_open_missing_doc_no_notify_in_detail`: `_open_doc` sin archivo no emite notify en ChangeDetailScreen
  - Commit: `[ux-feedback] Tests for document open notify in ChangeDetailScreen`

- [x] **T06** Modificar `tests/test_tui_doc_viewer.py` — tests warning y q binding
  - `test_doc_viewer_missing_emits_warning`: `on_mount` con path inexistente emite notify con severity warning
  - `test_spec_selector_q_closes`: `q` en SpecSelectorScreen cierra la pantalla (vuelve a ChangeDetailScreen)
  - Commit: `[ux-feedback] Tests for missing file warning and q binding in SpecSelectorScreen`

## Quality Gate Final

- [x] **QG** Ejecutar tests completos
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest tests/ -v`

## Notas

- T01 y T02 son independientes — pueden hacerse en cualquier orden
- T03 depende conceptualmente de T01/T02 (mismo patrón) pero no técnicamente
- T04/T05/T06 van siempre después de la tarea de implementación correspondiente
- Orden TDD: implementar primero (T01-T03), luego tests (T04-T06)
- `refresh_bindings()` en Textual requiere que `self.BINDINGS` sea un atributo de instancia
  (sobrescribir en el propio método es válido — Python resuelve instancia antes que clase)
- El notify de refresh usa `self.notify()` (en Widget), no `self.app.notify()`
- En tests de notify: usar `app.screen_stack[-1]._notifications` o verificar vía `pilot` con
  `app.query_one(Toast)` — ver patrón en tests existentes si hay alguno; si no, verificar
  el comportamiento indirectamente (ej. que no lanza excepción + navegación correcta)
