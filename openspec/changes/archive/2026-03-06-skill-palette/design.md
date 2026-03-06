# Design: skill-palette

## Metadata
- **Change:** skill-palette
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-06
- **Estado:** approved

## Resumen Técnico

Dos piezas independientes: un lector puro (`core/skills.py`) que escanea
`~/.claude/skills/` y un Screen TUI (`tui/skill_palette.py`) que consume
ese lector para mostrar una paleta de comandos con filtrado y copia al
portapapeles.

El filtro reutiliza exactamente el patrón de `EpicsView` (`Input` oculto,
`/` activa, Esc limpia). El comando copiado es context-aware cuando la
pantalla se abre desde `ChangeDetailScreen` (`K`).

## Arquitectura

```
~/.claude/skills/
    sdd-apply/SKILL.md  (front matter: name + description)
    sdd-new/SKILL.md
    build/SKILL.md
    …
           │
           ▼
    core/skills.py
    ─────────────
    load_skills(skills_dir) → list[SkillInfo]
    _parse_front_matter(text) → dict[str, str]
           │
           ▼
    tui/skill_palette.py
    ────────────────────
    SkillPaletteScreen(change_name=None)
      ├── DataTable (command / description)
      ├── Input (filtrado, oculto por defecto)
      └── _build_command(skill_name, change_name) → str
           │
    ┌──────┴──────────────────────────┐
    │                                 │
tui/epics.py                 tui/change_detail.py
K → SkillPaletteScreen()     K → SkillPaletteScreen(change.name)

tui/app.py
ctrl+p → SkillPaletteScreen()  (priority=True)
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/skills.py` | Module | `SkillInfo` + `load_skills()` |
| `src/sdd_tui/tui/skill_palette.py` | Screen | `SkillPaletteScreen` |
| `tests/test_skills.py` | Unit tests | Cobertura de `load_skills()` |
| `tests/test_tui_skill_palette.py` | TUI tests | Cobertura de `SkillPaletteScreen` |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/epics.py` | Añadir `Binding("K", ...)` + `action_skill_palette` | Acceso desde View 1 |
| `src/sdd_tui/tui/change_detail.py` | Añadir `Binding("K", ...)` + `action_skill_palette` | Acceso desde View 2 con contexto |
| `src/sdd_tui/tui/app.py` | Añadir `Binding("ctrl+p", ...)` + `action_skill_palette` | Acceso global |
| `src/sdd_tui/tui/help.py` | Documentar `K` y `ctrl+p` | Consistencia con HelpScreen |

## Scope

- **Total archivos:** 8 (4 nuevos + 4 modificados)
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Sin dependencias nuevas — `re`, `pathlib`, `dataclasses` (stdlib)
- `copy_to_clipboard` nativo de Textual (≥ 0.70.0) — ya usado en View 5
- No requiere migración ni cambios de schema

## Detalle de Implementación

### `core/skills.py`

```python
@dataclass
class SkillInfo:
    name: str
    description: str

# Whitelist de skills que aceptan {change_name} como argumento
_CONTEXT_AWARE: frozenset[str] = frozenset({
    "sdd-apply", "sdd-verify", "sdd-archive", "sdd-spec",
    "sdd-design", "sdd-tasks", "sdd-continue", "sdd-steer", "sdd-audit",
})

def load_skills(skills_dir: Path) -> list[SkillInfo]:
    """Escanea skills_dir, retorna list[SkillInfo] SDD-first, alfabético."""

def _parse_front_matter(text: str) -> dict[str, str]:
    """Extrae key: value del bloque --- YAML del inicio del archivo."""
```

Front matter parsing: regex sobre líneas entre los dos `---` (patrón
consistente con `config.py` — sin dependencia de PyYAML).

Orden: primero `sdd-*` ordenados, luego el resto ordenados.

### `tui/skill_palette.py`

```python
_CONTEXT_AWARE = frozenset(...)  # misma definición que en core/skills.py — o importar

class SkillPaletteScreen(Screen):
    def __init__(self, change_name: str | None = None) -> None: ...

    # Patrón de filtro idéntico a EpicsView:
    #   _search_mode: bool, _search_query: str
    #   Input id="search-input", display: none por defecto
    #   on_key: Esc limpia filtro si activo, pop_screen si no
    #   on_input_changed: re-populate
    #   action_search: activa Input
    #   action_cancel_search: limpia y devuelve foco al DataTable

    def _populate(self) -> None:
        """Puebla DataTable aplicando _search_query si hay filtro."""

    def _build_command(self, skill_name: str) -> str:
        """Retorna '/skill-name [change_name]' según context-aware."""
        if self._change_name and skill_name in _CONTEXT_AWARE:
            return f"/{skill_name} {self._change_name}"
        return f"/{skill_name}"

    def on_data_table_row_selected(self, event: ...) -> None:
        """Enter: copy to clipboard + notify."""
```

DataTable: `cursor_type="row"`, `show_header=True`, columnas `COMMAND` + `DESCRIPTION`.

Highlight de filtro: `bold cyan` (patrón EpicsView).

Row key = `skill.name` para lookup en `on_data_table_row_selected`.

### `tui/epics.py`

```python
Binding("K", "skill_palette", "Skills")

def action_skill_palette(self) -> None:
    from sdd_tui.tui.skill_palette import SkillPaletteScreen
    self.app.push_screen(SkillPaletteScreen())
```

### `tui/change_detail.py`

```python
Binding("K", "skill_palette", "Skills")

def action_skill_palette(self) -> None:
    from sdd_tui.tui.skill_palette import SkillPaletteScreen
    self.app.push_screen(SkillPaletteScreen(change_name=self._change.name))
```

### `tui/app.py`

```python
Binding("ctrl+p", "skill_palette", "Skills", priority=True)

def action_skill_palette(self) -> None:
    from sdd_tui.tui.skill_palette import SkillPaletteScreen
    self.push_screen(SkillPaletteScreen())
```

### `tui/help.py`

Añadir en sección `VIEW 1`:
```
row("K", "Skill palette")
```

Añadir en sección `VIEW 2`:
```
row("K", "Skill palette (with change context)")
```

Añadir en sección `GLOBAL`:
```
row("ctrl+p", "Skill palette")
```

## Patrones Aplicados

- **Filtro con Input oculto:** mismo patrón que `EpicsView` — `_search_mode`, `_search_query`, Input `display: none`, `/` activa, Esc doble (limpiar → pop)
- **Import lazy en actions:** `from sdd_tui.tui.X import X` dentro del método — patrón ya usado en `app.py` (HelpScreen, ErrorScreen)
- **Screen parametrizado:** `SkillPaletteScreen(change_name=None)` — patrón de `ChangeDetailScreen(change)`
- **Front matter regex:** sin PyYAML — patrón de `config.py`

## Tests Planificados

### `tests/test_skills.py` (unit)

| Test | Qué verifica |
|------|-------------|
| `test_load_skills_returns_empty_when_dir_missing` | `[]` si el dir no existe |
| `test_load_skills_skips_entry_without_skill_md` | subdir sin SKILL.md ignorado |
| `test_load_skills_skips_invalid_front_matter` | SKILL.md sin `---` ignorado |
| `test_load_skills_skips_missing_fields` | SKILL.md con `name` pero sin `description` ignorado |
| `test_load_skills_returns_skill_info` | parsea correctamente name + description |
| `test_load_skills_sdd_first_order` | sdd-* antes que non-sdd, cada grupo alfabético |
| `test_load_skills_multiple_sdd_sorted` | varios sdd-* en orden alfabético entre sí |
| `test_context_aware_set_contains_expected` | verifica que `_CONTEXT_AWARE` tiene los skills esperados |

### `tests/test_tui_skill_palette.py` (TUI)

| Test | Qué verifica |
|------|-------------|
| `test_skill_palette_mounts_without_crash` | pantalla monta sin error |
| `test_skill_palette_shows_no_skills_when_empty` | sin skills → "No skills found" |
| `test_skill_palette_populates_table` | con skills → filas en DataTable |
| `test_enter_copies_command_without_context` | Enter sin change_name → `/skill-name` |
| `test_enter_copies_command_with_context_aware` | Enter con change_name y skill context-aware → `/skill apply my-feature` |
| `test_enter_copies_command_with_non_context_aware` | Enter con change_name y skill no context-aware → `/sdd-new` (sin change) |
| `test_filter_reduces_rows` | filtro activo reduce filas visibles |
| `test_esc_clears_filter_before_pop` | primer Esc limpia filtro, no cierra pantalla |

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `_CONTEXT_AWARE` definido en `core/skills.py` | Definido en `tui/skill_palette.py` | Testable en unit tests del core sin TUI |
| Import lazy en actions | Import en top-level | Patrón ya establecido en el proyecto; evita dependencias circulares |
| `show_header=True` en DataTable | Sin header | Dos columnas de naturaleza distinta — el header clarifica |
| Reutilizar patrón de filtro de EpicsView tal cual | Refactor a mixin/helper | La duplicación es pequeña (< 20 líneas); YAGNI — no hay 3er uso todavía |

## Notas de Implementación

- El `V` binding de EpicsView es uppercase → `K` también debe ser uppercase para consistencia con `H`, `X`, `V`, `L` (screens secundarios en View 1)
- En `ChangeDetailScreen`, el binding `K` (uppercase) no colisiona con ninguno existente
- `ctrl+p` en App con `priority=True` garantiza que capture desde cualquier pantalla, incluso si hay un widget activo con foco
- `_CONTEXT_AWARE` es un `frozenset` para lookups O(1) y para que sea importable por los tests sin instanciar la pantalla
