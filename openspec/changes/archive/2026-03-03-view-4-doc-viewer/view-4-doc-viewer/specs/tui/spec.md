# Spec: TUI — View 4 (Document viewer)

## Metadata
- **Dominio:** tui
- **Change:** view-4-doc-viewer
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Versión:** 0.1
- **Estado:** approved

## Contexto

View 2 muestra el estado de progreso de un change (tareas + pipeline + diff).
Para leer el contenido documental del change (propuesta, diseño técnico, spec,
lista de tareas completa) el usuario tiene que salir de la TUI.

View 4 añade acceso directo a esos documentos desde View 2, usando teclas de
acceso rápido y una pantalla de visualización de markdown.

---

## Comportamiento Actual

View 2 no tiene acceso a los archivos de documentación del change.
Los keybindings disponibles son: `Esc` (volver) y `r` (refresh).

---

## Comportamiento Esperado (Post-Cambio)

### Keybindings en View 2

| Tecla | Documento | Archivo |
|-------|-----------|---------|
| `p` | Proposal | `proposal.md` |
| `d` | Design | `design.md` |
| `s` | Spec(s) | `specs/{dominio}/spec.md` |
| `t` | Tasks | `tasks.md` |

### Caso Principal — Documento único

**Dado** View 2 de un change con `proposal.md` existente
**Cuando** el usuario pulsa `p`
**Entonces** se abre `DocumentViewerScreen` con el contenido renderizado de
`proposal.md`, mostrando el título `sdd-tui — {change} / proposal`

**Dado** `DocumentViewerScreen` abierto
**Cuando** el usuario pulsa `Esc`
**Entonces** se cierra y vuelve a View 2 con el estado previo intacto
(tarea seleccionada, diff visible)

### Caso Principal — Specs con un solo dominio

**Dado** View 2 de un change con `specs/tui/spec.md` (un solo dominio)
**Cuando** el usuario pulsa `s`
**Entonces** se abre directamente `DocumentViewerScreen` con ese spec

### Caso — Specs con múltiples dominios

**Dado** View 2 de un change con specs en varios dominios (ej: `specs/tui/` y `specs/core/`)
**Cuando** el usuario pulsa `s`
**Entonces** se abre `SpecSelectorScreen` mostrando la lista de dominios disponibles

**Dado** `SpecSelectorScreen` abierto
**Cuando** el usuario selecciona un dominio con Enter
**Entonces** se abre `DocumentViewerScreen` con el spec de ese dominio

**Dado** `SpecSelectorScreen` abierto
**Cuando** el usuario pulsa `Esc`
**Entonces** vuelve a View 2 (sin abrir ningún documento)

### Casos de edge

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Documento no existe | `proposal.md` ausente, usuario pulsa `p` | `DocumentViewerScreen` muestra `{archivo} not found` |
| No hay specs | `specs/` vacío o ausente, usuario pulsa `s` | Mensaje `No specs found` (sin abrir selector) |
| Documento vacío | Archivo existe pero está vacío | Viewer muestra el archivo vacío (sin error) |
| Documento muy largo | Cientos de líneas | Viewer scrollable, sin truncar |

---

## Componentes

### `DocumentViewerScreen`

Nueva pantalla que muestra el contenido de un archivo markdown.

- **Layout:** `Header` + `ScrollableContainer(Static)` + `Footer`
- **Título:** `sdd-tui — {change-name} / {doc-label}` (ej: `sdd-tui — view-4 / proposal`)
- **Contenido:** `rich.Markdown` renderizado dentro de un `Static`
- **Scroll:** flechas ↑↓, `Page Up`/`Page Down` (comportamiento estándar de `ScrollableContainer`)
- **Bindings:** solo `Esc` (volver)

### `SpecSelectorScreen`

Nueva pantalla de selección cuando hay varios dominios de spec.

- **Layout:** `Header` + `ListView` con un item por dominio + `Footer`
- **Título:** `sdd-tui — {change-name} / specs`
- **Items:** nombre del dominio (ej: `tui`, `core`)
- **Acción Enter:** abre `DocumentViewerScreen` con el spec seleccionado
- **Binding Esc:** vuelve a View 2

### `ChangeDetailScreen` — Nuevos bindings

Añadir a `BINDINGS`:
```python
Binding("p", "view_doc('proposal')", "Proposal"),
Binding("d", "view_doc('design')", "Design"),
Binding("s", "view_spec", "Spec"),
Binding("t", "view_doc('tasks')", "Tasks"),
```

---

## Reglas de Negocio

- **RB-V4-01:** El viewer es de solo lectura — no hay edición.
- **RB-V4-02:** Si el documento no existe, mostrar mensaje informativo; no lanzar excepción.
- **RB-V4-03:** El estado de View 2 (tarea seleccionada, diff visible) se preserva al volver con Esc.
- **RB-V4-04:** El contenido se renderiza con `rich.Markdown` (no texto plano ni syntax highlight).
- **RB-V4-05:** Si hay exactamente un dominio de spec, `s` abre directamente el viewer (sin pasar por el selector).
- **RB-V4-06:** Los keybindings `p`, `d`, `s`, `t` están siempre disponibles en View 2, independientemente del estado del change.

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `push_screen` para el viewer | Panel inline en View 2 | Pantalla completa = mejor lectura; patrón ya establecido |
| `rich.Markdown` | `rich.Syntax` con lexer markdown | `Markdown` renderiza semánticamente (headers, tablas, listas), no solo colorea |
| Lista de selección para specs múltiples | Concatenar todos los specs | Más claro distinguir dominios; evita documentos muy largos |
| Acceso directo para doc único | Siempre pasar por selector | Menos pasos para el caso más común |

## Abierto / Pendiente

Ninguno.
