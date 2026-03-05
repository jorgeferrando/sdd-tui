# Proposal: gh-actions

## Metadata
- **Change:** gh-actions
- **Jira:** N/A (proyecto standalone)
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-05
- **Estado:** draft

## Descripción

Integración con GitHub Actions y releases en la TUI. Tres features complementarias
que amplían la visibilidad del estado de un change más allá del PR:

1. **CI status** — estado del último workflow run de GitHub Actions para la rama del change
2. **Ship binding** — atajo que copia el comando `gh pr create` pre-rellenado al clipboard
3. **Releases screen** — pantalla con el histórico de releases/tags del repositorio

## Motivación

Actualmente la TUI muestra el estado del PR (número, aprobaciones, estado). Sin embargo,
falta visibilidad sobre:
- Si el CI está pasando o fallando (crítico antes de mergear)
- Una forma rápida de iniciar el flujo de creación de PR desde la TUI
- Un acceso al histórico de releases para contexto de versión

Estas tres piezas completan el ciclo git-GitHub sin salir de la TUI.

## Features

### Feature 1: CI Status en PipelinePanel

- Nueva función `get_ci_status(branch: str, cwd: Path) -> CiStatus | None` en `github.py`
- Usa `gh run list --branch {branch} --limit 1 --json status,conclusion,workflowName`
- `CiStatus` dataclass: `workflow: str`, `status: str` (queued/in_progress/completed), `conclusion: str | None` (success/failure/cancelled/skipped)
- Nueva fila "CI" en `PipelinePanel` con símbolos: ✓ success · — no runs ⟳ in_progress ✗ failure
- Carga async en `ChangeDetailScreen.on_mount` (mismo patrón que PR status, sentinel propio)
- Solo activo si `gh` está disponible (misma guard que PR)

### Feature 2: Ship Binding

- Binding `W` en `ChangeDetailScreen` → copia comando `gh pr create` al clipboard
- Comando generado: `gh pr create --title "[{change-name}] {description}" --body ""`
  donde `description` se extrae de la primera línea de `proposal.md` (si existe)
- Notificación `Copied: gh pr create ...`
- No ejecuta nada — solo clipboard (seguro, sin side effects)

### Feature 3: Releases Screen

- Binding `L` en `EpicsView` → abre `ReleasesScreen`
- `get_releases(cwd: Path) -> list[ReleaseInfo]` en `github.py`
  usando `gh release list --json tagName,name,publishedAt,isLatest`
- `ReleasesScreen`: DataTable con columnas TAG / NAME / DATE / LATEST
- Sin diff panel — solo tabla + Esc para volver
- Fallback: si `gh release list` falla → mensaje "No releases found"

## Alternativas consideradas

- **CI badge en EpicsView (columna extra)** — descartado: requeriría cargar CI status para TODOS los changes al abrir la app (coste O(N) de llamadas gh). PipelinePanel en view detalle es bajo demanda.
- **Ejecutar `gh pr create` directamente** — descartado: es una acción irreversible, clipboard es más seguro y preserva el control del usuario.
- **Tags en lugar de releases** — `gh release list` da más contexto (nombre, fecha). Si no hay releases pero sí tags, `git tag -l` como fallback.

## Impacto

- `core/github.py` — añadir `CiStatus`, `ReleaseInfo`, `get_ci_status()`, `get_releases()`
- `core/models.py` — sin cambios (CiStatus vive en github.py, no en models)
- `tui/change_detail.py` — nuevo worker CI, nuevo binding `W`, actualización PipelinePanel
- `tui/epics.py` — nuevo binding `L`
- `tui/releases.py` — nuevo (ReleasesScreen)
- `tests/test_github.py` — extender con tests CI + releases
- `tests/test_tui_releases.py` — nuevo
- `tests/test_tui_change_detail.py` — extender con tests CI + ship binding

## Criterios de éxito

- [ ] CI status visible en PipelinePanel con símbolo correcto según estado
- [ ] `W` copia comando `gh pr create` con título pre-rellenado
- [ ] `L` abre ReleasesScreen con la lista de releases
- [ ] Funciona con `gh` no instalado (graceful degradation → "—")
- [ ] Tests pasan al 100%, lint limpio
