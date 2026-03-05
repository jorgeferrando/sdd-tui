# Spec: Core — Dependency Checker

## Metadata
- **Dominio:** core
- **Change:** startup-deps-check
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** draft

## Contexto

`sdd-tui` usa herramientas externas (git, y en el futuro gh CLI). Sin un registro
central de dependencias, cada módulo falla silenciosamente de forma distinta.
`core/deps.py` centraliza la detección y proporciona información de instalación.

---

## 1. Modelo — `Dep`

```python
@dataclass
class Dep:
    name: str                        # "git", "gh"
    required: bool                   # True → app no arranca sin ella
    check_cmd: list[str]             # ["git", "--version"]
    install_hint: dict[str, str]     # {"macOS": "brew install git", "Ubuntu": "sudo apt install git"}
    docs_url: str | None             # URL canónica de instalación
    feature: str | None              # None si required; nombre de feature si optional
```

---

## 2. Registro `DEPS`

Lista estática que es la única fuente de verdad de las dependencias externas.
Toda dep nueva se añade aquí — la lógica de detección y display ya existe.

Registro inicial:

| `name` | `required` | `check_cmd` | `feature` |
|--------|-----------|-------------|-----------|
| `git` | `True` | `["git", "--version"]` | `None` |
| `gh` | `False` | `["gh", "--version"]` | `"pr-status"` |

---

## 3. `check_deps()` — Detección

### Comportamiento

- **REQ-01** `[Ubiquitous]` The `check_deps()` function SHALL return a tuple `(missing_required: list[Dep], missing_optional: list[Dep])`.
- **REQ-02** `[Ubiquitous]` The `check_deps()` function SHALL detect a dependency as **missing** when its `check_cmd` raises `FileNotFoundError` OR returns a non-zero exit code.
- **REQ-03** `[Ubiquitous]` The `check_deps()` function SHALL detect a dependency as **present** when its `check_cmd` exits with code 0, regardless of stdout/stderr content.
- **REQ-04** `[Ubiquitous]` The `DEPS` list SHALL be the single source of truth — no dependency check SHALL exist outside of `core/deps.py`.

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Comando no encontrado | `FileNotFoundError` al llamar `subprocess.run` | Dep considerada missing |
| Comando falla | returncode != 0 | Dep considerada missing |
| Comando exitoso | returncode == 0 | Dep considerada presente |
| Todas presentes | Todas las `check_cmd` → code 0 | `([], [])` |
| Múltiples missing | Varias deps ausentes | Ambas listas pobladas correctamente |

### Reglas de negocio

- **RB-D1:** `check_deps()` captura `FileNotFoundError` y `subprocess.CalledProcessError` — nunca lanza excepción.
- **RB-D2:** Los checks se ejecutan con `capture_output=True` — no contaminan stdout/stderr de la app.
- **RB-D3:** Cada check es independiente — el fallo de uno no impide comprobar los siguientes.

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| `check_cmd` como lista de strings | String único | `subprocess.run` prefiere lista; evita shell injection |
| `install_hint: dict[str, str]` | String plano | Permite mostrar instrucción específica por plataforma |
| `DEPS` estática en módulo | Config file | Las deps son código, no configuración de usuario |
| `FileNotFoundError` OR non-zero | Solo `FileNotFoundError` | `gh --version` puede existir pero fallar (auth); ambos casos = missing |

## Abierto / Pendiente

Ninguno.
