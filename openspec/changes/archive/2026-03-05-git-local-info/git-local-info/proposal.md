# Proposal: git-local-info

## Metadata
- **Change:** git-local-info
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema

La TUI tiene integración básica con git (diff por tarea, estado del working tree, PR status),
pero no expone información git que sería útil al navegar:

1. **No se ve la rama activa** del proyecto en ninguna vista — hay que salir al terminal.
2. **No hay vista de commits del change** — solo el hash por tarea, sin contexto de
   cuándo se hizo, quién lo hizo, o el conjunto completo de commits.
3. **El indicador de working tree** existe (badge ✓/✗ en PipelinePanel) pero no dice
   qué archivos están modificados.

## Solución Propuesta

### 1. Rama activa en View 1 y View 2

Mostrar la rama git actual del proyecto en el subtítulo de la app (ya existe `app.sub_title`)
o en el header de View 2. Se obtiene con `git branch --show-current`.

### 2. Vista GitLog (tecla `G` desde View 2)

Nueva pantalla `GitLogScreen` que muestra todos los commits del change activo:
- Lista de commits con `hash`, `autor`, `fecha relativa`, `mensaje`
- Obtenidos con `git log --grep=[change-name] --format=...`
- Al seleccionar un commit → muestra el diff (reutiliza lógica de `DiffPanel`)
- Tecla `Esc` para volver a View 2

### 3. Working tree detail en View 2

Cuando hay cambios sin commitear, mostrar los archivos afectados en el DiffPanel
en lugar de solo "No uncommitted changes" — ya se hace el `git diff HEAD`, lo que
falta es mostrar también `git status --short` como cabecera del diff.

## Alternativas Consideradas

### A. Panel git permanente en View 1
Mostrar rama + estado en una columna de la tabla de changes. Descartado: ocupa
espacio en la vista principal sin aportar suficiente valor.

### B. Integrar con `gitk` o `tig`
Abrir herramientas externas. Descartado: rompe el flujo dentro de la TUI.

## Impacto

**Archivos a crear/modificar:**
- `core/git_reader.py` — añadir `get_branch()`, `get_change_log()`, `get_status_short()`
- `tui/git_log.py` — nueva `GitLogScreen`
- `tui/change_detail.py` — binding `G`, working tree detail, rama en header
- `tui/app.py` — rama en `sub_title`
- `tui/epics.py` — rama en sub_title (View 1)
- `tests/test_git_reader.py` — tests para los nuevos métodos
- `tests/test_tui_git_log.py` — tests de la nueva pantalla

**Sin cambios en:** skills, openspec, scripts.

## Criterios de Éxito

- [ ] View 1 muestra la rama git activa del proyecto en el subtítulo
- [ ] View 2 tiene binding `G` que abre GitLogScreen con commits del change
- [ ] GitLogScreen muestra hash, autor, fecha relativa y mensaje de cada commit
- [ ] Seleccionar un commit en GitLogScreen muestra su diff
- [ ] Working tree diff incluye cabecera con archivos modificados (`git status --short`)
- [ ] Tests cubren los nuevos métodos de `GitReader` y la pantalla `GitLogScreen`
