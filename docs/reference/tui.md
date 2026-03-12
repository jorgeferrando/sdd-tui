# Tui Reference

The TUI domain contains all Textual screens and widgets that make up the sdd-tui interface. It is organized around a screen stack: `EpicsView` is the root screen listing all active changes, and from it you drill into `ChangeDetailScreen` (pipeline + diff), `SpecHealthScreen` (spec coverage at a glance), `SpecEvolutionScreen` (delta vs canonical specs), `DocumentViewerScreen` (prose files), and several auxiliary screens like `ProgressDashboard`, `SkillPaletteScreen`, `TodosScreen`, and `ReleasesScreen`. Navigation is entirely keyboard-driven — every screen advertises its bindings in the Footer, and `?` opens a global help overlay.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-NA-01` | Ubiquitous | The `PipelinePanel` SHALL display a `NEXT` line when `name` is non-empty. |
| `REQ-NA-02` | Ubiquitous | The `NEXT` line SHALL use `next_command(pipeline, tasks, name)` for resolution. |
| `REQ-NA-03` | Ubiquitous | The `NEXT` line SHALL be positioned after the CI line, separated by a blank line. |
| `REQ-NA-04` | Ubiquitous | The `NEXT` line format SHALL be `  NEXT  {command}`. |
| `REQ-NA-08` | Unwanted | The `NEXT` line SHALL NOT update when PR or CI status loads — it only depends on pipeline state and tasks. |
| `REQ-SH-01` | Event | When `SpecHealthScreen` renders a change row, the system SHALL call `repair_hints(metrics, change)` and display the first element in the `HINT` column. |
| `REQ-SH-02` | Ubiquitous | The `HINT` column SHALL be the last column in the table. |
| `REQ-SH-03` | Ubiquitous | Separator rows SHALL display an empty string in the `HINT` column. |
| `REQ-SH-04` | Ubiquitous | The hint `✓` SHALL be rendered in `green`; pipeline hints SHALL be `cyan`; quality hints SHALL be `yellow`. |
| `REQ-01` | Event | When el usuario pulsa `j`, la pantalla SHALL hacer scroll hacia abajo. |
| `REQ-02` | Event | When el usuario pulsa `k`, la pantalla SHALL hacer scroll hacia arriba. |
| `REQ-03` | Ubiquitous | The bindings `j/k` SHALL estar disponibles en todas las pantallas de solo lectura. |
| `REQ-04` | Event | When el usuario pulsa Enter sobre una fila de change en `SpecHealthScreen`, la app SHALL hacer `push_screen(ChangeDetailScreen(change))`. |
| `REQ-05` | Unwanted | If la fila seleccionada no tiene key (separador), Enter SHALL no hacer nada. |
| `REQ-06` | Event | When `ChangeDetailScreen` se abre desde `SpecHealthScreen`, `Esc` SHALL volver a `SpecHealthScreen`. |
| `REQ-07` | Ubiquitous | The `SddTuiApp` SHALL exponer los changes como `@property changes` (sin prefijo `_`). |
| `REQ-08` | Ubiquitous | The paths de `openspec/` SHALL calcularse desde `self.app._openspec_path`, no desde `Path.cwd() / "openspec"`. |
| `REQ-01` | Event | When el usuario pulsa `?` en cualquier pantalla, la app SHALL hacer `push_screen(HelpScreen)`. |
| `REQ-02` | Ubiquitous | The binding `?` SHALL estar disponible en todas las pantallas con `priority=True`. |
| `REQ-03` | Event | When el usuario pulsa `Esc` en `HelpScreen`, la app SHALL hacer `pop_screen`. |
| `REQ-04` | Ubiquitous | The `HelpScreen` SHALL mostrar todos los keybindings agrupados en 6 secciones: View 1, View 2, View 8, View 9, Viewers, Global. |
| `REQ-06` | State | While el contenido supera la altura de pantalla, el usuario SHALL poder hacer scroll con `j`/`k`. |
| `REQ-01` | Event | When el usuario pulsa `/` en View 1, the app SHALL activar el modo búsqueda mostrando un `Input` en el pie de pantalla. |
| `REQ-02` | State | While el modo búsqueda está activo, the `Input` SHALL recibir las teclas del teclado y filtrar el `DataTable` en tiempo real. |
| `REQ-03` | Event | When el usuario escribe en el input, the `DataTable` SHALL actualizar sus filas mostrando solo los changes cuyo nombre contiene el texto (substring case-insensitive). |
| `REQ-04` | Event | When el usuario pulsa `Esc` con modo búsqueda activo, the app SHALL desactivar el modo, limpiar el filtro y restaurar la lista completa. |
| `REQ-05` | Event | When el usuario pulsa `Enter` con modo búsqueda activo, the app SHALL desactivar el modo, mantener el filtro y devolver el foco al `DataTable` con el cursor en el primer resultado. |
| `REQ-06` | Unwanted | If el filtro produce 0 resultados, the `DataTable` SHALL mostrar una fila `No matches for "{query}"` sin key. |
| `REQ-07` | State | While el filtro está confirmado, the `app.sub_title` SHALL mostrar `filtered: "{query}"`. |
| `REQ-08` | Event | When el usuario pulsa `r` (refresh) con filtro activo, the app SHALL limpiar el filtro antes de recargar. |
| `REQ-09` | State | While el filtro está activo y el usuario pulsa `a` (toggle archivados), the filtro SHALL persistir aplicándose al nuevo scope. |
| `REQ-10` | Ubiquitous | The filtrado SHALL respetar `_show_archived`: los archivados solo aparecen en resultados si el toggle está activo. |
| `REQ-11` | Ubiquitous | The separador `── archived ──` SHALL mantenerse si hay archivados en los resultados filtrados. |
| `REQ-12` | Event | When el `DataTable` muestra resultados filtrados, the nombre del change SHALL mostrar el substring coincidente en `bold cyan`. |
| `REQ-01` | Event | When the app mounts, the system SHALL call `check_deps()` before the main view is usable. |
| `REQ-02` | Event | When required deps are missing, the app SHALL push `ErrorScreen` with the list of missing deps. |
| `REQ-03` | Unwanted | If `ErrorScreen` is displayed, the main view SHALL NOT be interactable. |
| `REQ-04` | Event | When optional deps are missing, the app SHALL emit one `notify()` per dep with `severity="warning"` and `timeout=15`. |
| `REQ-05` | Event | When all deps are present, the app SHALL mount normally without any notification. |
| `REQ-01` | Optional | Where multi-project config is active, `EpicsView` SHALL show changes grouped by project with a separator row per project. |
| `REQ-02` | Ubiquitous | The system SHALL NOT show project separators in single-project (legacy) mode. |
| `REQ-03` | Event | When the user presses `Enter` on any change (from any project), the app SHALL push `ChangeDetailScreen`. |
| `REQ-04` | Event | When the user presses `r`, the app SHALL reload all projects defined in config. |
| `REQ-05` | Unwanted | If a project becomes unavailable after startup, the system SHALL skip it silently during reload. |
| `REQ-06` | Optional | Where multi-project config is active, `SpecHealthScreen` SHALL show changes from all projects, grouped with separator rows. |
| `REQ-07` | Ubiquitous | In single-project mode, `SpecHealthScreen` behavior SHALL be identical to the current spec. |
| `REQ-08` | Optional | Where multi-project config is active, `DecisionsTimeline` SHALL aggregate decisions from `archive/` of all configured projects. |
| `REQ-09` | Ubiquitous | Decisions SHALL be ordered chronologically (ascending) across all projects combined. |
| `REQ-PR01` | Event | When View 2 mounts, the system SHALL launch `_load_pr_status_worker()`. |
| `REQ-PR02` | State | While the worker is running, PipelinePanel SHALL show `…  PR`. |
| `REQ-PR03` | Event | When the worker completes with a result, PipelinePanel SHALL update with state symbol, number, and review counts. |
| `REQ-PR04` | Event | When the worker completes with no result, PipelinePanel SHALL show `—  PR`. |
| `REQ-PR05` | Unwanted | If `gh` is unavailable, `get_pr_status` SHALL return `None` without raising. |
| `REQ-PR06` | Unwanted | If `gh` returns non-zero exit code, `get_pr_status` SHALL return `None` without raising. |
| `REQ-PR07` | Event | When the user presses `r`, the PR status SHALL reload (worker relaunched with fresh panels). |
| `REQ-PR08` | Ubiquitous | The review count SHALL only show non-zero values. |
| `REQ-V01` | Event | When el usuario pulsa `V` en View 1, the app SHALL hacer `push_screen(VelocityView)`. |
| `REQ-V02` | Event | When el usuario pulsa `Esc`, the app SHALL hacer `pop_screen`. |
| `REQ-V03` | Event | When el usuario pulsa `j/k`, the screen SHALL hacer scroll. |
| `REQ-V05` | Ubiquitous | VelocityView SHALL mostrar una sección `THROUGHPUT` con una barra Unicode por semana (últimas 8 semanas ISO). |
| `REQ-V06` | Ubiquitous | Cada barra SHALL escalar proporcionalmente al máximo del período. |
| `REQ-V08` | Ubiquitous | VelocityView SHALL mostrar una sección `LEAD TIME` con Median, P90, total de changes y el más lento. |
| `REQ-V09` | Unwanted | If `median_lead_time is None`, the section SHALL mostrar `Not enough data`. |
| `REQ-V10` | Event | When el usuario pulsa `E`, the app SHALL copiar un reporte Markdown al portapapeles. |
| `REQ-V11` | Event | When export completes, the app SHALL mostrar toast `Report copied to clipboard`. |
| `REQ-V12` | Unwanted | If `compute_velocity` returns empty, VelocityView SHALL mostrar `No data available`. |
| `REQ-SP-01` | Event | When `SkillPaletteScreen` se monta, the screen SHALL cargar skills via `load_skills` y poblar el DataTable. |
| `REQ-SP-02` | Unwanted | If no hay skills disponibles, the screen SHALL mostrar `No skills found`. |
| `REQ-SP-03` | Event | When el usuario pulsa Enter sobre una fila, the screen SHALL copiar el comando y mostrar `notify("Copied: {cmd}")`. |
| `REQ-SP-04` | Event | When el usuario pulsa `/`, the screen SHALL activar el Input de filtrado. |
| `REQ-SP-05` | Event | When el texto del Input cambia, the screen SHALL filtrar filas (case-insensitive) por command o description. |
| `REQ-SP-06` | Event | When el filtro está activo y el usuario pulsa Esc, the screen SHALL limpiar el filtro y devolver foco al DataTable. |
| `REQ-SP-07` | Event | When el filtro está vacío y el usuario pulsa Esc, the screen SHALL hacer `pop_screen`. |
| `REQ-SP-08` | Event | When hay `change_name` en contexto y el skill está en `_CONTEXT_AWARE`, the screen SHALL copiar `/{skill-name} {change_name}`. |
| `REQ-SP-09` | Event | When el skill no es context-aware o no hay contexto, the screen SHALL copiar `/{skill-name}` sin argumentos. |
| `REQ-SP-10` | Event | When el usuario pulsa `K` en EpicsView, the app SHALL abrir `SkillPaletteScreen` sin contexto. |
| `REQ-SP-11` | Event | When el usuario pulsa `K` en ChangeDetailScreen, the app SHALL abrir `SkillPaletteScreen` con `change_name` del change activo. |
| `REQ-SP-12` | Event | When el usuario pulsa `ctrl+p` desde cualquier pantalla, the app SHALL abrir `SkillPaletteScreen` sin contexto. |
| `REQ-CB-10` | Event | When EpicsView renders the change list, the system SHALL display a `SIZE` column showing `complexity_label` (XS/S/M/L/XL) for each change row. |
| `REQ-CB-11` | Ubiquitous | The `SIZE` column SHALL be positioned between `change` and `propose`. |
| `REQ-CB-12` | State | While `complexity_label == "XL"`, the system SHALL render the badge in yellow. |
| `REQ-CB-13` | Ubiquitous | Separator rows SHALL show an empty string in the `SIZE` column. |
| `REQ-CB-14` | Ubiquitous | The system SHALL compute `ChangeMetrics` for each visible change during `_populate`. |
| `REQ-CB-15` | Unwanted | If `parse_metrics` raises, the system SHALL show `"?"` in the `SIZE` column without crashing. |
| `REQ-PD-01` | Event | When el usuario pulsa `P` en EpicsView, the app SHALL navegar a ProgressDashboard mostrando los changes actualmente visibles. |
| `REQ-PD-02` | Event | When el usuario pulsa `Escape` en ProgressDashboard, the app SHALL volver a EpicsView sin modificar su estado. |
| `REQ-PD-03` | Ubiquitous | The ProgressDashboard SHALL mostrar una sección GLOBAL con: número de changes, total de tareas (done + pending), porcentaje completado (done / total × 100, redondeado) y barra de progreso visual proporcional. |
| `REQ-PD-04` | Unwanted | If no hay changes, the ProgressDashboard SHALL mostrar "No changes to display". |
| `REQ-PD-05` | Unwanted | If el total de tareas es 0, the ProgressDashboard SHALL mostrar 0% sin dividir por cero. |
| `REQ-PD-06` | Ubiquitous | The ProgressDashboard SHALL mostrar una sección BY CHANGE con una línea por change: nombre, barra de progreso, ratio done/total, y fase más avanzada completada (o `—` si ninguna). |
| `REQ-PD-07` | Ubiquitous | The ProgressDashboard SHALL mostrar `0/0` para un change sin `tasks.md`. |
| `REQ-PD-08` | Ubiquitous | The ProgressDashboard SHALL mostrar una sección PIPELINE DISTRIBUTION contando, para cada fase, cuántos changes la tienen como su fase más avanzada completada (última DONE). |
| `REQ-PD-09` | Ubiquitous | The ProgressDashboard SHALL mostrar una barra visual proporcional al número de changes en cada fase. |
| `REQ-PD-10` | Unwanted | If ningún change tiene una fase como la más avanzada, the ProgressDashboard SHALL mostrar `·` para esa fase. |
| `REQ-PD-11` | Event | When el usuario pulsa `e`, the app SHALL copiar el reporte en Markdown al clipboard y notificar "Report copied to clipboard". |
| `REQ-PD-12` | Event | When el usuario pulsa `j`, the app SHALL hacer scroll hacia abajo. |
| `REQ-PD-13` | Event | When el usuario pulsa `k`, the app SHALL hacer scroll hacia arriba. |
| `REQ-MG-01` | Optional | Where `milestones.yaml` exists and single-project mode is active, `EpicsView` SHALL display active changes grouped under milestone header rows. |
| `REQ-MG-02` | Ubiquitous | Each milestone header SHALL be rendered as a non-selectable separator row (no key registered in `_change_map`). |
| `REQ-MG-03` | Optional | Where a change is not assigned to any milestone, the system SHALL display it under an `── unassigned ──` separator. |
| `REQ-MG-04` | Unwanted | If `milestones.yaml` does not exist or returns `[]`, `EpicsView` SHALL fall back to the current flat list behavior without modification. |
| `REQ-MG-05` | Optional | Where multi-project mode is active (`len(active_projects) > 1`), milestone grouping SHALL NOT be applied — existing project separator behavior is preserved. |
| `REQ-MG-06` | Ubiquitous | The archived section (`── archived ──`) SHALL NOT be grouped by milestone, regardless of milestones.yaml content. |
| `REQ-MG-07` | Optional | Where `milestones.yaml` exists and the `unassigned` section is empty (all active changes are assigned), the `── unassigned ──` separator SHALL NOT be rendered. |
| `REQ-MG-08` | Optional | Where search filter is active, milestone grouping is preserved — only matching changes are shown within each milestone section. Empty milestone sections (no matches) are omitted. |
| `REQ-MG-09` | Ubiquitous | A change that appears in `milestones.yaml` but has no corresponding `Change` object (e.g., archived) SHALL be silently skipped — no empty row rendered. |
| `REQ-TU-01` | Event | When the user presses `T` in EpicsView, the system SHALL push `TodosScreen` onto the screen stack. |
| `REQ-TU-02` | Event | When the user presses `Escape` in TodosScreen, the system SHALL pop the screen and return to EpicsView. |
| `REQ-TU-03` | Ubiquitous | TodosScreen SHALL display todos grouped by `TodoFile`, with a header showing `── {title} [{done}/{total}] ──`. |
| `REQ-TU-04` | Ubiquitous | Completed items (`done=True`) SHALL be displayed with `dim` style and a `✓` prefix. |
| `REQ-TU-05` | Ubiquitous | Pending items (`done=False`) SHALL be displayed with a `·` prefix and default style. |
| `REQ-TU-06` | Unwanted | If `load_todos()` returns `[]`, the system SHALL display "No todos found". |
| `REQ-TU-07` | Ubiquitous | TodosScreen SHALL support scroll via `j`/`k` bindings, delegating to the inner `ScrollableContainer`. |
| `REQ-TU-08` | Ubiquitous | The screen title SHALL be "sdd-tui — todos". |
| `REQ-SW01` | Event | When the user presses `S` in `EpicsView`, the system SHALL open `GitWorkflowSetupScreen`. |
| `REQ-SW02` | Ubiquitous | The `S` binding SHALL appear in the `Footer` with label "Setup". |
| `REQ-WZ01` | Event | When `GitWorkflowSetupScreen` mounts, the system SHALL display the first question of the wizard. |
| `REQ-WZ02` | Ubiquitous | The wizard SHALL present 5 questions in sequence: (1) Issue tracker, (2) Git host, (3) Branching model, (4) Change prefix, (5) Changelog format. |
| `REQ-WZ03` | Ubiquitous | Options marked as "coming soon" (jira, trello, bitbucket, gitlab) SHALL be displayed as disabled. Attempting to select them SHALL show "Not yet available" without advancing. |
| `REQ-WZ04` | Event | When the user selects "Custom prefix…" for change prefix, the system SHALL show a text input for free-form entry. |
| `REQ-WZ05` | Event | When the user completes all 5 questions, the system SHALL write the `git_workflow:` section to `openspec/config.yaml` and notify "Git workflow configured ✓". |
| `REQ-WZ06` | Ubiquitous | The write operation SHALL be atomic: only `git_workflow:` block is added or replaced; the rest of `config.yaml` remains unchanged. |
| `REQ-WZ07` | Unwanted | If `openspec/config.yaml` does not exist, the system SHALL create it with only the `git_workflow:` section plus the comment `# Añadir jira_prefix: si usas SDD`. |
| `REQ-WZ08` | Event | When the user presses `Escape`, the system SHALL discard all answers and return to `EpicsView` without modifying `config.yaml`. |
| `REQ-WZ09` | Ubiquitous | The wizard is all-or-nothing: partial answers are never persisted. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
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
| `next_command(pipeline, tasks, name)` como función pura module-level | Método privado de Screen | Testable sin TUI, reutilizada por PipelinePanel y ChangeDetailScreen |
| `copy_to_clipboard` nativo de Textual | `pyperclip` / `subprocess pbcopy` | Sin deps nuevas; API nativa ≥ 0.70.0 |
| `.remove()` + `.mount()` para refresh | Re-compose completa | Quirúrgico; Textual soporta mount/remove en widgets montados |
| `refresh_changes()` retorna `list[Change]` | Segunda llamada a `_load_changes()` | Evita doble carga del filesystem |
| `row_key` para selección en EpicsView | Índice de fila | El separador `── archived ──` rompe la correspondencia índice→change |
| `Change.archived: bool` | Path-based detection | El modelo conoce su origen; EpicsView no necesita inspeccionar paths |
| Separator row sin key | Fila con key especial | `_change_map.get()` devuelve None para rows sin key — comportamiento natural |
