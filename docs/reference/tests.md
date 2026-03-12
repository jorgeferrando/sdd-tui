# Tests Reference

The tests domain defines the testing strategy and patterns for sdd-tui. The suite is split into unit tests (pure functions, readers, parsers) and TUI integration tests that drive real Textual screens in an in-process pilot. TUI tests use `pytest-asyncio` as the async backend, mock `GitReader` to avoid real git calls, and build a minimal `openspec/` fixture in `tmp_path`. Each test covers a single observable behavior — a key press, a screen transition, a rendered cell value — keeping tests readable and failures easy to diagnose. The full suite runs with `uv run pytest` and currently covers over 489 behaviors.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-01` | Ubiquitous | The test suite SHALL use `pytest-asyncio` as the async backend for all TUI tests. |
| `REQ-02` | Ubiquitous | The test suite SHALL mock `GitReader` to avoid real git calls in TUI tests. |
| `REQ-03` | Ubiquitous | TUI fixtures SHALL create a minimal `openspec/` structure in `tmp_path` with at least one active change. |
| `REQ-04` | Event | When the app loads, the EpicsView SHALL render a DataTable with one row per active change. |
| `REQ-05` | Event | When the user presses `a`, the EpicsView SHALL toggle display of archived changes (filas adicionales visibles / ocultas). |
| `REQ-06` | Event | When the user presses `Enter` on an active change row, the app SHALL push `ChangeDetailScreen`. |
| `REQ-07` | Event | When the user presses `H`, the app SHALL push `SpecHealthScreen`. |
| `REQ-08` | Event | When the user presses `r`, the EpicsView SHALL reload without navigating away. |
| `REQ-09` | Event | When ChangeDetailScreen loads, it SHALL display a DataTable with the tasks of the change. |
| `REQ-10` | Event | When the user presses `Esc`, the app SHALL pop back to EpicsView. |
| `REQ-11` | Event | When the user presses `p`, `d`, `s`, `t`, or `q`, the app SHALL push `DocumentViewerScreen` for the corresponding file. |
| `REQ-12` | Event | When the user presses `E`, the app SHALL push `SpecEvolutionScreen`. |
| `REQ-13` | Event | When SpecHealthScreen loads, it SHALL display a DataTable with one row per active change. |
| `REQ-14` | Unwanted | If a change has `req_count == 0`, the corresponding row SHALL be styled in yellow. |
| `REQ-15` | Event | When the user presses `Esc`, the app SHALL pop back to EpicsView. |
| `REQ-16` | Event | When SpecEvolutionScreen loads, it SHALL render in delta mode by default. |
| `REQ-17` | Event | When the user presses `D`, the screen SHALL toggle between delta mode and canonical mode. |
| `REQ-18` | Event | When the user presses `Esc`, the app SHALL pop back to ChangeDetailScreen. |
| `REQ-19` | Event | When DocumentViewerScreen loads with a valid file path, it SHALL render the file content. |
| `REQ-20` | Unwanted | If the file does not exist, the DocumentViewerScreen SHALL display a "not found" message. |
| `REQ-21` | Event | When the user presses `Esc`, the app SHALL pop back to the previous screen. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| pytest-asyncio | anyio | Recomendación oficial Textual; anyio no aporta nada en este stack |
| mock GitReader | repo git real en tmp_path | Tests deterministas; patrón ya establecido en test_git_reader.py |
| Un test por comportamiento | Un test por binding / un test por pantalla | Balance entre granularidad y legibilidad |
| `@pytest_asyncio.fixture` para fixtures async | `@pytest.fixture` con `asyncio.run()` | Integración nativa con el event loop de pytest-asyncio |
