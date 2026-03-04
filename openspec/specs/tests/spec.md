# Spec: Tests — Cobertura de pantallas TUI

## Metadata
- **Dominio:** tests
- **Change:** tui-tests
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

El core de sdd-tui tiene cobertura completa (62 tests). Las pantallas Textual
(EpicsView, ChangeDetailScreen, SpecHealthScreen, SpecEvolutionScreen,
DocumentViewerScreen) no tienen ningún test.

Sin tests de integración TUI, cualquier cambio en bindings, layout condicional
o lógica de pantalla es un salto al vacío — las regresiones solo se detectan
manualmente. Este change establece la red de seguridad antes de las features
futuras (ux-feedback, ux-navigation, view-help-screen…).

## Comportamiento Actual

Solo existen tests de core (pytest sync, sin asyncio, sin Pilot).
No existe `pytest-asyncio` en las dependencias de desarrollo.
`tests/conftest.py` tiene fixtures para `openspec_dir` y `change_dir` (core only).

## Decisiones

### Backend async: pytest-asyncio
Textual usa `asyncio` internamente. `App.run_test()` retorna un async context manager
que requiere `await`. pytest-asyncio es la recomendación oficial de Textual.

### Aislamiento de git: mock de GitReader
Los tests no dependen de un repo git real. Se usa `unittest.mock.patch` sobre
`sdd_tui.core.git_reader.GitReader` — mismo patrón que `test_git_reader.py`.
Esto garantiza tests deterministas independientemente del estado del repo local.

### Granularidad: un test por comportamiento verificable
No un test por binding (demasiado granular) ni un test por pantalla (demasiado amplio).
Un test verifica un comportamiento observable: "Enter navega a detalle",
"toggle archivados añade filas", "Esc regresa a pantalla anterior".

## Requisitos (EARS)

### Setup / Infraestructura

- **REQ-01** `[Ubiquitous]` The test suite SHALL use `pytest-asyncio` as the async backend for all TUI tests.
- **REQ-02** `[Ubiquitous]` The test suite SHALL mock `GitReader` to avoid real git calls in TUI tests.
- **REQ-03** `[Ubiquitous]` TUI fixtures SHALL create a minimal `openspec/` structure in `tmp_path` with at least one active change.

### EpicsView (View 1)

- **REQ-04** `[Event]` When the app loads, the EpicsView SHALL render a DataTable with one row per active change.
- **REQ-05** `[Event]` When the user presses `a`, the EpicsView SHALL toggle display of archived changes (filas adicionales visibles / ocultas).
- **REQ-06** `[Event]` When the user presses `Enter` on an active change row, the app SHALL push `ChangeDetailScreen`.
- **REQ-07** `[Event]` When the user presses `H`, the app SHALL push `SpecHealthScreen`.
- **REQ-08** `[Event]` When the user presses `r`, the EpicsView SHALL reload without navigating away.

### ChangeDetailScreen (View 2)

- **REQ-09** `[Event]` When ChangeDetailScreen loads, it SHALL display a DataTable with the tasks of the change.
- **REQ-10** `[Event]` When the user presses `Esc`, the app SHALL pop back to EpicsView.
- **REQ-11** `[Event]` When the user presses `p`, `d`, `s`, `t`, or `q`, the app SHALL push `DocumentViewerScreen` for the corresponding file.
- **REQ-12** `[Event]` When the user presses `E`, the app SHALL push `SpecEvolutionScreen`.

### SpecHealthScreen (View 8)

- **REQ-13** `[Event]` When SpecHealthScreen loads, it SHALL display a DataTable with one row per active change.
- **REQ-14** `[Unwanted]` If a change has `req_count == 0`, the corresponding row SHALL be styled in yellow.
- **REQ-15** `[Event]` When the user presses `Esc`, the app SHALL pop back to EpicsView.

### SpecEvolutionScreen (View 9)

- **REQ-16** `[Event]` When SpecEvolutionScreen loads, it SHALL render in delta mode by default.
- **REQ-17** `[Event]` When the user presses `D`, the screen SHALL toggle between delta mode and canonical mode.
- **REQ-18** `[Event]` When the user presses `Esc`, the app SHALL pop back to ChangeDetailScreen.

### DocumentViewerScreen (View 4)

- **REQ-19** `[Event]` When DocumentViewerScreen loads with a valid file path, it SHALL render the file content.
- **REQ-20** `[Unwanted]` If the file does not exist, the DocumentViewerScreen SHALL display a "not found" message.
- **REQ-21** `[Event]` When the user presses `Esc`, the app SHALL pop back to the previous screen.

## Escenarios de verificación

**REQ-04** — EpicsView carga changes
**Dado** un `openspec/` con 2 changes activos y GitReader mockeado
**Cuando** se lanza `SddTuiApp` con `run_test()`
**Entonces** el DataTable de EpicsView tiene exactamente 2 filas

**REQ-05** — Toggle archivados
**Dado** EpicsView con 1 change activo y 1 archivado
**Cuando** el usuario pulsa `a`
**Entonces** el DataTable tiene 2 filas (change activo + change archivado)
**Y cuando** pulsa `a` de nuevo
**Entonces** el DataTable vuelve a tener 1 fila

**REQ-06** — Enter navega a detalle
**Dado** EpicsView con 1 change activo
**Cuando** el usuario pulsa `Enter`
**Entonces** la pantalla activa es `ChangeDetailScreen`

**REQ-20** — Archivo no encontrado
**Dado** `DocumentViewerScreen` inicializado con path inexistente
**Cuando** la pantalla carga
**Entonces** el contenido visible contiene texto de "not found" o "no encontrado"

## Interfaces / Contratos

### Fixtures en `tests/conftest.py`

```python
@pytest_asyncio.fixture
async def app_with_changes(tmp_path: Path) -> AsyncIterator[SddTuiApp]:
    """SddTuiApp sobre openspec/ mínimo con 1 change activo."""

@pytest.fixture
def openspec_with_archive(tmp_path: Path) -> Path:
    """openspec/ con 1 change activo y 1 archivado."""
```

### Patrón de test TUI

```python
@pytest.mark.asyncio
async def test_something(app_with_changes):
    async with app_with_changes.run_test() as pilot:
        await pilot.press("h")
        # asserts sobre pilot.app.screen, query_one(), etc.
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| pytest-asyncio | anyio | Recomendación oficial Textual; anyio no aporta nada en este stack |
| mock GitReader | repo git real en tmp_path | Tests deterministas; patrón ya establecido en test_git_reader.py |
| Un test por comportamiento | Un test por binding / un test por pantalla | Balance entre granularidad y legibilidad |
| `@pytest_asyncio.fixture` para fixtures async | `@pytest.fixture` con `asyncio.run()` | Integración nativa con el event loop de pytest-asyncio |

## Abierto / Pendiente

Ninguno.
