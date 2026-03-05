# Proposal: startup-deps-check — Detección de Dependencias Externas

## Metadata
- **Change:** startup-deps-check
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema / Motivación

`sdd-tui` asume que `git` existe (ya lo hace, falla silenciosamente).
Las nuevas features (`pr-status`) añaden `gh` CLI como dependencia opcional.
Sin un mecanismo explícito de detección, el usuario ve `—` o comportamiento
degradado sin saber por qué ni cómo resolverlo.

El principio: si la app requiere o puede aprovechar una herramienta externa,
debe decirlo claramente — no fallar en silencio.

## Solución Propuesta

### Dos categorías de dependencias

| Categoría | Comportamiento si falta |
|-----------|------------------------|
| **Required** | App no arranca. Muestra error + instrucciones de instalación |
| **Optional** | App arranca. Notificación en startup: feature X desactivada + instrucciones |

Dependencias actuales y futuras:

| Herramienta | Categoría | Feature que la necesita |
|------------|-----------|------------------------|
| `git` | Required | Todo — leer estado, diffs, commits |
| `gh` CLI | Optional | `pr-status` |

### Check al arrancar

En `SddTuiApp.on_mount` (o antes del primer render), se ejecuta `DepsChecker`:

```
Required missing → ErrorScreen (no TUI, solo mensaje + exit)
Optional missing → notify() por cada herramienta ausente
Optional present → no hace nada
```

**Required missing — ErrorScreen:**

```
┌─────────────────────────────────────────────────────────────┐
│ sdd-tui — dependency error                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Required dependency missing: git                            │
│                                                              │
│  Install instructions:                                       │
│                                                              │
│    macOS:   brew install git                                 │
│    Ubuntu:  sudo apt install git                             │
│    Docs:    https://git-scm.com/downloads                    │
│                                                              │
│  [q] quit                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Optional missing — notify toast:**

```
gh CLI not found — PR status disabled
Install: brew install gh  |  https://cli.github.com
```

El toast de optional es `severity="warning"` y persiste hasta que el usuario
lo descarte (timeout largo o sin timeout).

### `core/deps.py`

```python
@dataclass
class Dep:
    name: str                        # "git", "gh"
    required: bool                   # True = app no arranca sin ella
    check_cmd: list[str]             # ["git", "--version"]
    install_hint: dict[str, str]     # {"macOS": "brew install git", ...}
    feature: str | None              # None si required; "pr-status" si optional
    docs_url: str | None             # URL de documentación oficial

DEPS: list[Dep] = [...]              # registro central de todas las deps

def check_deps() -> tuple[list[Dep], list[Dep]]:
    """Returns (missing_required, missing_optional)"""
```

### Registro central de deps

Un solo lugar para añadir nuevas dependencias a medida que el proyecto crece.
Cada dep nueva que necesite una feature futura se registra aquí — la lógica
de detección y display ya está.

## Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|---------------|
| Degradación silenciosa total | El usuario no sabe por qué la feature no funciona |
| Check al usar la feature (lazy) | El usuario descubre el problema tarde, en medio del flujo |
| Lanzar excepción en el módulo | UX terrible — traceback en lugar de mensaje claro |
| Pre-flight script (CLI separado) | Requiere paso manual fuera de la TUI |

## Impacto Estimado

| Archivo | Cambio |
|---------|--------|
| `core/deps.py` | Nuevo: `Dep`, `DEPS`, `check_deps()` |
| `tui/app.py` | `on_mount` llama `check_deps()`; maneja required vs optional |
| `tui/error_screen.py` | Nuevo: `ErrorScreen` para required missing (simple, solo texto + quit) |
| `tests/test_deps.py` | Nuevo: tests unitarios con subprocess mock |

Estimación: ~4 archivos, ~10 tests nuevos.

## Criterios de Exito

- [ ] Si `git` no está disponible, la app muestra `ErrorScreen` con instrucciones y no arranca
- [ ] Si `gh` no está disponible, la app arranca y muestra notify warning con instrucciones
- [ ] Añadir una nueva dep opcional requiere solo añadir una entrada a `DEPS`
- [ ] Los checks no añaden latencia perceptible al startup (comandos `--version` son rápidos)
- [ ] Tests >= 121 (actualmente 111)
