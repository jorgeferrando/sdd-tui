# Design: View 9 — Delta Specs Viewer

## Metadata
- **Change:** view-9-delta-specs
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** draft

## Resumen Técnico

Se añaden dos módulos nuevos. El primero es `core/spec_parser.py`: funciones puras que parsean
el formato ADDED/MODIFIED/REMOVED de las delta specs y extraen las tablas de decisiones de los
`design.md` archivados. El segundo es `tui/spec_evolution.py`: `SpecEvolutionScreen` (binding `E`
desde View 2) y `DecisionsTimeline` (binding `X` desde View 1).

El rendering de las secciones coloreadas sigue el patrón ya establecido en el proyecto:
`ScrollableContainer(Static)` con `Rich.Text` para contenido dinámico con estilos, y
`rich.Markdown` para contenido en fallback.

## Arquitectura

```
EpicsView ──── X ────→ DecisionsTimeline
                          └── collect_archived_decisions(archive_dir)
                                └── extract_decisions(design_path)

ChangeDetailScreen ── E ──→ SpecEvolutionScreen
                               ├── domain list (ListView) [si >1 dominio]
                               └── diff panel (ScrollableContainer + Static)
                                     └── parse_delta(spec_path)
                                     └── toggle D → spec canónica (rich.Markdown)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/spec_parser.py` | Módulo core | Dataclasses + funciones `parse_delta`, `extract_decisions`, `collect_archived_decisions` |
| `src/sdd_tui/tui/spec_evolution.py` | Screen TUI | `SpecEvolutionScreen` + `DecisionsTimeline` |
| `tests/test_spec_parser.py` | Tests unitarios | Cobertura de `parse_delta` y `extract_decisions` / `collect_archived_decisions` |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | Añadir binding `E` + `action_spec_evolution` | Abrir `SpecEvolutionScreen` desde View 2 |
| `src/sdd_tui/tui/epics.py` | Añadir binding `X` + `action_decisions_timeline` | Abrir `DecisionsTimeline` desde View 1 |

## Scope

- **Total archivos:** 5
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Reutiliza `rich.Text`, `rich.Markdown` (ya en uso en el proyecto)
- Reutiliza patrón `ScrollableContainer(Static)` de `change_detail.py`
- No requiere migración ni cambio de datos
- No depende de changes pendientes

## Patrones Aplicados

- **Módulo core puro**: `spec_parser.py` sin imports de TUI, igual que `metrics.py`
- **Screen con `push_screen` / `pop_screen`**: igual que `SpecHealthScreen` y `DocumentViewerScreen`
- **`Rich.Text` para coloreado por sección**: `ScrollableContainer(Static(...))` ya establecido en `doc_viewer.py` y `change_detail.py`
- **`ListView` para selector de dominios**: patrón de `SpecSelectorScreen` en `doc_viewer.py`
- **`Binding("escape", "app.pop_screen", "Back")`**: convención de todas las screens

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Panel izquierdo con `ListView` omitido si 1 dominio | Siempre mostrarlo | Un único dominio no necesita selector; pantalla completa más legible |
| `Rich.Text` para secciones ADDED/MODIFIED/REMOVED | CSS custom | DataTable no aplica; es el patrón ya establecido para contenido dinámico |
| `DecisionsTimeline` usa `ScrollableContainer(Static)` | DataTable | Vista de solo lectura lineal, sin necesidad de selección por fila |
| Orden por prefijo YYYY-MM-DD del directorio archive | `git log` | El prefijo ya es canónico; no requiere acceso a git |
| `fallback=True` en DeltaSpec en lugar de excepción | Excepción | Los delta specs sin marcadores (legacy) deben funcionar sin error |
| Toggle `D` único (delta ↔ canónica) | Dos bindings distintos | Menos bindings; estado claro con label en header |
| Regex simple para tabla markdown | Parser MD completo | Suficiente para extraer filas `\| ... \| ... \| ... \|` sin AST |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_parse_delta_with_markers` | Unit | ADDED/MODIFIED/REMOVED se extraen correctamente |
| `test_parse_delta_fallback` | Unit | Archivo sin marcadores devuelve `fallback=True` |
| `test_parse_delta_case_insensitive` | Unit | `## added` y `## ADDED` se reconocen igual |
| `test_extract_decisions_with_table` | Unit | Filas de tabla de decisiones se parsean correctamente |
| `test_extract_decisions_no_table` | Unit | `design.md` sin tabla devuelve lista vacía |
| `test_collect_archived_decisions_order` | Unit | Directorios ordenados por prefijo YYYY-MM-DD |
| `test_collect_archived_decisions_skip_invalid` | Unit | Directorios sin prefijo fecha se ignoran silenciosamente |

## Notas de Implementación

- `SpecEvolutionScreen.__init__` recibe `change: Change` y lee `change.path / "specs"` para
  detectar dominios disponibles.
- `ChangeDetailScreen` necesita acceder al path de las specs canónicas:
  `Path.cwd() / "openspec" / "specs" / domain / "spec.md"` para el toggle canónica.
- `DecisionsTimeline` recibe `archive_dir: Path` calculado en `action_decisions_timeline` de
  `EpicsView` como `Path.cwd() / "openspec" / "changes" / "archive"`.
- El header de `SpecEvolutionScreen` muestra `[delta]` o `[canonical]` según el modo activo
  para dar feedback visual del toggle.
