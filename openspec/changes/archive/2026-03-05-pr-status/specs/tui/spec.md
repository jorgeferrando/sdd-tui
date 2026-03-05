# Spec: pr-status — GitHub PR Status en PipelinePanel

## Metadata
- **Dominio:** tui
- **Change:** pr-status
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** draft

## Contexto

Delta sobre el spec canónico `tui/spec.md` v1.6 (sección 2 — View 2 Pipeline sidebar).

Extiende `PipelinePanel` con una fila extra que muestra el estado del PR de GitHub
asociado al change actual. La información se obtiene via `gh` CLI y se carga de
forma asíncrona para no bloquear la apertura de View 2.

---

## 1. Modelo de datos — `PrStatus`

### `core/github.py` — nuevo módulo

```python
@dataclass
class PrStatus:
    number: int
    state: str           # "OPEN" | "MERGED" | "CLOSED"
    approvals: int
    changes_requested: int
```

### `get_pr_status(change_name, cwd) -> PrStatus | None`

Ejecuta:
```
gh pr list --json number,title,headRefName,state,reviews \
           --state all --limit 20
```

Filtra por `headRefName` que contenga `change_name`.

Procesa `reviews`:
- `approvals` = reviews con `state == "APPROVED"`
- `changes_requested` = reviews con `state == "CHANGES_REQUESTED"`

Retorna `None` en cualquiera de estos casos:
- `gh` no está disponible (FileNotFoundError)
- El comando falla (returncode != 0)
- No hay PR con `headRefName` que contenga `change_name`
- Output JSON inválido

No lanza excepciones — degradación silenciosa total.

---

## 2. PipelinePanel — fila PR

### Extensión del layout

Cuando `PrStatus` está disponible, se añade una fila extra al final del panel:

```
  PIPELINE

  ✓  propose
  ✓  spec
  ✓  design
  ✓  tasks
  ✓  apply
  ✓  verify

  ⧗  PR #1234  2✓ 1✗
```

Cuando `PrStatus` es `None` (sin PR o `gh` no disponible):
```
  —  PR
```

### Símbolos de estado

| `PrStatus.state` | Símbolo |
|------------------|---------|
| `"OPEN"`         | `⧗`     |
| `"MERGED"`       | `✓`     |
| `"CLOSED"`       | `✗`     |
| `None` (sin PR)  | `—`     |

### Formato del conteo de reviews

Solo se muestra si `PrStatus` no es `None`:
- `{approvals}✓` solo si `approvals > 0`
- `{changes_requested}✗` solo si `changes_requested > 0`
- Sin conteo si ambos son 0

Ejemplos:
- `2✓ 1✗` → 2 approvals, 1 changes requested
- `3✓` → 3 approvals, 0 changes requested
- `1✗` → 0 approvals, 1 changes requested
- `⧗  PR #42` → PR abierto sin reviews

### Estado de carga

Mientras el worker asíncrono no ha respondido:
```
  …  PR
```

---

## 3. Carga asíncrona en ChangeDetailScreen

### Worker `_load_pr_status_worker`

- Decorado con `@work(thread=True)` (no `exclusive` — no interfiere con diff worker)
- Llamado en `on_mount` de `ChangeDetailScreen`
- Al completar, llama `self.app.call_from_thread(_update_pr_row, pr_status)`

### Flujo

```
on_mount
  → PipelinePanel construido con pr_status=None (muestra "… PR")
  → _load_pr_status_worker lanzado
    → get_pr_status(change.name, cwd)
    → call_from_thread(_update_pr_row, result)
      → PipelinePanel.update_pr(pr_status)
```

### `PipelinePanel.update_pr(pr_status: PrStatus | None) -> None`

Método público que recalcula el contenido del panel y llama `self.update(new_content)`.

---

## 4. Refresh (`r`) — recarga de PR status

**Dado** View 2 con PR status cargado
**Cuando** el usuario pulsa `r`
**Entonces:**
- Los paneles se reconstruyen (comportamiento existente)
- El nuevo `PipelinePanel` muestra `… PR` mientras recarga
- `_load_pr_status_worker` se lanza de nuevo

El worker se lanza automáticamente al montar los nuevos paneles — no requiere
lógica extra en `action_refresh_view`.

---

## 5. Comportamientos esperados (EARS)

- **REQ-PR01** `[Event]` When View 2 mounts, the system SHALL launch a background worker to fetch the PR status for the current change.
- **REQ-PR02** `[State]` While the PR worker is running, the PipelinePanel SHALL show `…  PR` as the PR row.
- **REQ-PR03** `[Event]` When the PR worker completes with a result, the PipelinePanel SHALL update the PR row with the state symbol, number, and review counts.
- **REQ-PR04** `[Event]` When the PR worker completes with no result (no PR or `gh` unavailable), the PipelinePanel SHALL show `—  PR`.
- **REQ-PR05** `[Unwanted]` If `gh` CLI is unavailable, `get_pr_status` SHALL return `None` without raising.
- **REQ-PR06** `[Unwanted]` If `gh` returns non-zero exit code, `get_pr_status` SHALL return `None` without raising.
- **REQ-PR07** `[Event]` When the user presses `r`, the PR status SHALL reload (new worker launched with fresh panels).
- **REQ-PR08** `[Ubiquitous]` The review count SHALL only show non-zero values (approvals and/or changes_requested).

---

## 6. Reglas de negocio

- **RB-PR01:** `get_pr_status` es puro — sin efectos secundarios, sin estado global.
- **RB-PR02:** El worker usa `@work(thread=True)` sin `exclusive` — puede coexistir con el diff worker.
- **RB-PR03:** `self.app.call_from_thread` (no `self.call_from_thread`) — patrón establecido en el proyecto.
- **RB-PR04:** `PipelinePanel` sigue siendo un `Static` — `update_pr` llama `self.update(content)`.
- **RB-PR05:** El estado de carga inicial (`… PR`) se construye en `__init__` de `PipelinePanel`, no depende del worker.
- **RB-PR06:** La columna de reviews omite `0✓` y `0✗` — solo valores > 0.
- **RB-PR07:** `get_pr_status` filtra por `headRefName contains change_name` (substring, no exact match) — la rama puede tener prefijo como `feature/change-name`.
- **RB-PR08:** `gh pr list --state all` incluye PRs MERGED y CLOSED — necesario para mostrar el estado final.

---

## Casos alternativos

| Escenario | Resultado |
|-----------|-----------|
| `gh` no instalado | `get_pr_status` → `None` → fila `—  PR` |
| PR no encontrado | `get_pr_status` → `None` → fila `—  PR` |
| PR abierto sin reviews | `⧗  PR #42` (sin conteo) |
| PR mergeado con approvals | `✓  PR #42  3✓` |
| PR cerrado con changes requested | `✗  PR #42  1✗` |
| Error de red / timeout | `get_pr_status` → `None` → fila `—  PR` |
| JSON inválido en respuesta `gh` | `get_pr_status` → `None` → fila `—  PR` |

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `src/sdd_tui/core/github.py` | Nuevo: `PrStatus`, `get_pr_status` |
| `src/sdd_tui/tui/change_detail.py` | `PipelinePanel.update_pr`, worker en `ChangeDetailScreen` |
| `tests/test_github.py` | Nuevo: tests unitarios `get_pr_status` con subprocess mock |
| `tests/test_tui_change_detail.py` | Casos con PR status (loading, loaded, no PR) |

---

## Fuera de scope

- Binding `P` para abrir PR en browser (diferido a v2)
- Polling periódico (la recarga manual con `r` es suficiente)
- Soporte multi-proyecto en la resolución del PR (usar `change_name` como proxy es suficiente)
