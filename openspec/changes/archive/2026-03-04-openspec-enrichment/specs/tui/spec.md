# Spec: TUI — openspec enrichment (SteeringScreen + requirements binding)

## Metadata
- **Dominio:** tui
- **Change:** openspec-enrichment
- **Fecha:** 2026-03-04
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Expone en la TUI los nuevos artefactos del formato openspec:
- `SteeringScreen` — nueva pantalla para `openspec/steering.md` desde View 1
- Binding `q` en View 2 — abre `requirements.md` como document viewer
- `SpecHealthScreen` (View 8) — columna `Q` para requirements.md

## Comportamiento Actual

View 1 (EpicsView) tiene bindings: Enter → View 2, H → SpecHealthScreen,
a → toggle archived, X → DecisionsTimeline.
View 2 tiene bindings para documentos: p, d, s, t.
SpecHealthScreen muestra artefactos: P S R D T.

## Requisitos (EARS)

### SteeringScreen

- **REQ-ST01** `[Event]` When the user presses `S` in View 1, the TUI SHALL open `SteeringScreen` via `push_screen`
- **REQ-ST02** `[Event]` When the user presses `Esc` in SteeringScreen, the TUI SHALL return to View 1 via `pop_screen`
- **REQ-ST03** `[Optional]` Where `steering.md` exists, SteeringScreen SHALL render its content with `rich.Markdown`
- **REQ-ST04** `[Unwanted]` If `steering.md` does not exist, SteeringScreen SHALL display `"No steering document found"` without raising any exception

### View 2 — Requirements binding

- **REQ-RB01** `[Event]` When the user presses `q` in View 2, the TUI SHALL open a `DocumentViewerScreen` with `requirements.md` content
- **REQ-RB02** `[Unwanted]` If `requirements.md` does not exist, the viewer SHALL display `"requirements.md not found"` (consistent with behavior for other missing documents)

### View 8 — SpecHealthScreen requirements column

- **REQ-HQ01** `[Optional]` Where at least one visible change has `requirements.md`, the ARTIFACTS column SHALL include a `Q` indicator for each change that has it
- **REQ-HQ02** `[Ubiquitous]` The ARTIFACTS column letter order SHALL be: `P S R Q D T` (requirements between research and design, matching core artifact order)

### Escenarios de verificación

**REQ-ST03 / REQ-ST04** — SteeringScreen con y sin archivo
**Dado** View 1 abierto
**Cuando** el usuario pulsa `S`
**Entonces** si `steering.md` existe → SteeringScreen muestra el contenido formateado
            si no existe → SteeringScreen muestra `"No steering document found"`

**REQ-HQ01** — Columna Q condicional
**Dado** SpecHealthScreen con 3 changes, donde 2 tienen `requirements.md`
**Cuando** se renderiza la tabla
**Entonces** la columna ARTIFACTS muestra `Q` para los 2 changes con requirements.md
  y `.` (punto) para el change sin él

## Layout

### SteeringScreen

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — steering                                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  {rich.Markdown del steering.md}                            │
│                                                              │
│  ...scrollable...                                            │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ [Esc] ← changes                                              │
└─────────────────────────────────────────────────────────────┘
```

### View 1 — Footer actualizado

```
[H] health   [S] steering   [X] decisions   [a] toggle archived
```

### View 2 — Footer actualizado

```
[Esc] ← changes   [r] refresh   [p] proposal   [d] design
[s] spec(s)   [t] tasks   [q] requirements   [E] evolution   [Space] copy
```

### SpecHealthScreen — ARTIFACTS column con Q

```
CHANGE              REQ  EARS%  TASKS   ARTIFACTS      INACTIVE
view-8-spec-health   19  100%   6/6    P S . Q D T    0d
view-9-delta-specs    0   —     0/4    P . . . . .    —
```

Nota: la columna `R` (research) y `Q` (requirements) solo aparecen en la tabla
si al menos un change visible tiene ese artefacto (misma regla que `R` actual).

## Casos alternativos

| Escenario | Resultado |
|-----------|-----------|
| steering.md no existe | SteeringScreen muestra `"No steering document found"` |
| steering.md vacío | SteeringScreen muestra contenido vacío sin error |
| requirements.md no existe | `q` en View 2 muestra `"requirements.md not found"` |
| Ningún change tiene requirements.md | Columna `Q` no aparece en SpecHealthScreen (misma regla que `R`) |

## Reglas de negocio

- **RB-ST01:** `SteeringScreen` usa `push_screen` — patrón consistente con otras pantallas de detalle
- **RB-ST02:** `SteeringScreen` reutiliza el mismo layout que `DocumentViewerScreen` (Header + ScrollableContainer + Footer)
- **RB-ST03:** El binding `S` es uppercase para distinguirlo de `s` (specs en View 2); en View 1 no hay binding `s` previo
- **RB-RB01:** `q` para requirements sigue la convención de View 2: letras minúsculas para documentos del change
- **RB-HQ01:** La columna `Q` solo aparece si `any(change has requirements.md)` — consistente con el comportamiento de `R`

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `SteeringScreen` como nueva pantalla con `push_screen` | Panel visible en View 1 | Pantalla completa = mejor lectura; View 1 ya está densa con la tabla de changes |
| `rich.Markdown` para steering | `rich.Syntax` + lexer markdown | Renderiza semánticamente (headers, tablas, listas) — mismo patrón que DocumentViewerScreen |
| Binding `S` (uppercase) en View 1 | `s` (lowercase) | `s` no existe en View 1 pero `S` es consistente con `H` y `X` (uppercase para pantallas especiales en View 1) |
| Binding `q` (lowercase) en View 2 | `R` (uppercase) | View 2 usa minúsculas para todos los documentos (p/d/s/t); `q` de reQueriments sigue el patrón |
| `SteeringScreen` separada de `DocumentViewerScreen` | Reutilizar DocumentViewerScreen | steering.md es global (no pertenece a un change); el título y el origen del contenido son distintos |

## Abierto / Pendiente

Ninguno.
