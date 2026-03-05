# Spec: TUI — Multi-project View 1

## Metadata
- **Dominio:** tui
- **Change:** observatory-v1
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** draft

## Contexto

Delta sobre la spec TUI existente. Extiende View 1 (EpicsView) para mostrar
changes de múltiples proyectos con separadores, y adapta SpecHealthScreen y
DecisionsTimeline para agregar datos de todos los proyectos.

---

## Requisitos (EARS)

### View 1 — Separadores de proyecto

- **REQ-01** `[Optional]` Where multi-project config is active, the `EpicsView` SHALL show changes grouped by project with a separator row per project.
- **REQ-02** `[Ubiquitous]` The system SHALL NOT show project separators in single-project (legacy) mode.
- **REQ-03** `[Event]` When the user presses `Enter` on any change (from any project), the app SHALL push `ChangeDetailScreen` with that change.
- **REQ-04** `[Event]` When the user presses `r`, the app SHALL reload all projects defined in config.
- **REQ-05** `[Unwanted]` If a project becomes unavailable after startup (path deleted), the system SHALL skip it silently during reload.

### SpecHealthScreen — Agregación multi-proyecto

- **REQ-06** `[Optional]` Where multi-project config is active, `SpecHealthScreen` SHALL show changes from all projects, grouped by project with separator rows.
- **REQ-07** `[Ubiquitous]` In single-project mode, `SpecHealthScreen` behavior SHALL be identical to the current spec.

### DecisionsTimeline — Agregación multi-proyecto

- **REQ-08** `[Optional]` Where multi-project config is active, `DecisionsTimeline` SHALL aggregate decisions from `archive/` of all configured projects.
- **REQ-09** `[Ubiquitous]` Decisions SHALL be ordered chronologically (ascending) across all projects combined.

---

## Comportamiento Actual (single-project)

View 1 muestra una tabla plana de changes del `cwd`. Sin separadores de proyecto.
SpecHealthScreen y DecisionsTimeline leen desde `cwd/openspec/`.

---

## Diseño de View 1 multi-proyecto

### Layout con separadores

```
─── sdd-tui ────────────────────────────────────────
  observatory-v1        ✓ · · · ·  [spec]
─── next ───────────────────────────────────────────
  di-464-parking        ✓ ✓ ✓ ✓ ·  [apply T03]
  di-471-rates          ✓ ✓ · · ·  [design]
─── front ──────────────────────────────────────────
  (no active changes)
```

- Los separadores son filas sin key → Enter no hace nada (igual que `── archived ──`).
- Si un proyecto no tiene changes activos → separador + fila `(no active changes)` sin key.

### `EpicsView` — Cambios internos

- `_projects: list[tuple[str, list[Change]]]` — resultado de `load_all_changes(config, cwd)`
- `_is_multi_project: bool` — `True` si `config.projects` no está vacío
- `_populate()` itera `_projects`: inserta fila separadora si `_is_multi_project`, luego inserta changes
- `_change_map: dict[str, Change]` — clave = `row_key.value` (sin cambio)
- Los separadores de proyecto y `(no active changes)` no tienen key → `_change_map.get()` devuelve `None`

### Compatibilidad con toggle `a` (archived)

- En modo multi-proyecto, el toggle `a` sigue mostrando/ocultando archivados de todos los proyectos.
- Los archivados se cargan con `load_changes(project_path / "openspec", project_path, include_archived=True)`.
- El separador `── archived ──` se mueve dentro de cada grupo de proyecto.

### Refresh (`r`) en modo multi-proyecto

**Dado** View 1 en modo multi-proyecto
**Cuando** el usuario pulsa `r`
**Entonces** se recargan los changes de todos los proyectos declarados en config,
se repobla el DataTable con los mismos separadores, y se emite notify
con el total de changes cargados sumando todos los proyectos.

---

## SpecHealthScreen — Separadores de proyecto

En modo multi-proyecto, la tabla añade separadores por proyecto antes de las filas de cada proyecto.
Formato igual al del separador de `── archived ──`: fila sin key.

```
─── sdd-tui ─────────────────────────────────────────────────────────
  observatory-v1   0  —    0/0    P . . .   —
─── next ────────────────────────────────────────────────────────────
  di-464-parking   5  80%  4/6    P S D T   2d
```

En modo single-project: sin separadores (comportamiento actual sin cambios).

---

## DecisionsTimeline — Multi-proyecto

`DecisionsTimeline` recibe `archive_dirs: list[Path]` en lugar de `archive_dir: Path`.
En single-project: `[cwd / "openspec" / "changes" / "archive"]` (sin cambio visible).
En multi-project: lista con el archive de cada proyecto configurado.

`collect_archived_decisions` se llama por cada `archive_dir` y los resultados se
fusionan ordenados por fecha.

---

## Fuera de Scope — `s` (steering)

El binding `s` (steering.md) en View 1 queda sin cambios en `observatory-v1`.
Sigue usando `self.app._openspec_path / "steering.md"` (single-project).
La extensión a multi-proyecto queda diferida a una versión futura.

---

## Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Config vacía (`projects: []`) | No se configura nada | Behavior idéntico al actual (sin separadores) |
| Un solo proyecto en config | Una entrada en `projects` | Separador de proyecto visible (con nombre) |
| Proyecto sin changes | Proyecto válido pero `openspec/changes/` vacío | Separador + `(no active changes)` |
| Proyecto desaparece en refresh | Path eliminado tras startup | Skip silencioso, notify "1 project unavailable" |

---

## Reglas de negocio

- **RB-MP01:** Los separadores de proyecto son filas sin key — Enter no navega.
- **RB-MP02:** En multi-proyecto, `_is_multi_project=True` determina si se renderizan separadores; no depende del número de changes encontrados.
- **RB-MP03:** El nombre en el separador = `project_path.name` (basename), no configurable.
- **RB-MP04:** `EpicsView` recibe `config: AppConfig` en `__init__` — no `cwd` directo.
- **RB-MP05:** En multi-proyecto, el notify de refresh indica el total: `"{n} changes loaded across {m} projects"`.
- **RB-MP06:** `SpecHealthScreen` recibe `changes: list[Change]` (ya aplanada con `project` field) — no necesita saber si es multi-proyecto; usa `change.project` para agrupar.
- **RB-MP07:** La fila `── archived ──` (toggle `a`) se añade dentro de cada grupo de proyecto, no al final global.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Separadores solo en multi-proyecto | Separador siempre (incluso en single) | Evita regresión visual en modo legacy |
| Fila `(no active changes)` por proyecto | Ocultar el separador si no hay changes | El usuario sabe que el proyecto existe pero está limpio |
| `DecisionsTimeline` recibe `list[Path]` | `list[Change]` (ya cargados) | DecisionsTimeline necesita el archive, no los changes activos |
| `s` (steering) fuera de scope | Extender a multi-proyecto en v1 | Requiere decisión sobre qué steering mostrar; no bloquea el valor de v1 |

## Abierto / Pendiente

- [ ] Definir comportamiento de `s` (steering) en multi-proyecto — diferido a v2.
