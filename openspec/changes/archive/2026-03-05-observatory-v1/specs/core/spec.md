# Spec: Core — Multi-project Config Loader

## Metadata
- **Dominio:** core
- **Change:** observatory-v1
- **Fecha:** 2026-03-05
- **Versión:** 0.1
- **Estado:** draft

## Contexto

Hasta `observatory-v1`, la app lee changes de un único proyecto: `Path.cwd()`.
Este delta añade soporte para una config global opcional en `~/.sdd-tui/config.yaml`
que declara múltiples proyectos. Si la config no existe, el comportamiento es idéntico al actual.

---

## Requisitos (EARS)

- **REQ-01** `[Optional]` Where `~/.sdd-tui/config.yaml` exists and declares multiple projects, the system SHALL load changes from all declared project paths.
- **REQ-02** `[Ubiquitous]` The system SHALL use `Path.cwd()` as the single project when no config file exists.
- **REQ-03** `[Unwanted]` If a declared project path does not exist or has no `openspec/` directory, the system SHALL skip that project silently without error.
- **REQ-04** `[Ubiquitous]` Each `Change` SHALL carry `project: str` (basename of the project root) and `project_path: Path` (absolute path to the project root).
- **REQ-05** `[Ubiquitous]` In single-project mode (legacy), `Change.project` SHALL be the basename of `Path.cwd()`.
- **REQ-06** `[Unwanted]` If `~/.sdd-tui/config.yaml` is malformed YAML or has no `projects` key, the system SHALL fall back to single-project mode (legacy) silently.

## Modelo — `AppConfig`

```python
@dataclass
class ProjectConfig:
    path: Path          # absoluto (expandido de ~)

@dataclass
class AppConfig:
    projects: list[ProjectConfig]  # vacío → single-project (legacy)
```

## `core/config.py` — Funciones

### `load_config() -> AppConfig`

**Dado** que se llama a `load_config()`
**Cuando** `~/.sdd-tui/config.yaml` existe y es válida
**Entonces** retorna `AppConfig` con la lista de proyectos declarados

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Config no existe | `~/.sdd-tui/config.yaml` ausente | `AppConfig(projects=[])` |
| Config sin `projects` key | YAML válido pero sin la clave | `AppConfig(projects=[])` |
| Config malformada | YAML inválido | `AppConfig(projects=[])` — sin excepción |
| Path con `~` | `path: ~/sites/sdd-tui` | Expandido con `Path.expanduser()` |
| Config válida | Lista de paths | `AppConfig` poblado |

## `core/reader.py` — Nuevas funciones

### `load_changes(path: Path, project_path: Path | None = None) -> list[Change]`

Versión extendida de la actual — acepta `project_path` explícito.
Si `project_path` es `None`, usa `path` como `project_path` (compatibilidad legacy).

Cada `Change` en el resultado lleva `project = project_path.name` y `project_path = project_path`.

### `load_all_changes(config: AppConfig, cwd: Path) -> list[tuple[str, list[Change]]]`

**Dado** un `AppConfig`
**Cuando** `config.projects` está vacío (modo legacy)
**Entonces** retorna `[("", load_changes(cwd / "openspec", project_path=cwd))]`
— la clave vacía indica que no hay separador de proyecto en la UI.

**Dado** un `AppConfig`
**Cuando** `config.projects` tiene N entradas
**Entonces** retorna lista de `(project_name, changes)` para cada proyecto válido,
omitiendo los proyectos que lanzan `OpenspecNotFoundError`.

```python
def load_all_changes(config: AppConfig, cwd: Path) -> list[tuple[str, list[Change]]]:
    """Returns list of (project_name, changes). project_name='' means legacy/no separator."""
```

## Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Todos los proyectos fallan | Todos lanzan `OpenspecNotFoundError` | Retorna `[]` |
| Un proyecto válido en config | Solo uno con openspec/ | Retorna `[("nombre", changes)]` con separador |
| Config vacía | `projects: []` | Comportamiento idéntico a legacy (`cwd`) |

## Reglas de negocio

- **RB-CFG1:** `~/.sdd-tui/config.yaml` se evalúa una vez al inicio de la app — no se relanza en `r` (refresh).
- **RB-CFG2:** El path del proyecto se expande siempre con `Path.expanduser().resolve()`.
- **RB-CFG3:** Errores de I/O, YAML o paths inválidos → `AppConfig(projects=[])` — nunca excepción.
- **RB-CFG4:** `load_all_changes` con `config.projects == []` equivale exactamente a `load_changes(cwd / "openspec")` — ningún comportamiento nuevo.
- **RB-CFG5:** `Change.project_path` es la raíz del repo git del proyecto — todas las operaciones git del change usan este path como `cwd`.

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `~/.sdd-tui/config.yaml` | `~/.config/sdd-tui/config.yaml` (XDG) | Más simple y discoverable |
| `AppConfig(projects=[])` como legacy | Flags separados | Un único retorno para dos modos simplifica el caller |
| `list[tuple[str, list[Change]]]` | Dict | Preserva orden de declaración en config |
| project_name vacío para legacy | `None` | Más fácil de comprobar en la TUI: `if project_name` |
| `load_config()` captura todos los errores | Lanzar excepción | Degradación silenciosa — coherente con el resto del core |

## Abierto / Pendiente

Ninguno.
