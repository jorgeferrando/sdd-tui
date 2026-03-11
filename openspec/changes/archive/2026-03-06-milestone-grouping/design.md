# Design: milestone-grouping

## Metadata
- **Change:** milestone-grouping
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** draft

## Resumen Técnico

Dos piezas independientes: un nuevo módulo `core/milestones.py` con parser manual
de YAML (sin dependencias externas), y una extensión de `EpicsView._populate()` que
llama al parser y renderiza separadores de milestone cuando el archivo existe.

El patrón es idéntico al de `core/config.py`: state machine sobre líneas de texto,
degradación silenciosa ante errores, retrocompatibilidad garantizada por la ausencia
del archivo.

## Arquitectura

```
openspec/milestones.yaml
        │
        ▼
core/milestones.py
  load_milestones(openspec_path) -> list[Milestone]
  _parse_milestones(text) -> list[Milestone]
        │
        ▼
tui/epics.py — EpicsView._populate()
  if not is_multi and milestones:
    _populate_with_milestones(table, active, milestones)
  else:
    comportamiento actual
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/milestones.py` | Core module | Parser de milestones.yaml + dataclass Milestone |
| `tests/test_milestones.py` | Unit tests | Cobertura del parser: REQ-ML-01…05 |
| `tests/test_tui_epics_milestones.py` | TUI tests | Cobertura de EpicsView con milestones: REQ-MG-01…09 |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir rama milestone en `_populate()` | Agrupar changes por milestone en single-project |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal (< 10)

## Detalle de Implementación

### `core/milestones.py`

```python
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Milestone:
    name: str
    changes: list[str] = field(default_factory=list)


def load_milestones(openspec_path: Path) -> list[Milestone]:
    yaml_path = openspec_path / "milestones.yaml"
    if not yaml_path.exists():
        return []
    try:
        return _parse_milestones(yaml_path.read_text(errors="replace"))
    except Exception:
        return []


def _parse_milestones(text: str) -> list[Milestone]:
    """State machine parser. No PyYAML dependency."""
    milestones: list[Milestone] = []
    current_name: str | None = None
    current_changes: list[str] = []
    in_milestones = False
    in_changes = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "milestones:":
            in_milestones = True
            continue

        if not in_milestones:
            continue

        # New top-level key exits milestones block
        if stripped and not line.startswith(" "):
            break

        # New milestone: "  - name: ..."
        m = re.match(r"  - name:\s*(.+)", line)
        if m:
            if current_name is not None:
                milestones.append(Milestone(name=current_name, changes=current_changes))
            current_name = m.group(1).strip().strip("\"'")
            current_changes = []
            in_changes = False
            continue

        # Start of changes block: "    changes:"
        if re.match(r"    changes:", line):
            in_changes = True
            continue

        # Change entry: "      - change-name"
        if in_changes:
            m2 = re.match(r"\s{6}-\s+(.+)", line)
            if m2:
                current_changes.append(m2.group(1).strip())

    if current_name is not None:
        milestones.append(Milestone(name=current_name, changes=current_changes))

    return milestones
```

### `tui/epics.py` — cambios en `_populate()`

Añadir import de `load_milestones` y refactorizar la rama `not is_multi`:

```python
from sdd_tui.core.milestones import load_milestones

# En _populate(), dentro de `if not is_multi:`:
milestones = load_milestones(self.app._openspec_path)
if milestones:
    self._populate_by_milestone(table, active, milestones)
else:
    # comportamiento actual (lista plana con filtro)
    if self._search_query:
        active = self._filter_changes(active, self._search_query)
    for change in active:
        self._add_change_row(table, change)
```

Nuevo método privado `_populate_by_milestone`:

```python
def _populate_by_milestone(
    self, table: DataTable, active: list[Change], milestones: list[Milestone]
) -> None:
    assigned: set[str] = set()
    for milestone in milestones:
        # Resolver changes asignados a este milestone (solo activos existentes)
        milestone_changes = [
            c for c in active if c.name in milestone.changes
        ]
        if self._search_query:
            milestone_changes = self._filter_changes(milestone_changes, self._search_query)
        if not milestone_changes:
            continue  # REQ-MG-08: omitir milestone vacío con búsqueda
        table.add_row(f"── {milestone.name} ──", "", "", "", "", "", "", "")
        for change in milestone_changes:
            self._add_change_row(table, change)
            assigned.add(change.name)

    unassigned = [c for c in active if c.name not in assigned]
    if self._search_query:
        unassigned = self._filter_changes(unassigned, self._search_query)
    if unassigned:  # REQ-MG-07: ocultar si vacío
        table.add_row("── unassigned ──", "", "", "", "", "", "", "")
        for change in unassigned:
            self._add_change_row(table, change)
```

**Nota:** El orden de changes dentro de un milestone sigue el orden de `milestones.yaml`,
no el orden alfabético de la lista de changes. Para preservar el orden declarado:

```python
milestone_changes = [
    c for name in milestone.changes
    for c in active if c.name == name
]
```

## Patrones Aplicados

- **State machine parser**: idéntico a `core/config.py` — sin PyYAML, sin dependencias extra.
- **Degradación silenciosa**: `load_milestones()` siempre retorna `[]` en caso de error.
- **Retrocompatibilidad**: sin `milestones.yaml` → rama existente sin modificaciones.
- **Separation of concerns**: `_populate_by_milestone()` como método privado extraído — testable vía TUI test.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Parser manual (state machine) | PyYAML | Consistencia con `config.py`; sin deps extra |
| `_populate_by_milestone()` como método privado | Inline en `_populate()` | Legibilidad; método principal no crece |
| Orden por `milestones.yaml` dentro de milestone | Orden alfabético | El usuario controla el orden declarando en el YAML |
| `not is_multi` como condición de activación | Siempre activo | Multi-project tiene su propia lógica de separadores; mezclar añade complejidad sin valor en v1 |
| `load_milestones` llamado en `_populate()` | Llamado en `on_mount` | Permite editar YAML y refrescar con `r` sin reiniciar |

## Tests Planificados

### `tests/test_milestones.py` (unit — core)

| Test | Qué verifica |
|------|-------------|
| `test_load_milestones_no_file` | REQ-ML-02: retorna `[]` si no existe |
| `test_load_milestones_empty_file` | REQ-ML-02: retorna `[]` si vacío |
| `test_parse_milestones_basic` | REQ-ML-01: parsea 2 milestones con sus changes |
| `test_parse_milestones_single_milestone` | REQ-ML-01: un solo milestone |
| `test_parse_milestones_empty_changes` | REQ-ML-04: milestone sin changes → `changes=[]` |
| `test_parse_milestones_quoted_name` | REQ-ML-01: nombre con comillas dobles/simples |
| `test_parse_milestones_name_with_em_dash` | REQ-ML-01: nombre con `—` (unicode) |
| `test_load_milestones_malformed` | REQ-ML-03: retorna `[]` sin excepción |
| `test_parse_milestones_preserves_order` | REQ-ML-01: orden de milestones = orden en YAML |
| `test_parse_milestones_ignores_comments` | REQ-ML-05: parser ignora líneas `#` |

### `tests/test_tui_epics_milestones.py` (TUI — async)

| Test | Qué verifica |
|------|-------------|
| `test_milestone_grouping_adds_separator_rows` | REQ-MG-01: hay más filas que changes (separadores) |
| `test_milestone_grouping_separator_not_navigable` | REQ-MG-02: fila separadora no dispara nav |
| `test_unassigned_section_shows_for_missing_changes` | REQ-MG-03: `── unassigned ──` aparece |
| `test_no_unassigned_when_all_assigned` | REQ-MG-07: sin `── unassigned ──` si todos asignados |
| `test_no_milestone_grouping_without_yaml` | REQ-MG-04: sin YAML → lista plana |
| `test_no_milestone_grouping_in_multiproject` | REQ-MG-05: multi-project ignora milestones |
| `test_archived_not_grouped_by_milestone` | REQ-MG-06: archivados sin separador de milestone |
| `test_milestone_grouping_with_search_filter` | REQ-MG-08: búsqueda activa, milestone vacío omitido |
| `test_milestone_change_not_in_active_skipped` | REQ-MG-09: change en YAML pero no en activos → no fila vacía |

## Notas de Implementación

- `self.app._openspec_path` ya es el path correcto para single-project (lo usan `action_steering` y `action_decisions_timeline`).
- Los separadores de milestone usan la misma firma que los separadores existentes (8 columnas vacías) — sin cambios en `add_row` signature.
- No hay nueva binding de teclado necesaria — milestone grouping es automático al detectar el archivo.
