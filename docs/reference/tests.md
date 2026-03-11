# Tests Reference

The tests domain defines the infrastructure and conventions for testing sdd-tui with pytest and pytest-asyncio. TUI screens are tested using Textual's `app.run_test()` and `Pilot` API, which allows simulating key presses and asserting on rendered output. Core logic is tested with plain pytest functions — no TUI harness needed. Shared fixtures (fake openspec directories, mock git readers) live in `conftest.py` and are reused across the full test suite of 489+ tests.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-01` | Ubiquitous | The test suite SHALL use `pytest-asyncio` as the async backend for all TUI tests. |
| `REQ-02` | Ubiquitous | The test suite SHALL mock `GitReader` to avoid real git calls in TUI tests. |
| `REQ-03` | Ubiquitous | TUI fixtures SHALL create a minimal `openspec/` structure in `tmp_path` with at least one active change. ### EpicsView (View 1) |
| `REQ-04` | Event | When the app loads, the EpicsView SHALL render a DataTable with one row per active change. |
| `REQ-05` | Event | When the user presses `a`, the EpicsView SHALL toggle display of archived changes (filas adicionales visibles / ocultas). |
| `REQ-06` | Event | When the user presses `Enter` on an active change row, the app SHALL push `ChangeDetailScreen`. |
| `REQ-07` | Event | When the user presses `H`, the app SHALL push `SpecHealthScreen`. |
| `REQ-08` | Event | When the user presses `r`, the EpicsView SHALL reload without navigating away. ### ChangeDetailScreen (View 2) |
| `REQ-09` | Event | When ChangeDetailScreen loads, it SHALL display a DataTable with the tasks of the change. |
| `REQ-10` | Event | When the user presses `Esc`, the app SHALL pop back to EpicsView. |
| `REQ-11` | Event | When the user presses `p`, `d`, `s`, `t`, or `q`, the app SHALL push `DocumentViewerScreen` for the corresponding file. |
| `REQ-12` | Event | When the user presses `E`, the app SHALL push `SpecEvolutionScreen`. ### SpecHealthScreen (View 8) |
| `REQ-13` | Event | When SpecHealthScreen loads, it SHALL display a DataTable with one row per active change. |
| `REQ-14` | Unwanted | If a change has `req_count == 0`, the corresponding row SHALL be styled in yellow. |
| `REQ-15` | Event | When the user presses `Esc`, the app SHALL pop back to EpicsView. ### SpecEvolutionScreen (View 9) |
| `REQ-16` | Event | When SpecEvolutionScreen loads, it SHALL render in delta mode by default. |
| `REQ-17` | Event | When the user presses `D`, the screen SHALL toggle between delta mode and canonical mode. |
| `REQ-18` | Event | When the user presses `Esc`, the app SHALL pop back to ChangeDetailScreen. ### DocumentViewerScreen (View 4) |
| `REQ-19` | Event | When DocumentViewerScreen loads with a valid file path, it SHALL render the file content. |
| `REQ-20` | Unwanted | If the file does not exist, the DocumentViewerScreen SHALL display a "not found" message. |
| `REQ-21` | Event | When the user presses `Esc`, the app SHALL pop back to the previous screen. ## Escenarios de verificación **REQ-04** — EpicsView carga changes **Dado** un `openspec/` con 2 changes activos y GitReader mockeado **Cuando** se lanza `SddTuiApp` con `run_test()` **Entonces** el DataTable de EpicsView tiene exactamente 2 filas **REQ-05** — Toggle archivados **Dado** EpicsView con 1 change activo y 1 archivado **Cuando** el usuario pulsa `a` **Entonces** el DataTable tiene 2 filas (change activo + change archivado) **Y cuando** pulsa `a` de nuevo **Entonces** el DataTable vuelve a tener 1 fila **REQ-06** — Enter navega a detalle **Dado** EpicsView con 1 change activo **Cuando** el usuario pulsa `Enter` **Entonces** la pantalla activa es `ChangeDetailScreen` **REQ-20** — Archivo no encontrado **Dado** `DocumentViewerScreen` inicializado con path inexistente **Cuando** la pantalla carga **Entonces** el contenido visible contiene texto de "not found" o "no encontrado" ## Interfaces / Contratos ### Fixtures en `tests/conftest.py` ```python @pytest_asyncio.fixture async def app_with_changes(tmp_path: Path) -> AsyncIterator[SddTuiApp]: """SddTuiApp sobre openspec/ mínimo con 1 change activo.""" @pytest.fixture def openspec_with_archive(tmp_path: Path) -> Path: """openspec/ con 1 change activo y 1 archivado.""" ``` ### Patrón de test TUI ```python @pytest.mark.asyncio async def test_something(app_with_changes): async with app_with_changes.run_test() as pilot: await pilot.press("h") # asserts sobre pilot.app.screen, query_one(), etc. ``` ## Decisiones Tomadas \| Decisión \| Alternativa Descartada \| Motivo \| \|---------\|----------------------\|--------\| \| pytest-asyncio \| anyio \| Recomendación oficial Textual; anyio no aporta nada en este stack \| \| mock GitReader \| repo git real en tmp_path \| Tests deterministas; patrón ya establecido en test_git_reader.py \| \| Un test por comportamiento \| Un test por binding / un test por pantalla \| Balance entre granularidad y legibilidad \| \| `@pytest_asyncio.fixture` para fixtures async \| `@pytest.fixture` con `asyncio.run()` \| Integración nativa con el event loop de pytest-asyncio \| ## Abierto / Pendiente Ninguno. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| pytest-asyncio | anyio | Recomendación oficial Textual; anyio no aporta nada en este stack |
| mock GitReader | repo git real en tmp_path | Tests deterministas; patrón ya establecido en test_git_reader.py |
| Un test por comportamiento | Un test por binding / un test por pantalla | Balance entre granularidad y legibilidad |
| `@pytest_asyncio.fixture` para fixtures async | `@pytest.fixture` con `asyncio.run()` | Integración nativa con el event loop de pytest-asyncio |
