# Design: TUI Tests

## Metadata
- **Change:** tui-tests
- **Fecha:** 2026-03-04
- **Estado:** draft

## Resumen Técnico

Tests de integración usando `App.run_test()` de Textual + `pytest-asyncio`.
Cada test file cubre una pantalla. Los tests son funciones async marcadas con
`@pytest.mark.asyncio` que crean la app, abren un `Pilot` y hacen asserts sobre
el estado del DOM Textual.

El único obstáculo técnico es que `SddTuiApp.__init__` instancia `GitReader`
internamente (sin DI). La solución es `unittest.mock.patch` sobre
`sdd_tui.tui.app.GitReader` — el mismo patrón de `test_git_reader.py`.

No se modifica código de producción. Solo se añaden tests y una dependencia de dev.

## Arquitectura

```
tests/
├── conftest.py          ← extendido con fixtures TUI
├── test_tui_epics.py    ← EpicsView
├── test_tui_change_detail.py
├── test_tui_spec_health.py
├── test_tui_spec_evolution.py
└── test_tui_doc_viewer.py
```

## Archivos a Crear

| Archivo | Propósito |
|---------|-----------|
| `tests/test_tui_epics.py` | REQ-04..08 (EpicsView) |
| `tests/test_tui_change_detail.py` | REQ-09..12 (ChangeDetailScreen) |
| `tests/test_tui_spec_health.py` | REQ-13..15 (SpecHealthScreen) |
| `tests/test_tui_spec_evolution.py` | REQ-16..18 (SpecEvolutionScreen) |
| `tests/test_tui_doc_viewer.py` | REQ-19..21 (DocumentViewerScreen) |

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `tests/conftest.py` | Añadir `openspec_with_change` y `openspec_with_archive` para TUI tests |
| `pyproject.toml` | Añadir `pytest-asyncio` y `anyio` a `[dependency-groups] dev` |

## Scope

- **Total archivos:** 7 (5 nuevos + 2 modificados)
- **Resultado:** Ideal

## Patrón Base

### Fixture en conftest.py

```python
@pytest.fixture
def openspec_with_change(tmp_path: Path) -> Path:
    """openspec/ con 1 change activo que tiene tasks.md."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    change = openspec / "changes" / "my-change"
    change.mkdir()
    (change / "proposal.md").write_text("# Proposal\n")
    (change / "tasks.md").write_text("- [x] **T01** Done\n- [ ] **T02** Pending\n")
    return openspec

@pytest.fixture
def openspec_with_archive(openspec_with_change: Path) -> Path:
    """openspec/ con 1 change activo y 1 archivado."""
    archived = openspec_with_change / "changes" / "archive" / "2026-01-01-old-change"
    archived.mkdir()
    (archived / "proposal.md").write_text("# Old Proposal\n")
    (archived / "tasks.md").write_text("- [x] **T01** Done\n")
    return openspec_with_change
```

### Patrón de test

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from sdd_tui.tui.app import SddTuiApp

def _mock_git():
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m

@pytest.mark.asyncio
async def test_epics_loads_changes(openspec_with_change: Path) -> None:
    with patch("sdd_tui.tui.app.GitReader", _mock_git()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            table = app.query_one("EpicsView DataTable")
            assert table.row_count == 1
```

### pytest-asyncio mode

Configurar en `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Con `asyncio_mode = "auto"` no hace falta `@pytest.mark.asyncio` en cada test —
todos los tests async se tratan como asyncio automáticamente.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `patch("sdd_tui.tui.app.GitReader")` | Refactorizar SddTuiApp para DI | No tocar prod en este change; mismo patrón que test_git_reader.py |
| `asyncio_mode = "auto"` en pyproject.toml | `@pytest.mark.asyncio` en cada test | Menos boilerplate, estándar en proyectos Textual |
| Un archivo de test por pantalla | Todos en un archivo | Alineado con convención del proyecto (test_pipeline.py, test_reader.py…) |
| Fixtures en conftest.py | Fixtures inline en cada archivo | Reutilizables, DRY |
| `app.query_one("ClassName")` para asserts DOM | Inspeccionar `app.screen` directo | Más específico, soporta pantallas apiladas |

## Tests Planificados

| Test | Archivo | REQ |
|------|---------|-----|
| `test_epics_loads_changes` | test_tui_epics.py | REQ-04 |
| `test_epics_toggle_archived` | test_tui_epics.py | REQ-05 |
| `test_epics_enter_navigates_to_detail` | test_tui_epics.py | REQ-06 |
| `test_epics_h_navigates_to_health` | test_tui_epics.py | REQ-07 |
| `test_epics_r_reloads_in_place` | test_tui_epics.py | REQ-08 |
| `test_change_detail_shows_tasks` | test_tui_change_detail.py | REQ-09 |
| `test_change_detail_esc_goes_back` | test_tui_change_detail.py | REQ-10 |
| `test_change_detail_p_opens_proposal` | test_tui_change_detail.py | REQ-11 |
| `test_change_detail_e_opens_evolution` | test_tui_change_detail.py | REQ-12 |
| `test_spec_health_shows_changes` | test_tui_spec_health.py | REQ-13 |
| `test_spec_health_zero_reqs_yellow` | test_tui_spec_health.py | REQ-14 |
| `test_spec_health_esc_goes_back` | test_tui_spec_health.py | REQ-15 |
| `test_spec_evolution_default_delta_mode` | test_tui_spec_evolution.py | REQ-16 |
| `test_spec_evolution_d_toggles_canonical` | test_tui_spec_evolution.py | REQ-17 |
| `test_spec_evolution_esc_goes_back` | test_tui_spec_evolution.py | REQ-18 |
| `test_doc_viewer_renders_content` | test_tui_doc_viewer.py | REQ-19 |
| `test_doc_viewer_not_found` | test_tui_doc_viewer.py | REQ-20 |
| `test_doc_viewer_esc_goes_back` | test_tui_doc_viewer.py | REQ-21 |

## Notas de Implementación

- `SpecEvolutionScreen` y `ChangeDetailScreen` reciben el `Change` object en `__init__`,
  no el path. Hay que construir el objeto desde el fixture para pasárselo.
- `DocumentViewerScreen` recibe `file_path: Path` y `title: str` directamente —
  puede testearse de forma aislada sin necesidad de nav desde ChangeDetailScreen.
- `SpecHealthScreen` recibe `openspec_path: Path` — se puede construir directamente.
- Para REQ-14 (fila en amarillo): inspeccionar con `pilot.app.query_one(DataTable)`
  y verificar estilos de fila; Textual expone `.get_row_style()` o similar.
