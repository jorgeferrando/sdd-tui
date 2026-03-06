# Proposal: skill-palette

## Descripción

Pantalla de skills disponibles con escaneo dinámico de `~/.claude/skills/` y copia al portapapeles del comando de invocación. Accesible desde View 1 (EpicsView) y View 2 (ChangeDetailScreen), con paleta de comandos global.

## Motivación

El flujo SDD tiene ~15 comandos (`/sdd-new`, `/sdd-apply`, `/sdd-verify`, etc.) que el usuario debe recordar. No hay ningún lugar dentro del TUI donde ver qué skills están disponibles, qué hacen, y cómo invocarlos. La HelpScreen cubre keybindings del TUI pero no los comandos Claude.

El usuario tiene que salir del TUI, buscar en README o memory, y copiar manualmente. Esta fricción interrumpe el flujo.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|-------------|-------------------|
| Lista estática en HelpScreen | Se queda obsoleta cuando se añaden/eliminan skills |
| Config YAML con skill names | Requiere mantenimiento manual — el directorio ya es la fuente de verdad |
| Ampliar HelpScreen existente | Mezcla keybindings TUI con comandos Claude — conceptos distintos |

## Solución propuesta

### Componentes

**1. `core/skills.py`** — lector de skills
- Escanea `~/.claude/skills/` (o path configurable)
- Parsea YAML front matter de `SKILL.md`: extrae `name` y `description`
- Devuelve `list[SkillInfo]` ordenada — SDD skills primero, resto alfabético

**2. `tui/skill_palette.py`** — pantalla TUI
- `SkillPaletteScreen(Screen)`: DataTable con columnas `command` + `description`
- Enter en una fila → copia `/skill-name` al portapapeles + notify
- Filtrado incremental con `/` (patrón de EpicsView)
- Esc → vuelve a la pantalla anterior

**3. Integración de bindings**
- EpicsView: `K` → `SkillPaletteScreen` (sin contexto de change)
- ChangeDetailScreen: `K` → `SkillPaletteScreen` (con change en contexto — copy incluye change name si el skill lo admite)
- App global: `ctrl+p` → `SkillPaletteScreen` desde cualquier pantalla

### Comportamiento de copia

| Skill | Sin contexto (View 1) | Con contexto (View 2, change: `my-feature`) |
|-------|----------------------|---------------------------------------------|
| `sdd-new` | `/sdd-new` | `/sdd-new` |
| `sdd-apply` | `/sdd-apply` | `/sdd-apply my-feature` |
| `sdd-verify` | `/sdd-verify` | `/sdd-verify my-feature` |
| `sdd-archive` | `/sdd-archive` | `/sdd-archive my-feature` |
| `build` | `/build` | `/build` |

Los skills con argumento `{change-name}` se identifican por prefijo `sdd-` (excepto `sdd-new`, `sdd-explore`, `sdd-ff`).

## Impacto

| Area | Archivo |
|------|---------|
| core | `core/skills.py` (nuevo) |
| tui | `tui/skill_palette.py` (nuevo) |
| tui | `tui/epics.py` (binding K) |
| tui | `tui/change_detail.py` (binding K) |
| tui | `tui/app.py` (binding ctrl+p global) |
| tui | `tui/help.py` (documentar nuevos bindings) |
| tests | `tests/test_skills.py` (nuevo) |
| tests | `tests/test_tui_skill_palette.py` (nuevo) |

## Criterios de éxito

- [ ] Skills listados correctamente desde `~/.claude/skills/`
- [ ] Enter copia el comando al portapapeles + notify
- [ ] Filtrado `/` funciona en tiempo real
- [ ] Binding `K` en View 1 y View 2
- [ ] Binding global `ctrl+p` desde cualquier pantalla
- [ ] Si `~/.claude/skills/` no existe → mensaje vacío, sin crash
- [ ] Tests unitarios para `core/skills.py`
- [ ] Tests TUI para `SkillPaletteScreen`
