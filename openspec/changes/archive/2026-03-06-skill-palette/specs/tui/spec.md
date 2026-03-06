# Spec: TUI — SkillPaletteScreen (View 10)

## Metadata
- **Dominio:** tui
- **Change:** skill-palette
- **Fecha:** 2026-03-06
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Delta sobre la spec canónica `tui`. Añade `SkillPaletteScreen` — una paleta
de comandos que lista los skills de `~/.claude/skills/` con filtrado y copia
al portapapeles del comando de invocación.

---

## 10. SkillPaletteScreen (View 10)

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — Skill Palette                                      │
├─────────────────────────────────────────────────────────────┤
│ [/] filter...                                                │
├───────────────────┬─────────────────────────────────────────┤
│ COMMAND           │ DESCRIPTION                             │
├───────────────────┼─────────────────────────────────────────┤
│ /sdd-apply        │ SDD Apply - Implementación del cambio…  │
│ /sdd-archive      │ SDD Archive - Cierre del cambio…        │
│ /sdd-continue     │ SDD Continue - Detecta la siguiente…    │
│ …                 │ …                                       │
│ /build            │ Vertical BUILD - Code implementation…   │
│ /docker           │ Docker management skill…                │
├─────────────────────────────────────────────────────────────┤
│ [Enter] copy command   [/] filter   [Esc] back              │
└─────────────────────────────────────────────────────────────┘
```

### Requisitos (EARS)

- **REQ-01** `[Event]` When `SkillPaletteScreen` se monta, the screen SHALL cargar los skills via `load_skills(Path.home() / ".claude" / "skills")` y poblar el `DataTable`.
- **REQ-02** `[Event]` When no hay skills disponibles (directorio vacío o inexistente), the screen SHALL mostrar `No skills found` en lugar del DataTable.
- **REQ-03** `[Event]` When el usuario pulsa Enter sobre una fila, the screen SHALL copiar el comando al portapapeles con `app.copy_to_clipboard` y mostrar `notify("Copied: {cmd}")`.
- **REQ-04** `[Event]` When el usuario pulsa `/`, the screen SHALL activar el `Input` de filtrado y mover el foco a él.
- **REQ-05** `[Event]` When el texto del `Input` cambia, the screen SHALL filtrar las filas del DataTable mostrando solo las que contienen el texto (case-insensitive) en `command` o `description`.
- **REQ-06** `[Event]` When el filtro está activo y el usuario pulsa Esc, the screen SHALL limpiar el filtro y devolver el foco al DataTable.
- **REQ-07** `[Event]` When el filtro está vacío y el usuario pulsa Esc, the screen SHALL hacer `pop_screen` (volver a la pantalla anterior).
- **REQ-08** `[Ubiquitous]` The DataTable SHALL tener `cursor_type="row"` y mostrar dos columnas: `command` (prefijado con `/`) y `description`.
- **REQ-09** `[Ubiquitous]` The screen SHALL respetar el orden SDD-first definido por `load_skills`.

### Comando copiado — lógica context-aware

El comando copiado depende de si la pantalla fue abierta con contexto de change o sin él.

#### Sin contexto (desde EpicsView con `K` o desde cualquier pantalla con `ctrl+p`)

Siempre se copia `/{skill-name}` sin argumentos.

#### Con contexto (desde ChangeDetailScreen con `K`, `change_name` disponible)

| Skill | Comando copiado |
|-------|----------------|
| `sdd-apply` | `/sdd-apply {change_name}` |
| `sdd-verify` | `/sdd-verify {change_name}` |
| `sdd-archive` | `/sdd-archive {change_name}` |
| `sdd-spec` | `/sdd-spec {change_name}` |
| `sdd-design` | `/sdd-design {change_name}` |
| `sdd-tasks` | `/sdd-tasks {change_name}` |
| `sdd-continue` | `/sdd-continue {change_name}` |
| `sdd-steer` | `/sdd-steer {change_name}` |
| `sdd-audit` | `/sdd-audit {change_name}` |
| resto (`sdd-new`, `sdd-explore`, `sdd-ff`, `sdd-init`, `sdd-propose`, y todos los non-sdd) | `/{skill-name}` (sin change) |

Regla: skills con prefijo `sdd-` aceptan `{change_name}` **excepto**: `sdd-new`, `sdd-explore`, `sdd-ff`, `sdd-init`, `sdd-propose`.

**REQ-10** `[Event]` When hay `change_name` en contexto y el skill está en el conjunto "context-aware", the screen SHALL copiar `/{skill-name} {change_name}`.
**REQ-11** `[Event]` When el skill no es context-aware o no hay contexto, the screen SHALL copiar `/{skill-name}` sin argumentos.

### Integración de bindings

- **REQ-12** `[Event]` When el usuario pulsa `K` en EpicsView, the app SHALL abrir `SkillPaletteScreen` sin contexto de change.
- **REQ-13** `[Event]` When el usuario pulsa `K` en ChangeDetailScreen, the app SHALL abrir `SkillPaletteScreen` con el `change_name` del change activo.
- **REQ-14** `[Event]` When el usuario pulsa `ctrl+p` desde cualquier pantalla, the app SHALL abrir `SkillPaletteScreen` sin contexto de change.
- **REQ-15** `[Event]` When `SkillPaletteScreen` se cierra con Esc, the app SHALL volver a la pantalla anterior (sin efecto secundario en el estado de la pantalla previa).

### HelpScreen

- **REQ-16** `[Event]` When se abre HelpScreen, the screen SHALL incluir los bindings `K` y `ctrl+p` en la sección de navegación global.

### Escenarios de verificación

**REQ-03 + REQ-10** — copia con contexto
**Dado** `SkillPaletteScreen` abierta desde ChangeDetailScreen con `change_name="my-feature"`
**Cuando** el cursor está en la fila `sdd-apply` y el usuario pulsa Enter
**Entonces** se copia `/sdd-apply my-feature` y aparece `notify("Copied: /sdd-apply my-feature")`

**REQ-03 + REQ-11** — copia sin contexto
**Dado** `SkillPaletteScreen` abierta desde EpicsView (sin contexto)
**Cuando** el cursor está en la fila `sdd-apply` y el usuario pulsa Enter
**Entonces** se copia `/sdd-apply` (sin change name)

**REQ-05** — filtrado
**Dado** `SkillPaletteScreen` con 10 skills listados
**Cuando** el usuario activa `/` y escribe `"apply"`
**Entonces** solo aparecen filas cuyo command o description contiene "apply" (case-insensitive)

**REQ-06 → REQ-07** — Esc doble
**Dado** filtro activo con texto `"sdd"`
**Cuando** el usuario pulsa Esc
**Entonces** el filtro se limpia y el foco vuelve al DataTable (pantalla NO se cierra)
**Cuando** el usuario pulsa Esc de nuevo
**Entonces** `pop_screen` — vuelve a la pantalla anterior

**REQ-02** — sin skills
**Dado** `~/.claude/skills/` no existe
**Cuando** se monta `SkillPaletteScreen`
**Entonces** se muestra `No skills found` sin crash

### Reglas de negocio

- **RB-SP-01:** `SkillPaletteScreen` recibe `change_name: str | None = None` como parámetro de constructor.
- **RB-SP-02:** El filtrado es idéntico al patrón de EpicsView — `Input` oculto, visible al activar con `/`, foco vuelve al DataTable al limpiar.
- **RB-SP-03:** La pantalla usa `push_screen` — la pantalla previa conserva su estado.
- **RB-SP-04:** El highlight de resultados filtrados usa `bold cyan` (patrón establecido en EpicsView).
- **RB-SP-05:** El binding `ctrl+p` global se define en `App` con `priority=True` para que capture desde cualquier pantalla sin interferir con widgets.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `change_name: str \| None` en constructor | Inferir pantalla origen | Explícito y testable sin inspeccionar el stack de pantallas |
| `ctrl+p` global en App | Solo `K` en cada vista | `ctrl+p` es la convención universal de command palette — discoverability sin estar en View 1/2 |
| Reutilizar patrón de filtro de EpicsView | Filtro nuevo con diferente UX | Consistencia en la TUI — el usuario ya conoce el patrón |
| Context-aware por whitelist explícita | Prefijo `sdd-` sin excepciones | Las excepciones (`sdd-new`, `sdd-ff`, etc.) son reales y la lista es estable |
| `copy_to_clipboard` nativo de Textual | `pyperclip` | Sin deps nuevas — patrón ya usado en View 5 |

## Abierto / Pendiente

Ninguno.
