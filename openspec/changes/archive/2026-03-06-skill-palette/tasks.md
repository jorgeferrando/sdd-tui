# Tasks: Skill Palette

## Metadata
- **Change:** skill-palette
- **Jira:** —
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Crear `src/sdd_tui/core/skills.py` — `SkillInfo`, `load_skills()`, `_CONTEXT_AWARE`
  - Commit: `[skill-palette] Add skills reader with SkillInfo and load_skills`

- [x] **T02** Crear `tests/test_skills.py` — unit tests para `load_skills()`
  - Commit: `[skill-palette] Add unit tests for skills reader`
  - Depende de: T01

- [x] **T03** Crear `src/sdd_tui/tui/skill_palette.py` — `SkillPaletteScreen` con filtro y clipboard
  - Commit: `[skill-palette] Add SkillPaletteScreen with filter and clipboard copy`
  - Depende de: T01

- [x] **T04** Modificar `src/sdd_tui/tui/epics.py` — binding `K` → `SkillPaletteScreen` sin contexto
  - Commit: `[skill-palette] Add K binding to EpicsView for skill palette`
  - Depende de: T03

- [x] **T05** Modificar `src/sdd_tui/tui/change_detail.py` — binding `K` → `SkillPaletteScreen` con change context
  - Commit: `[skill-palette] Add K binding to ChangeDetailScreen with change context`
  - Depende de: T03

- [x] **T06** Modificar `src/sdd_tui/tui/app.py` — binding global `ctrl+p` → `SkillPaletteScreen`
  - Commit: `[skill-palette] Add global ctrl+p binding for skill palette`
  - Depende de: T03

- [x] **T07** Modificar `src/sdd_tui/tui/help.py` — documentar `K` y `ctrl+p` en HelpScreen
  - Commit: `[skill-palette] Document K and ctrl+p bindings in HelpScreen`
  - Depende de: T04, T05, T06

- [x] **T08** Crear `tests/test_tui_skill_palette.py` — TUI tests para `SkillPaletteScreen`
  - Commit: `[skill-palette] Add TUI tests for SkillPaletteScreen`
  - Depende de: T03

## Quality Gate Final

- [x] **QG** Ejecutar suite completa de tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest tests/ -q`

## Notas

- T01 → T02 → TDD: tests primero (RED), luego ajustar si falla algo
- T03 depende de T01 (`_CONTEXT_AWARE` se importa desde `core/skills.py`)
- T04, T05, T06 son independientes entre sí — pueden hacerse en cualquier orden tras T03
- T07 va al final para documentar todos los bindings de una vez
- T08 puede ir tras T03 sin esperar T04-T06
