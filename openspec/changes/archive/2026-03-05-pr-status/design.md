# Design: pr-status — GitHub PR Status en PipelinePanel

## Metadata
- **Change:** pr-status
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Nuevo módulo `core/github.py` con función pura `get_pr_status(change_name, cwd)` que
invoca `gh pr list` via subprocess y retorna un `PrStatus` dataclass o `None`.
Patrón idéntico a `GitReader` — subprocess con captura, `FileNotFoundError` silenciado,
`returncode != 0` retorna `None`.

`PipelinePanel` añade un método `update_pr(pr_status)` que recalcula y actualiza su
contenido. `ChangeDetailScreen` lanza un worker `@work(thread=True)` en `on_mount`
que llama `get_pr_status` y actualiza el panel via `self.app.call_from_thread`.

## Arquitectura

```
ChangeDetailScreen.on_mount
  → PipelinePanel(pipeline, tasks, metrics)   ← construido con pr_status=LOADING
  → _load_pr_status_worker()  [@work(thread=True)]
      → get_pr_status(change.name, cwd)
          → subprocess: gh pr list --json ... --state all
          → parse JSON → PrStatus | None
      → self.app.call_from_thread(
            lambda s: s.query_one(PipelinePanel).update_pr(pr_status)
        )
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/github.py` | Módulo core | `PrStatus` dataclass + `get_pr_status` |
| `tests/test_github.py` | Tests unitarios | Cobertura de `get_pr_status` con subprocess mock |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/change_detail.py` | `PipelinePanel`: estado `LOADING`, `update_pr()`; `ChangeDetailScreen`: worker + import | Integra PR status en el panel |
| `tests/test_tui_change_detail.py` | Añadir casos: loading row, PR loaded, no PR | Cobertura de los nuevos comportamientos |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal (< 10)

## Detalles de Implementación

### `core/github.py`

```python
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PrStatus:
    number: int
    state: str          # "OPEN" | "MERGED" | "CLOSED"
    approvals: int
    changes_requested: int


def get_pr_status(change_name: str, cwd: Path) -> PrStatus | None:
    try:
        result = subprocess.run(
            [
                "gh", "pr", "list",
                "--json", "number,headRefName,state,reviews",
                "--state", "all",
                "--limit", "20",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None

    if result.returncode != 0:
        return None

    try:
        prs = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return None

    pr = next((p for p in prs if change_name in p.get("headRefName", "")), None)
    if pr is None:
        return None

    reviews = pr.get("reviews", [])
    approvals = sum(1 for r in reviews if r.get("state") == "APPROVED")
    changes_requested = sum(1 for r in reviews if r.get("state") == "CHANGES_REQUESTED")

    return PrStatus(
        number=pr["number"],
        state=pr["state"],
        approvals=approvals,
        changes_requested=changes_requested,
    )
```

### `PipelinePanel` — cambios

Constante de estado de carga:
```python
_PR_LOADING = "…"
_PR_NONE = "—"
_PR_STATE_SYMBOL = {"OPEN": "⧗", "MERGED": DONE, "CLOSED": "✗"}
```

Nuevo parámetro `pr_status` en `__init__` con valor centinela para "loading":
```python
_LOADING = object()  # sentinel

def __init__(self, pipeline, tasks, metrics=None, pr_status=_LOADING):
    ...
```

`_build_content` añade fila PR al final del contenido.

`update_pr(pr_status)` recalcula contenido y llama `self.update(new_content)`.

### `ChangeDetailScreen` — cambios

En `on_mount`:
```python
self._load_pr_status_worker()
```

Worker:
```python
@work(thread=True)
def _load_pr_status_worker(self) -> None:
    from sdd_tui.core.github import get_pr_status
    pr_status = get_pr_status(self._change.name, self._change.project_path)
    self.app.call_from_thread(
        lambda s=pr_status: self.query_one(PipelinePanel).update_pr(s)
    )
```

Import local de `get_pr_status` en el worker (patrón establecido en `app.py` para
evitar importaciones circulares y acelerar startup).

`action_refresh_view` no requiere cambios — los nuevos paneles se montan con estado
loading y lanzan el worker automáticamente via `on_mount` de `ChangeDetailScreen`.

**Nota:** `change.project_path` existe en `Change` desde `observatory-v1`. En modo
single-project es `Path.cwd()`.

## Patrones Aplicados

- **Subprocess con degradación silenciosa**: idéntico a `GitReader` — `FileNotFoundError` y `returncode != 0` retornan `None`.
- **Worker async `@work(thread=True)`**: sin `exclusive` (no interfiere con diff worker que sí usa `exclusive=True`).
- **`self.app.call_from_thread`**: patrón establecido — `Screen` no expone `call_from_thread` en Textual 8.x.
- **Import local en worker**: patrón de `app.py` para deps opcionales y evitar circulares.
- **Sentinel object para "loading"**: distingue "aún cargando" de `None` ("no hay PR") sin ensumar la API pública.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Función pura `get_pr_status` (no clase) | Clase `GitHubReader` como `GitReader` | Una sola función pública — clase innecesaria |
| Sentinel `_LOADING = object()` | Bool `loading: bool` en PipelinePanel | Encapsula el estado en el parámetro; PipelinePanel sigue siendo un `Static` simple |
| Import local de `get_pr_status` en worker | Import de módulo global | Patrón establecido en el proyecto para deps opcionales |
| `--limit 20` en `gh pr list` | Sin límite | Evita output masivo; 20 PRs recientes son suficientes |
| `--state all` | Solo `--state open` | Permite mostrar MERGED/CLOSED del change ya mergeado |

## Tests Planificados

### `tests/test_github.py` (nuevo)

| Test | Qué verifica |
|------|-------------|
| `test_get_pr_status_returns_none_when_gh_missing` | `FileNotFoundError` → `None` |
| `test_get_pr_status_returns_none_on_nonzero_exit` | `returncode=1` → `None` |
| `test_get_pr_status_returns_none_when_no_pr_found` | Lista vacía o sin match → `None` |
| `test_get_pr_status_returns_pr_status_on_match` | Match por `headRefName` → `PrStatus` correcto |
| `test_get_pr_status_counts_approvals_and_changes_requested` | Reviews mixtos → conteo correcto |
| `test_get_pr_status_returns_none_on_invalid_json` | JSON inválido → `None` |
| `test_get_pr_status_matches_substring_in_branch_name` | `feature/pr-status` contiene `pr-status` → match |

### `tests/test_tui_change_detail.py` (ampliación)

| Test | Qué verifica |
|------|-------------|
| `test_pipeline_panel_shows_loading_pr_row` | `PipelinePanel` con sentinel muestra `…  PR` |
| `test_pipeline_panel_shows_pr_none_row` | `update_pr(None)` muestra `—  PR` |
| `test_pipeline_panel_shows_open_pr` | `update_pr(PrStatus(42, "OPEN", 0, 0))` muestra `⧗  PR #42` |
| `test_pipeline_panel_shows_review_counts` | `update_pr(PrStatus(42, "OPEN", 2, 1))` muestra `2✓ 1✗` |
| `test_pipeline_panel_omits_zero_counts` | approvals=0, changes_requested=1 → solo `1✗` |

Total tests estimados: 138 + 12 = **~150 tests**

## Notas de Implementación

- `gh pr list` con `--json` requiere que el usuario esté autenticado con `gh auth login`.
  Si no está autenticado, `returncode != 0` — se maneja con degradación silenciosa.
- El campo `reviews` en el JSON de `gh` incluye todas las reviews, no solo la más reciente
  por reviewer. Para este scope es aceptable (conteo total, no de reviewers únicos).
- `change.project_path` puede ser `Path.cwd()` en modo single-project — correcto para
  que `gh` detecte el repo de GitHub desde el directorio de trabajo.
