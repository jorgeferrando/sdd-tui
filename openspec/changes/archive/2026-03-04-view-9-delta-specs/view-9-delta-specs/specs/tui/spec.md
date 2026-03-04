# Spec: TUI — View 9 (Spec Evolution Viewer) + Decisions Timeline

## Metadata
- **Dominio:** tui
- **Change:** view-9-delta-specs
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** draft

## Contexto

View 9 añade dos pantallas nuevas:

1. **`SpecEvolutionScreen`** (`E` desde View 2): muestra el delta spec del change
   activo con secciones ADDED/MODIFIED/REMOVED coloreadas. Toggle `D` para
   ver la spec canónica completa en su lugar.

2. **`DecisionsTimeline`** (`X` desde View 1): agrega todas las secciones
   "Decisiones Tomadas" de los `design.md` archivados, ordenadas por fecha.

## ADDED Requirements

### Spec Evolution Screen (View 9)

- **REQ-01** `[Event]` When the user presses `E` in View 2 (ChangeDetailScreen), the system SHALL open `SpecEvolutionScreen` via `push_screen`, passing the current change.

- **REQ-02** `[Event]` When `SpecEvolutionScreen` opens with a change that has multiple spec domains, the system SHALL show a left panel (domain list) and a right panel (diff content).

- **REQ-03** `[Event]` When `SpecEvolutionScreen` opens with a change that has exactly one spec domain, the system SHALL omit the left panel and show the diff content full-width.

- **REQ-04** `[Event]` When a domain is selected in the left panel, the system SHALL load and render the delta for that domain in the right panel.

- **REQ-05** `[State]` While `fallback=False` (delta markers present), the system SHALL render:
  - Lines under `## ADDED` with green style
  - Lines under `## MODIFIED` with yellow style
  - Lines under `## REMOVED` with red style

- **REQ-06** `[State]` While `fallback=True` (no markers), the system SHALL render the spec file content as plain `rich.Markdown` without coloring.

- **REQ-07** `[Event]` When the user presses `D` in `SpecEvolutionScreen`, the system SHALL toggle between delta view and canonical spec view (`openspec/specs/{dominio}/spec.md`).

- **REQ-08** `[Unwanted]` If the canonical spec does not exist when toggling to canonical view, the system SHALL show `"No canonical spec found for {domain}"`.

- **REQ-09** `[Event]` When the user presses `Esc` in `SpecEvolutionScreen`, the system SHALL return to View 2 via `pop_screen`.

- **REQ-10** `[Unwanted]` If the change has no spec files, the system SHALL show `"No specs found for this change"` instead of opening panels.

### Decisions Timeline

- **REQ-11** `[Event]` When the user presses `X` in View 1 (EpicsView), the system SHALL open `DecisionsTimeline` via `push_screen`.

- **REQ-12** `[Ubiquitous]` `DecisionsTimeline` SHALL display a scrollable list of all archived changes that have decisions, ordered by archive date ascending (oldest first).

- **REQ-13** `[Ubiquitous]` For each change, the system SHALL show a header with the change name and date, followed by its decisions rendered as a readable list (not raw markdown table).

- **REQ-14** `[Unwanted]` If no archived changes have decisions, the system SHALL show `"No archived decisions found"`.

- **REQ-15** `[Event]` When the user presses `Esc` in `DecisionsTimeline`, the system SHALL return to View 1 via `pop_screen`.

### Escenarios de verificación

**REQ-02/03** — Layout condicional

**Dado** un change con specs en dos dominios (`core` y `tui`)
**Cuando** se abre `SpecEvolutionScreen`
**Entonces** panel izquierdo lista `core` y `tui`; panel derecho muestra el diff del primero

**Dado** un change con spec en un solo dominio
**Cuando** se abre `SpecEvolutionScreen`
**Entonces** pantalla completa con el diff del único dominio, sin panel izquierdo

**REQ-05** — Coloreado de secciones

**Dado** un delta spec con las tres secciones
**Cuando** se renderiza
**Entonces** ADDED en verde, MODIFIED en amarillo, REMOVED en rojo (usando `Rich.Text`)

**REQ-07** — Toggle D

**Dado** `SpecEvolutionScreen` en modo delta
**Cuando** el usuario pulsa `D`
**Entonces** el panel derecho muestra la spec canónica como `rich.Markdown`; pulsando `D` de nuevo vuelve al delta

## Layout

### SpecEvolutionScreen (multi-dominio)

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — {change} / spec evolution                          │
├──────────────────┬──────────────────────────────────────────┤
│ DOMAINS          │ [delta] core                              │
│                  │                                           │
│ > core           │ ADDED                                     │
│   tui            │   - **REQ-01** [Event] When...  (verde)  │
│                  │                                           │
│                  │ MODIFIED                                   │
│                  │   - **REQ-03** — Before... (amarillo)    │
│                  │                                           │
│                  │ REMOVED                                   │
│                  │   - **REQ-02** — Removed... (rojo)       │
├──────────────────┴──────────────────────────────────────────┤
│ [D] toggle canonical   [Esc] ← back                         │
└─────────────────────────────────────────────────────────────┘
```

### DecisionsTimeline

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — decisions timeline                                  │
├─────────────────────────────────────────────────────────────┤
│ ── view-2-change-detail (2026-02-15) ──                      │
│   push_screen / pop_screen → Textual estándar                │
│   DataTable cursor_type="row" → RowSelected se dispara       │
│                                                              │
│ ── view-8-spec-health (2026-03-04) ──                        │
│   REQ count → IDs únicos (no ocurrencias)                    │
│   metrics opcional en PipelinePanel → retrocompatible        │
│ ...                                                          │
├─────────────────────────────────────────────────────────────┤
│ [Esc] ← changes                                             │
└─────────────────────────────────────────────────────────────┘
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Omitir panel izquierdo si 1 dominio | Siempre mostrar panel | Un solo dominio no necesita selector; pantalla completa mejor legibilidad |
| `Rich.Text` para colorear secciones ADDED/MODIFIED/REMOVED | CSS custom | DataTable no aplica; `ScrollableContainer(Static)` con Rich Text es el patrón ya establecido |
| `DecisionsTimeline` usa `ScrollableContainer(Static)` con Rich | DataTable | No hay selección de filas; es vista de solo lectura lineal |
| Orden por prefijo YYYY-MM-DD del directorio archive | Fecha metadata de design.md | El prefijo ya es canónico y no requiere parsear el interior del archivo |
| `change_name` sin fecha en DecisionsTimeline | Con prefijo completo | Más legible; la fecha aparece como contexto en el header |
| `D` como toggle (delta ↔ canonical) | Dos bindings distintos | Menos bindings; estado visual claro con label en header |

## Abierto / Pendiente

Ninguno.
