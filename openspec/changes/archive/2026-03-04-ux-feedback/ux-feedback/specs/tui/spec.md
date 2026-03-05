# Spec: TUI — UX Feedback (Estado Visual y Notificaciones)

## Metadata
- **Dominio:** tui
- **Change:** ux-feedback
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** draft

## Contexto

La app ejecuta acciones sin dar feedback visual al usuario. Cuatro problemas
concretos: toggle de archivados sin estado visible, acciones sin notificación
de éxito, avisos de "archivo no encontrado" que pasan desapercibidos, y falta
del binding `q` en SpecSelectorScreen.

## Comportamiento Actual

- El footer de View 1 muestra siempre "Archived" como label del binding `a`,
  sin distinguir si los archivados están visibles u ocultos.
- Las acciones (refresh, abrir docs) son silenciosas — sin notificaciones.
- `DocumentViewerScreen` muestra `[dim]filename not found[/dim]` en el cuerpo;
  fácil de no ver.
- `SpecSelectorScreen` solo acepta `Esc` para cerrar — `q` no tiene efecto.

## Requisitos (EARS)

- **REQ-01** `[State]` While los archivados están ocultos (`_show_archived == False`), the footer SHALL mostrar `"Show archived"` como label del binding `a`.

- **REQ-02** `[State]` While los archivados están visibles (`_show_archived == True`), the footer SHALL mostrar `"Hide archived"` como label del binding `a`.

- **REQ-03** `[Event]` When el usuario pulsa `a` para togglear archivados, the `EpicsView` SHALL llamar `self.refresh_bindings()` para que el footer refleje el nuevo estado inmediatamente.

- **REQ-04** `[Event]` When el refresh de View 1 completa con éxito, the `EpicsView` SHALL mostrar una notificación con el conteo: `"{N} changes loaded ({M} archived)"` donde N es el total y M el número de archivados.

- **REQ-05** `[Ubiquitous]` The notificación de refresh SHALL mostrarse solo tras un refresh exitoso — no cuando la lista ya estaba actualizada o cuando falla.

- **REQ-06** `[Event]` When el usuario abre un documento que existe (p, d, t, s, q, r), the `ChangeDetailScreen` SHALL mostrar una notificación `"Opening {label}"` donde `{label}` es el nombre semántico corto (e.g. "proposal", "design", "tasks").

- **REQ-07** `[Unwanted]` If el archivo solicitado no existe, the `DocumentViewerScreen` SHALL mostrar `self.app.notify("{filename} not found", severity="warning")` además del mensaje `"[dim]{filename} not found[/dim]"` en el cuerpo.

- **REQ-08** `[Ubiquitous]` The binding `q` SHALL estar disponible en `SpecSelectorScreen` con action `"app.pop_screen"` y label `"Close"`.

- **REQ-09** `[Event]` When el usuario pulsa `q` en `SpecSelectorScreen`, the screen SHALL cerrarse y volver a View 2 (equivalente a `Esc`).

### Escenarios de verificación

**REQ-01 / REQ-02** — Label dinámico en footer
**Dado** View 1 con archivados ocultos (estado inicial)
**Cuando** el usuario mira el footer
**Entonces** el binding `a` muestra "Show archived"

**Dado** View 1 con archivados ocultos
**Cuando** el usuario pulsa `a`
**Entonces** el footer muestra "Hide archived" (sin delay — refresh_bindings inmediato)

**REQ-04** — Notify con conteo
**Dado** View 1 con 5 changes activos y 3 archivados (archivados ocultos)
**Cuando** el usuario pulsa `r` (refresh)
**Entonces** aparece la notificación "5 changes loaded (3 archived)"

**REQ-06** — Notify al abrir doc
**Dado** View 2 con un change que tiene `proposal.md`
**Cuando** el usuario pulsa `p`
**Entonces** aparece "Opening proposal" y se abre el viewer

**REQ-07** — Warning archivo no encontrado
**Dado** View 2 con un change sin `design.md`
**Cuando** el usuario pulsa `d`
**Entonces** aparece una notificación warning "design.md not found" Y el viewer muestra "[dim]design.md not found[/dim]"

**REQ-08 / REQ-09** — `q` en SpecSelectorScreen
**Dado** SpecSelectorScreen abierto desde View 2
**Cuando** el usuario pulsa `q`
**Entonces** se cierra el selector y vuelve a View 2

## Interfaces / Contratos

### EpicsView — label dinámico

El binding `a` se declara con un `check` method o un `BINDINGS` dinámico:

```python
def check_action(self, action: str, parameters: tuple) -> bool | None:
    # No aplica — usar refresh_bindings()
    pass

def _get_archived_label(self) -> str:
    return "Hide archived" if self._show_archived else "Show archived"
```

### EpicsView — notify refresh

```python
notify_msg = f"{n_active} changes loaded ({n_archived} archived)"
self.notify(notify_msg)
```

Donde `n_active` = changes con `archived == False`, `n_archived` = changes con `archived == True`.

### ChangeDetailScreen — notify al abrir doc

```python
# Solo si el archivo existe
if path.exists():
    self.notify(f"Opening {label}")
self.push_screen(DocumentViewerScreen(path, title))
```

### DocumentViewerScreen — warning not found

```python
if not self._path.exists():
    self.app.notify(f"{self._path.name} not found", severity="warning")
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `refresh_bindings()` para label dinámico | Reescribir `BINDINGS` como lista | `refresh_bindings()` es la API oficial de Textual para bindings reactivos |
| Notify en `ChangeDetailScreen` antes de `push_screen` | Notify en `DocumentViewerScreen` al montar | Más claro: el que abre el documento notifica; el viewer solo gestiona "not found" |
| Notify con conteo `N changes loaded (M archived)` | "Changes refreshed" simple | El usuario pidió conteo explícito para distinguir activos/archivados |
| Notify en viewer solo para not-found | Notify siempre en viewer | Evitar doble notify (abrir + not found) cuando el archivo no existe |
| `q` en SpecSelectorScreen = `app.pop_screen` | Binding a acción custom | Consistente con `Esc` — ambos cierran el selector |
| Nombre corto en notify ("proposal") | Ruta o filename completo | Más legible; el usuario ya sabe qué documento abre por el contexto |

## Abierto / Pendiente

Ninguno.
