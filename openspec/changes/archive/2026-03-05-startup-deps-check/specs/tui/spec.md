# Spec: TUI — Startup Dependency Check

## Metadata
- **Dominio:** tui
- **Change:** startup-deps-check
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** draft

## Contexto

`SddTuiApp.on_mount` llama a `check_deps()` y actúa según el resultado antes de
que el usuario pueda interactuar con la app. El objetivo es informar claramente
sobre dependencias ausentes, nunca fallar en silencio.

---

## 1. Flujo de startup

- **REQ-01** `[Event]` When the app mounts, the system SHALL call `check_deps()` before the main view is usable.
- **REQ-02** `[Event]` When `check_deps()` returns one or more missing required deps, the app SHALL push `ErrorScreen` with the list of missing deps.
- **REQ-03** `[Unwanted]` If `ErrorScreen` is displayed, the main application view SHALL NOT be interactable (ErrorScreen ocupa el stack completo).
- **REQ-04** `[Event]` When `check_deps()` returns one or more missing optional deps, the app SHALL emit one `notify()` per missing dep with `severity="warning"`.
- **REQ-05** `[Event]` When all deps are present, the app SHALL mount normally without any notification.

---

## 2. `ErrorScreen` — Required dependency missing

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — dependency error                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Required dependency missing: git                            │
│                                                              │
│  Install:                                                    │
│    macOS:    brew install git                                │
│    Ubuntu:   sudo apt install git                            │
│    Docs:     https://git-scm.com/downloads                   │
│                                                              │
│  (repeat block for each missing required dep)                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ [q] quit                                                     │
└─────────────────────────────────────────────────────────────┘
```

### Comportamiento

- **REQ-06** `[State]` While `ErrorScreen` is displayed, the user SHALL be able to quit with `q`.
- **REQ-07** `[Ubiquitous]` `ErrorScreen` SHALL display all missing required deps, one block per dep.
- **REQ-08** `[Ubiquitous]` Each dep block SHALL show: dep name, one install line per platform key in `install_hint`, and `docs_url` si no es `None`.
- **REQ-09** `[Unwanted]` If `ErrorScreen` is displayed, `Esc` SHALL NOT close it (no `pop_screen` — la app no tiene estado previo válido).

### Reglas de negocio

- **RB-E1:** `ErrorScreen` recibe `deps: list[Dep]` en su constructor.
- **RB-E2:** El binding `q` llama `self.app.exit()` — no `pop_screen`.
- **RB-E3:** `ErrorScreen` está en `tui/error_screen.py` — clase independiente.
- **RB-E4:** `on_mount` usa `self.push_screen` para mostrar `ErrorScreen` sin desmontar la app base (permite `self.app.exit()` desde dentro).

---

## 3. Notify toast — Optional dependency missing

### Formato del mensaje

```
{name} not found — {feature} disabled
Install: {install_hint[platform]}  |  {docs_url}
```

Si hay múltiples plataformas, se muestra solo la del sistema actual (`sys.platform`):
- `darwin` → key `"macOS"`
- `linux` → key `"Ubuntu"` (fallback genérico)
- Si la key no existe → omitir la línea de install; mostrar solo `docs_url`.

### Comportamiento

- **REQ-10** `[Event]` When an optional dep is missing, the app SHALL call `self.notify(message, severity="warning", timeout=15)` — timeout largo para que el usuario pueda leer.
- **REQ-11** `[Ubiquitous]` One notify SHALL be emitted per missing optional dep — no se agrupan.
- **REQ-12** `[Ubiquitous]` Optional dep warnings SHALL be emitted only once per session (on_mount), not on refresh or navigation.

### Reglas de negocio

- **RB-N1:** La detección de plataforma usa `sys.platform` — no requiere deps externas.
- **RB-N2:** Si `docs_url` es `None`, la línea del URL se omite del mensaje.
- **RB-N3:** El `timeout=15` es suficiente para leer; el usuario puede descartarlo con Esc nativo de Textual toasts.

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| Check en `on_mount` | Check pre-`App.run()` con `sys.exit` | Consistente con el ciclo de vida Textual; permite `ErrorScreen` con rich UI |
| `push_screen(ErrorScreen)` | Swap del screen inicial | `push_screen` permite que `self.app.exit()` funcione correctamente |
| `timeout=15` en notify | Sin timeout (persiste indefinidamente) | Textual no soporta toasts sin timeout de forma limpia; 15s es suficiente para leer |
| Plataforma actual en notify | Mostrar todas las plataformas | El notify es texto corto — mostrar todas contamina; ErrorScreen sí las muestra todas |
| `Esc` bloqueado en ErrorScreen | `Esc` cierra como siempre | No hay pantalla previa válida; `pop_screen` dejaría la app en estado inconsistente |

## Abierto / Pendiente

Ninguno.
