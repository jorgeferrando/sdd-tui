# Spec: TUI — View 1 Search & Filter

## Metadata
- **Dominio:** tui
- **Change:** view-search-filter
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** approved

## Contexto

View 1 (`EpicsView`) muestra todos los changes en un `DataTable`. Con muchos changes
activos y archivados, encontrar uno específico requiere navegación fila a fila.

Este cambio añade modo búsqueda `/` al estilo de herramientas TUI estándar (fzf, lazygit,
tig, k9s): filtrado en tiempo real con substring case-insensitive sobre el nombre del change.

## Comportamiento Actual

- View 1 muestra todos los changes en un `DataTable` sin capacidad de filtrado.
- La navegación es exclusivamente por cursor (j/k o flechas).
- El binding `/` no existe en `EpicsView`.

## Requisitos (EARS)

- **REQ-01** `[Event]` When el usuario pulsa `/` en View 1, the app SHALL activar el modo búsqueda mostrando un input en el pie de pantalla.
- **REQ-02** `[State]` While el modo búsqueda está activo, the input SHALL recibir las teclas del teclado y filtrar el DataTable en tiempo real.
- **REQ-03** `[Event]` When el usuario escribe en el input de búsqueda, the DataTable SHALL actualizar sus filas mostrando solo los changes cuyo nombre contiene el texto (substring case-insensitive).
- **REQ-04** `[Event]` When el usuario pulsa `Esc` con modo búsqueda activo, the app SHALL desactivar el modo búsqueda, limpiar el filtro y restaurar la lista completa.
- **REQ-05** `[Event]` When el usuario pulsa `Enter` con modo búsqueda activo, the app SHALL desactivar el modo búsqueda, mantener el filtro aplicado y devolver el foco al DataTable con el cursor en el primer resultado.
- **REQ-06** `[Unwanted]` If el filtro produce 0 resultados, the DataTable SHALL mostrar una fila `No matches for "{query}"` sin key.
- **REQ-07** `[State]` While el modo búsqueda está activo, the footer SHALL mostrar `/ {query}▌   [Enter] confirmar   [Esc] cancelar`.
- **REQ-08** `[Event]` When el filtro está confirmado (modo normal con filtro activo), the title SHALL mostrar `sdd-tui — changes (filtered: "{query}")`.
- **REQ-09** `[Event]` When el usuario pulsa `r` (refresh) con filtro activo, the app SHALL limpiar el filtro y restaurar la lista completa antes de recargar.
- **REQ-10** `[State]` While el filtro está activo y el usuario pulsa `a` (toggle archivados), the filtro SHALL persistir aplicándose al nuevo scope (activos+archivados o solo activos).
- **REQ-11** `[Ubiquitous]` The filtrado SHALL respetar el estado del toggle `a`: los archivados solo aparecen en los resultados si `_show_archived` es `True`.
- **REQ-12** `[Ubiquitous]` The separador `── archived ──` SHALL mantenerse si hay archivados en los resultados filtrados.
- **REQ-13** `[Event]` When el DataTable muestra resultados filtrados, the nombre del change SHALL mostrar el substring coincidente en `bold cyan` dentro del nombre.

### Escenarios de verificación

**REQ-03 + REQ-13** — Filtrado en tiempo real con highlight
**Dado** View 1 con changes: `view-search-filter`, `view-help-screen`, `perf-async-diffs`
**Cuando** el usuario pulsa `/` y escribe `view`
**Entonces** el DataTable muestra solo las filas `view-search-filter` y `view-help-screen`, con `view` en bold cyan dentro de cada nombre

**REQ-06** — Sin resultados
**Dado** View 1 en modo búsqueda con query `xyz-no-match`
**Cuando** no hay ningún change que contenga `xyz-no-match`
**Entonces** el DataTable muestra una única fila `No matches for "xyz-no-match"` sin key, sin posibilidad de navegación a View 2

**REQ-10** — Filtro persiste con toggle archivados
**Dado** View 1 con filtro activo `view` mostrando 2 activos
**Cuando** el usuario pulsa `a` para mostrar archivados
**Entonces** el DataTable muestra activos + archivados cuyo nombre contiene `view`, con separador `── archived ──` si hay archivados en el resultado

**REQ-04 vs REQ-05** — Esc limpia, Enter confirma
**Dado** View 1 con modo búsqueda activo y query `view` (2 resultados)
**Cuando** el usuario pulsa `Esc`
**Entonces** la lista completa se restaura, query limpiada, title normal

**Dado** View 1 con modo búsqueda activo y query `view` (2 resultados)
**Cuando** el usuario pulsa `Enter`
**Entonces** el modo búsqueda se cierra, el DataTable mantiene las 2 filas filtradas, el cursor está en la primera fila, el title muestra `sdd-tui — changes (filtered: "view")`

## Interfaces / Contratos

### Estado nuevo en EpicsView

```
_search_mode: bool = False        # True mientras input está activo
_search_query: str = ""           # Query actual (vacío = sin filtro)
```

### Lógica de filtrado

```python
def _apply_filter(changes: list[Change], query: str, show_archived: bool) -> list[Change]:
    # Filtra por substring case-insensitive sobre change.name
    # Respeta show_archived para incluir/excluir archivados
    # Devuelve lista ordenada igual que _apply_display actual
```

### Highlight de match

```python
def _highlight_match(name: str, query: str) -> Text:
    # Devuelve rich.Text con el substring query en "bold cyan"
    # El resto del nombre en estilo normal
    # Si query vacío, devuelve Text(name)
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Widget `Input` de Textual (oculto/visible) | `Input` siempre visible en header | No ocupa espacio en reposo; patrón modal estándar en TUI |
| `Esc` limpia filtro completamente | `Esc` solo cierra input dejando filtro | Coherente con expectativa del usuario: Esc = cancelar = deshacer |
| Filtro persiste al toggle `a` | Filtro se limpia al toggle `a` | La búsqueda es una intención del usuario — el toggle cambia el scope, no la búsqueda |
| Highlight `bold cyan` en match | Sin highlight / `bold` solo | Contraste suficiente en terminales oscuras; `cyan` disponible universalmente |
| Fila especial sin key para 0 resultados | `notify` con mensaje | El feedback está donde el usuario mira — en la tabla misma |
| `r` limpia filtro antes de reload | `r` reload manteniendo filtro | El refresh es un reset explícito; confuso si el filtro persiste invisiblemente |

## Abierto / Pendiente

- Filtrado por fase del pipeline (ej: `apply` para ver changes en apply) — diferido a v2.
