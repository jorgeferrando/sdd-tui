# Proposal: TUI Tests — Cobertura de pantallas Textual

## Metadata
- **Change:** tui-tests
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

El core de sdd-tui (pipeline, reader, metrics, spec_parser) tiene cobertura
completa de tests. Las pantallas TUI no tienen ni un solo test.

Hoy mismo, cualquier cambio en `epics.py`, `change_detail.py`,
`spec_health.py`, `spec_evolution.py` o `doc_viewer.py` es un salto al vacío:
no hay nada que detecte si el binding `H` dejó de funcionar, si el diff panel
carga el commit equivocado, o si `SpecHealthScreen` calcula mal las columnas
condicionales (R, Q).

La deuda se acumula con cada feature nueva. A medida que crecen los keybindings
y las condiciones de layout, el riesgo de regresión silenciosa crece con ellos.

Textual tiene una API de testing nativa (`App.run_test()`, `Pilot`) diseñada
precisamente para esto: simular eventos de teclado, inspeccionar el DOM de
widgets, verificar contenido de DataTables. No es necesaria ninguna dependencia
extra.

## Solución Propuesta

Tests de integración para las 5 pantallas con `pytest-asyncio` + `Pilot`.
Un archivo de test por pantalla — misma estructura que los tests de core
existentes.

### Cobertura mínima por pantalla

**`EpicsView` (View 1)**
- Carga y muestra changes en DataTable
- `a` hace toggle de archivados (filas adicionales + separador)
- `Enter` sobre change activo navega a ChangeDetailScreen
- `Enter` sobre separador no hace nada
- `H` navega a SpecHealthScreen
- `r` recarga sin navegar fuera

**`ChangeDetailScreen` (View 2)**
- Muestra tareas con estado correcto (✓ / ·)
- Separadores de amendment presentes en posición correcta
- `RowHighlighted` carga diff en DiffPanel
- `Space` copia comando al clipboard y muestra notify
- `r` recarga en sitio (sin pop_screen)
- `Esc` regresa a View 1
- `p/d/s/t/q` abren DocumentViewerScreen con el archivo correcto
- `E` navega a SpecEvolutionScreen

**`SpecHealthScreen` (View 8)**
- DataTable con columnas correctas (R/Q condicionales)
- Fila en amarillo si `req_count == 0`
- `!Nd` en amarillo si inactividad > threshold
- `Esc` regresa a View 1

**`SpecEvolutionScreen` (View 9)**
- Delta mode por defecto (secciones ADDED/MODIFIED/REMOVED coloreadas)
- `D` alterna a canonical mode — título cambia
- Con 1 dominio: sin panel izquierdo
- Con N dominios: panel izquierdo con lista de dominios

**`DocumentViewerScreen` (View 4)**
- Muestra contenido Markdown del archivo
- Mensaje "not found" si el archivo no existe
- `Esc` regresa a la pantalla anterior

### Fixtures

Fixtures en `tests/conftest.py` extendidas con:
- `app_with_changes(tmp_path)` — SddTuiApp inicializado sobre openspec/ mínimo
- `change_with_tasks(change_dir)` — change con tasks.md y commits simulados
- `archived_change(openspec_dir)` — change archivado con design.md y decisions

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Snapshot testing (capturar output visual) | Detecta regresiones visuales | Frágil, se rompe con cualquier cambio de estilo | Descartada |
| Tests manuales / solo smoke test | Rápido de escribir | Ningún valor de automatización | Descartada |
| **Pilot + asserts sobre DOM** | API oficial de Textual, estable | Requiere `pytest-asyncio` | **Elegida** |

## Impacto Estimado

- **Dominio:** tests
- **Archivos nuevos:**
  - `tests/test_tui_epics.py`
  - `tests/test_tui_change_detail.py`
  - `tests/test_tui_spec_health.py`
  - `tests/test_tui_spec_evolution.py`
  - `tests/test_tui_doc_viewer.py`
  - `tests/conftest.py` — extendido con fixtures TUI
- **Archivos modificados:**
  - `pyproject.toml` — añadir `pytest-asyncio` como dev dependency
- **Breaking changes:** Ninguno — solo tests, no toca código de producción
- **Dependencias nuevas:** `pytest-asyncio` (solo en `[dev]`)

## Criterios de Éxito

- [ ] `uv run pytest tests/test_tui_*.py` pasa sin errores
- [ ] Cobertura: al menos los bindings principales y condiciones de layout de cada pantalla
- [ ] Sin `time.sleep` ni workarounds frágiles — tests deterministas
- [ ] Los tests documentan el comportamiento esperado de forma legible

## Preguntas Abiertas

- [ ] ¿`pytest-asyncio` o `anyio` como backend async? Textual recomienda `asyncio`
- [ ] ¿Mockear `GitReader` en tests TUI o usar repo git real en tmp_path?
- [ ] ¿Nivel de granularidad: un test por binding o agrupados por flujo de uso?
