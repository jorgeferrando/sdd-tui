# Spec: TUI — Mostrar/ocultar archivados (View 7)

## Metadata
- **Dominio:** tui
- **Change:** view-7-show-archived
- **Fecha:** 2026-03-03
- **Versión:** delta
- **Estado:** approved

## Comportamiento Esperado

### Toggle — tecla `a`

**Dado** View 1 mostrando solo changes activos (estado por defecto)
**Cuando** el usuario pulsa `a`
**Entonces** la lista se recarga mostrando activos + archivados, separados por `── archived ──`

**Dado** View 1 mostrando activos + archivados
**Cuando** el usuario pulsa `a`
**Entonces** la lista vuelve a mostrar solo activos

### Layout con archivados visibles

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui                                                      │
├──────────────────────────┬───┬───┬───┬───┬───┬─────────────┤
│ change                   │ p │ s │ d │ t │ a │ v           │
├──────────────────────────┼───┼───┼───┼───┼───┼─────────────┤
│ view-7-show-archived     │ ✓ │ ✓ │ ✓ │ ✓ │ · │ ·           │
│ ── archived ──           │   │   │   │   │   │             │
│ 2026-03-03-view-6-re...  │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │ ✓           │
│ 2026-03-03-view-5-cl...  │ ✓ │ ✓ │ ✓ │ ✓ │ ✓ │ ✓           │
├──────────────────────────┴───┴───┴───┴───┴───┴─────────────┤
│ [r] Refresh  [a] Archived  [q] Quit                         │
└─────────────────────────────────────────────────────────────┘
```

### Selección de un archivado

**Dado** View 1 con archivados visibles
**Cuando** el usuario pulsa Enter sobre un archivado
**Entonces** se abre View 2 (ChangeDetailScreen) con ese change, igual que con un activo

### Separador de sección

- El separador `── archived ──` es una fila no seleccionable (sin key en DataTable)
- No abre View 2 si se pulsa Enter sobre él

## Reglas de Negocio

- **RB-V7-01:** El estado del toggle es local a la sesión (no persiste).
- **RB-V7-02:** Por defecto, los archivados están ocultos.
- **RB-V7-03:** Los archivados se cargan desde `openspec/changes/archive/*/`.
- **RB-V7-04:** El separador no tiene key → Enter sobre él no hace nada.
- **RB-V7-05:** La selección usa `row_key` (no índice) para soportar la fila separadora.
- **RB-V7-06:** `r` recarga respetando el estado del toggle (`_show_archived`).
