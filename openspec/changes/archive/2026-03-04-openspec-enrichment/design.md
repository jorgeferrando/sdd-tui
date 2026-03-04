# Design: openspec enrichment (steering + requirements + spec.json)

## Metadata
- **Change:** openspec-enrichment
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-04
- **Estado:** approved

## Resumen Técnico

Se añaden dos funciones de lectura module-level en `core/reader.py`
(`load_steering`, `load_spec_json`) y se extiende `core/metrics.py` para
detectar `requirements.md` como artefacto y escanear sus REQs junto con
los de `specs/`.

En la TUI, se reutiliza `DocumentViewerScreen` para mostrar `steering.md`
desde View 1 (sin nueva pantalla) y se añade binding `q` en View 2 para
`requirements.md`. `SpecHealthScreen` recibe `has_requirements` con el mismo
patrón condicional que `has_research`.

Sin nuevos módulos Python — solo extensión de los existentes.

## Arquitectura

```
EpicsView [s] ──────────────────────────────────────────────────────────────────┐
                                                                                 │
openspec/steering.md ── load_steering() ──── DocumentViewerScreen("steering")  ←┘
openspec/{change}/requirements.md ──────────────────────────────────────────────┐
  └── parse_metrics() (artifacts + REQs)                                        │
  └── action_view_requirements() [q] ─── DocumentViewerScreen("requirements")  ←┘
openspec/{change}/spec.json ── load_spec_json() ── dict | None
```

## Archivos a Modificar

| Archivo | Cambio | REQs |
|---------|--------|------|
| `src/sdd_tui/core/reader.py` | Añadir `load_steering(openspec_path)` y `load_spec_json(change_path)` | REQ-S01..03, REQ-J01..04 |
| `src/sdd_tui/core/metrics.py` | Añadir `requirements` a `_ARTIFACT_FILES`; `_count_reqs` también lee `requirements.md` | REQ-R01..04 |
| `src/sdd_tui/tui/epics.py` | Añadir `Binding("s", "steering", "Steering")` + `action_steering()` | REQ-ST01..02 |
| `src/sdd_tui/tui/change_detail.py` | Añadir `Binding("q", "view_requirements", "Requirements")` + `action_view_requirements()` | REQ-RB01..02 |
| `src/sdd_tui/tui/spec_health.py` | Añadir `has_requirements`; actualizar `_artifacts_str` y `_add_row` | REQ-HQ01..02 |
| `tests/test_reader.py` | Tests para `load_steering` y `load_spec_json` | — |
| `tests/test_metrics.py` | Tests para requirements artifact y REQ counting desde requirements.md | — |

## Scope

- **Total archivos:** 7
- **Resultado:** Ideal (< 10)

## Detalle de Implementación

### `core/reader.py` — load_steering y load_spec_json

Funciones module-level (no métodos de `OpenspecReader`), sin estado:

```python
def load_steering(openspec_path: Path) -> str | None:
    path = openspec_path / "steering.md"
    if not path.exists():
        return None
    return path.read_text(errors="replace")


def load_spec_json(change_path: Path) -> dict | None:
    path = change_path / "spec.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(errors="replace"))
    except (json.JSONDecodeError, OSError):
        return None
```

### `core/metrics.py` — requirements artifact y REQ scan

Insertar `requirements` en `_ARTIFACT_FILES` entre `research` y `design`:

```python
_ARTIFACT_FILES = [
    ("proposal", "proposal.md"),
    ("spec", None),
    ("research", "research.md"),
    ("requirements", "requirements.md"),   # NUEVO
    ("design", "design.md"),
    ("tasks", "tasks.md"),
]
```

Actualizar `_count_reqs` para también escanear `requirements.md`:

```python
def _count_reqs(change_path: Path) -> tuple[int, int]:
    seen: set[str] = set()
    ears: set[str] = set()

    # scan specs/*/spec.md (comportamiento actual)
    specs_dir = change_path / "specs"
    if specs_dir.exists():
        for md_file in specs_dir.rglob("*.md"):
            _scan_req_lines(md_file, seen, ears)

    # scan requirements.md si existe (NUEVO)
    req_file = change_path / "requirements.md"
    if req_file.exists():
        _scan_req_lines(req_file, seen, ears)

    return len(seen), len(ears)


def _scan_req_lines(path: Path, seen: set[str], ears: set[str]) -> None:
    for line in path.read_text(errors="replace").splitlines():
        match = _REQ_PATTERN.search(line)
        if match:
            req_id = match.group(1)
            seen.add(req_id)
            if any(tag in line for tag in _EARS_TAGS):
                ears.add(req_id)
```

### `tui/epics.py` — binding s → steering

```python
BINDINGS = [
    Binding("r", "refresh", "Refresh"),
    Binding("a", "toggle_archived", "Archived"),
    Binding("s", "steering", "Steering"),   # NUEVO
    Binding("h", "health", "Health"),
    Binding("x", "decisions_timeline", "Decisions"),
    Binding("q", "quit", "Quit"),
]

def action_steering(self) -> None:
    from sdd_tui.tui.doc_viewer import DocumentViewerScreen
    steering_path = Path.cwd() / "openspec" / "steering.md"
    self.app.push_screen(DocumentViewerScreen(steering_path, "sdd-tui — steering"))
```

Nota: `DocumentViewerScreen` ya maneja el caso "archivo no encontrado" con
el mensaje `"steering.md not found"`, que cumple REQ-ST04.

### `tui/change_detail.py` — binding q → requirements

```python
BINDINGS = [
    ...
    Binding("q", "view_requirements", "Requirements"),  # NUEVO
]

def action_view_requirements(self) -> None:
    self._open_doc("requirements.md", "requirements")
```

### `tui/spec_health.py` — columna Q

```python
# En _populate():
has_research = any("research" in m.artifacts for m in all_metrics.values())
has_requirements = any("requirements" in m.artifacts for m in all_metrics.values())  # NUEVO

# _add_row recibe has_requirements:
self._add_row(table, change, all_metrics[change.name], has_research, has_requirements)

# _add_row firma actualizada:
def _add_row(self, table, change, metrics, has_research, has_requirements) -> None:
    ...
    artifacts_cell = Text(_artifacts_str(metrics.artifacts, has_research, has_requirements))

# _artifacts_str actualizado:
def _artifacts_str(artifacts, has_research, has_requirements) -> str:
    order = ["proposal", "spec"]
    if has_research:
        order.append("research")
    if has_requirements:
        order.append("requirements")
    order += ["design", "tasks"]
    ...
```

## Dependencias Técnicas

- Sin dependencias externas nuevas
- `json` (stdlib) — ya disponible
- `DocumentViewerScreen` ya maneja el caso "file not found" → no se necesita `SteeringScreen` nueva

## Patrones Aplicados

- **Module-level functions**: `load_steering` y `load_spec_json` siguen el patrón de `load()` y la filosofía del módulo — funciones puras sin estado
- **Reutilización de DocumentViewerScreen**: el viewer genérico ya maneja path + title + "not found" — no justifica nueva clase
- **`has_requirements` condicional**: mismo patrón que `has_research` en `spec_health.py`
- **`_scan_req_lines` helper**: extrae el bucle de scan para evitar duplicación

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `load_steering` como función module-level | Método de `OpenspecReader` | No tiene estado de clase; función pura más testeable |
| Reutilizar `DocumentViewerScreen` para steering | Nueva clase `SteeringScreen` | `DocumentViewerScreen` ya es genérico (path + title); sin comportamiento adicional en steering |
| `_scan_req_lines` helper extraído | Código inline duplicado | Evita duplicar el bucle de scan entre specs/ y requirements.md |
| `steering_path = Path.cwd() / "openspec"` | Recibir `openspec_path` como parámetro | Consistente con el patrón ya establecido en `action_decisions_timeline` |
| `has_requirements` como flag booleano | Siempre mostrar columna Q | Consistente con `has_research`; la columna aparece solo si es relevante |
| `import json` en `reader.py` | Módulo separado | stdlib, sin overhead; la función es simple |

## Tests Planificados

| Test | Archivo | Qué verifica |
|------|---------|-------------|
| `test_load_steering_exists` | `test_reader.py` | Retorna contenido cuando el archivo existe |
| `test_load_steering_missing` | `test_reader.py` | Retorna `None` cuando no existe |
| `test_load_spec_json_valid` | `test_reader.py` | Retorna dict cuando JSON válido |
| `test_load_spec_json_missing` | `test_reader.py` | Retorna `None` cuando no existe |
| `test_load_spec_json_malformed` | `test_reader.py` | Retorna `None` con JSON inválido |
| `test_requirements_artifact_detected` | `test_metrics.py` | `requirements` en artifacts cuando archivo existe |
| `test_requirements_artifact_absent` | `test_metrics.py` | `requirements` ausente cuando no hay archivo |
| `test_requirements_artifact_order` | `test_metrics.py` | Orden `[..., "research", "requirements", "design", ...]` |
| `test_reqs_counted_from_requirements_md` | `test_metrics.py` | REQs en requirements.md se suman a los de specs/ |
| `test_reqs_deduped_across_requirements_and_specs` | `test_metrics.py` | Mismo REQ en ambos archivos cuenta solo una vez |

## Notas de Implementación

- `EpicsView.action_steering` usa import inline para evitar circular imports
  (mismo patrón que otras acciones que importan screens al momento de uso)
- El binding `q` en `ChangeDetailScreen` no colisiona con `q` → quit en
  `EpicsView`: las screens de Textual tienen scope de bindings independiente
- `load_spec_json` captura tanto `json.JSONDecodeError` como `OSError`
  para robustez ante permisos o archivos corruptos
