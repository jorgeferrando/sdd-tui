# Design: startup-deps-check

## Metadata
- **Change:** startup-deps-check
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Módulo `core/deps.py` con dataclass `Dep`, lista estática `DEPS` y función
`check_deps()` que detecta ausencias via `subprocess.run`. La función sigue
el mismo patrón que `GitReader` — captura `FileNotFoundError` y comprueba
returncode. `SddTuiApp.on_mount` llama `check_deps()` y actúa: `push_screen`
de `ErrorScreen` para required missing, `notify()` para optional missing.

## Arquitectura

```
SddTuiApp.on_mount
  └─ check_deps()  [core/deps.py]
       └─ _is_present(dep) → subprocess.run(dep.check_cmd)
            ├─ returncode 0  → presente
            └─ returncode ≠0 / FileNotFoundError → ausente

  missing_required → push_screen(ErrorScreen(deps))
  missing_optional → notify(msg, severity="warning", timeout=15) × dep
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/core/deps.py` | Módulo core | `Dep`, `DEPS`, `check_deps()`, `_is_present()` |
| `src/sdd_tui/tui/error_screen.py` | Screen Textual | `ErrorScreen` — muestra deps required missing + `[q]` quit |
| `tests/test_deps.py` | Tests unitarios | Cobertura de `check_deps()` con subprocess mock |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/tui/app.py` | Añadir `on_mount` | Llama `check_deps()` y actúa según resultado |

## Scope

- **Total archivos:** 4
- **Resultado:** Ideal (< 10)

## Diseño de `core/deps.py`

```python
from __future__ import annotations
import subprocess
import sys
from dataclasses import dataclass

@dataclass
class Dep:
    name: str
    required: bool
    check_cmd: list[str]
    install_hint: dict[str, str]   # {"macOS": "brew install git", "Ubuntu": "sudo apt install git"}
    docs_url: str | None
    feature: str | None            # None si required

DEPS: list[Dep] = [
    Dep(
        name="git",
        required=True,
        check_cmd=["git", "--version"],
        install_hint={"macOS": "brew install git", "Ubuntu": "sudo apt install git"},
        docs_url="https://git-scm.com/downloads",
        feature=None,
    ),
    Dep(
        name="gh",
        required=False,
        check_cmd=["gh", "--version"],
        install_hint={"macOS": "brew install gh", "Ubuntu": "sudo apt install gh"},
        docs_url="https://cli.github.com",
        feature="pr-status",
    ),
]

def check_deps() -> tuple[list[Dep], list[Dep]]:
    """Returns (missing_required, missing_optional)."""
    missing_required, missing_optional = [], []
    for dep in DEPS:
        if not _is_present(dep):
            (missing_required if dep.required else missing_optional).append(dep)
    return missing_required, missing_optional

def _is_present(dep: Dep) -> bool:
    try:
        result = subprocess.run(dep.check_cmd, capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
```

## Diseño de `tui/error_screen.py`

Sigue el patrón de `HelpScreen`: `Header` + `ScrollableContainer(Static(...))` + `Footer`.
Contenido generado con `rich.Text`.

```python
class ErrorScreen(Screen):
    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self, deps: list[Dep]) -> None:
        super().__init__()
        self._deps = deps

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(Static(_build_error_content(self._deps)))
        yield Footer()

    def on_mount(self) -> None:
        self.title = "sdd-tui — dependency error"

    def action_quit(self) -> None:
        self.app.exit()
    # Sin binding Escape — no hay pantalla previa válida
```

`_build_error_content(deps)` genera `rich.Text` con un bloque por dep:
```
  Required dependency missing: git         (bold red)

    macOS:   brew install git
    Ubuntu:  sudo apt install git
    Docs:    https://git-scm.com/downloads
```

## Diseño de `SddTuiApp.on_mount`

```python
def on_mount(self) -> None:
    from sdd_tui.core.deps import check_deps
    from sdd_tui.tui.error_screen import ErrorScreen

    missing_required, missing_optional = check_deps()

    if missing_required:
        self.push_screen(ErrorScreen(missing_required))
        return

    for dep in missing_optional:
        platform_key = "macOS" if sys.platform == "darwin" else "Ubuntu"
        hint = dep.install_hint.get(platform_key, "")
        parts = [f"{dep.name} not found — {dep.feature} disabled"]
        if hint:
            parts.append(f"Install: {hint}")
        if dep.docs_url:
            parts.append(dep.docs_url)
        self.notify("  |  ".join(parts), severity="warning", timeout=15)
```

Imports locales para evitar importaciones circulares (patrón ya establecido en `action_help`).

## Patrones Aplicados

- **Mismo patrón que `GitReader`**: `subprocess.run` + `capture_output=True` + captura `FileNotFoundError`
- **Imports locales en métodos**: ya usado en `action_help` y `action_decisions_timeline`
- **`rich.Text` para contenido estático**: patrón de `HelpScreen`
- **`push_screen` desde `on_mount`**: patrón Textual estándar

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| `on_mount` para el check | `compose()` | `compose()` no puede hacer `push_screen`; `on_mount` sí |
| Imports locales en `on_mount` | Import al top del módulo | Consistencia con el resto de `app.py`; evita circulares |
| `_is_present` como función module-level | Método de clase | Testable de forma aislada con patch; sin estado |
| Sin binding `Esc` en `ErrorScreen` | `Esc` → exit | `Esc` en Textual hace `pop_screen` por defecto — peligroso aquí; explícito es mejor |
| `capture_output=True` en check | Dejar stdout/stderr libres | No contaminar la salida de la app con output de `git --version` |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_check_deps_all_present` | Unit | Todas las check_cmds → code 0 → `([], [])` |
| `test_check_deps_required_missing_file_not_found` | Unit | `FileNotFoundError` en required → `([dep], [])` |
| `test_check_deps_required_missing_non_zero` | Unit | returncode=1 en required → `([dep], [])` |
| `test_check_deps_optional_missing` | Unit | returncode=1 en optional → `([], [dep])` |
| `test_check_deps_checks_are_independent` | Unit | Un fallo no impide comprobar el siguiente |
| `test_is_present_file_not_found` | Unit | `FileNotFoundError` → `False` |
| `test_is_present_success` | Unit | returncode=0 → `True` |

## Notas de Implementación

- `sys.platform` ya importado en `app.py` — no añade dependencia nueva.
- El check de `git` nunca debería fallar en uso real (git es ubicuo), pero es
  correcto tenerlo para completitud y para que los tests sean posibles.
- El `timeout=15` en `notify` es configurable en el futuro si se necesita ajustar.
