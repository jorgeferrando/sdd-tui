# Proposal: View 1 — Search & Filter

## Metadata
- **Change:** view-search-filter
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

View 1 muestra todos los changes en un DataTable. Con pocos cambios esto
funciona bien. A medida que el proyecto crece — especialmente con el toggle `a`
que muestra archivados — la lista puede alcanzar 20-30 filas fácilmente.

No hay forma de llegar rápidamente a un change específico sin navegar fila
a fila. En proyectos multi-sprint con muchos archivados, encontrar
`di-450-parking-rate` entre 25 cambios requiere scroll manual.

El patrón `/ → input → filtrar` es estándar en herramientas TUI de alta
calidad (fzf, lazygit, tig, k9s). Los usuarios que trabajan en terminal
lo conocen y lo esperan.

## Solución Propuesta

### Binding `/` — activar modo búsqueda

**Dado** View 1 en modo normal
**Cuando** el usuario pulsa `/`
**Entonces:**
- Aparece un input de búsqueda en el pie de la pantalla (sobre el footer)
- El DataTable mantiene el foco visual pero las teclas de navegación
  van al input
- El texto ingresado filtra las filas del DataTable en tiempo real
  (substring case-insensitive sobre el nombre del change)
- `Esc` cancela la búsqueda y restaura la lista completa
- `Enter` confirma el filtro y devuelve el foco al DataTable

### Comportamiento de filtrado

- Filtro sobre `change.name` — substring case-insensitive
- Los archivados solo aparecen en el resultado si el toggle `a` está activo
- La fila separadora `── archived ──` se mantiene si hay archivados en el resultado
- Con 0 resultados: DataTable muestra una fila `No matches for "{query}"`
- El filtro se limpia automáticamente al pulsar `r` (refresh)

### Indicador visual

Mientras el modo búsqueda está activo, el footer muestra:
```
/ {query}▌   [Enter] confirmar   [Esc] cancelar
```

Al confirmar, el footer vuelve al estado normal con el filtro aplicado
visible en el título o como badge:
```
sdd-tui — changes (filtered: "{query}")
```

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Filtro siempre visible (input persistente arriba) | Siempre accesible | Ocupa espacio fijo, distrae en uso normal | Descartada |
| Navegación por primera letra (ej: `p` va a primer change que empieza por p) | Sin modo extra | Limitado, choca con bindings existentes | Descartada |
| **`/` como modal de búsqueda** | Patrón conocido, no ocupa espacio en reposo | Requiere gestión de estado de modo | **Elegida** |

## Impacto Estimado

- **Dominio:** tui
- **Archivos modificados:**
  - `tui/epics.py` — añadir modo búsqueda, widget Input, lógica de filtrado
- **Archivos nuevos:** Ninguno
- **Breaking changes:** Ninguno — `/` no tiene binding actual en View 1
- **Tests afectados:** `tests/test_tui_epics.py` (cuando exista, por `tui-tests`)

## Criterios de Éxito

- [ ] `/` activa modo búsqueda con input visible
- [ ] El filtrado ocurre en tiempo real mientras se escribe
- [ ] `Esc` restaura la lista completa
- [ ] `Enter` confirma y devuelve foco al DataTable con cursor en primer resultado
- [ ] Con 0 resultados, se muestra mensaje apropiado
- [ ] El filtro respeta el estado del toggle `a`

## Preguntas Abiertas

- [ ] ¿El filtro activo persiste al pulsar `a` (toggle archivados) o se limpia?
- [ ] ¿Filtrar también por fase del pipeline (ej: `apply` para ver changes en apply)? — podría ser scope de v2
- [ ] ¿Resaltar el match en el nombre del change dentro del DataTable?
