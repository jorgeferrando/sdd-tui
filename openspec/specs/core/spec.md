# Spec: Core — openspec reader + pipeline inference + task git state

## Metadata
- **Dominio:** core
- **Change:** velocity-metrics
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** approved

## Contexto

`sdd-tui` necesita leer el estado del flujo SDD directamente desde el
sistema de archivos (`openspec/`) y desde `git`. No hay base de datos ni
estado propio — todo se infiere de huellas en disco.

El core domain es agnóstico a la TUI. Es Python puro, testable de forma
aislada.

---

## 1. Reader — Detección de changes

### Comportamiento esperado

**Dado** un directorio `openspec/` válido
**Cuando** se solicita la lista de changes activos
**Entonces** se retornan todos los subdirectorios de `openspec/changes/`
excepto `archive/`, ordenados alfabéticamente

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin changes | `changes/` existe pero está vacío (solo `archive/`) | Lista vacía `[]` |
| `openspec/` no existe | Directorio ausente | `OpenspecNotFoundError` |
| `changes/` no existe | Solo existe `openspec/` sin estructura | `OpenspecNotFoundError` |
| Archivo suelto en `changes/` | Entrada que no es directorio | Se ignora silenciosamente |

### Estructura de un Change

```python
@dataclass
class Change:
    name: str                    # nombre del directorio (ej: "bootstrap", "di-450-rate")
    path: Path                   # ruta absoluta al directorio del change
    pipeline: Pipeline           # estado inferido de cada fase
    tasks: list[Task]            # tareas con estado git poblado
    project: str = ""            # basename del proyecto origen (ej: "sdd-tui")
    project_path: Path | None = None  # raíz del repo git del proyecto
```

### Carga de task git states

**Dado** un `Change` con `tasks.md` que contiene hints de commit
**Cuando** se carga el change
**Entonces** cada `Task` tiene su `git_state` y `commit` poblados

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin `tasks.md` | Change sin tareas | `change.tasks = []` |
| Tarea sin hint | `commit_hint=None` | `git_state=PENDING`, `commit=None` |
| Hint no encontrado en log | `find_commit()` retorna `None` | `git_state=PENDING` |
| Hint encontrado | `find_commit()` retorna info | `git_state=COMMITTED`, `commit=CommitInfo` |

### Reglas de negocio

- **RB-01:** `archive/` nunca se incluye en la lista de changes activos
- **RB-02:** Solo se incluyen entradas que sean directorios (no archivos)
- **RB-03:** El orden es alfabético por nombre de directorio

---

## 2. Pipeline — Inferencia de estado por fase

Cada fase del flujo SDD deja una huella en disco. El pipeline se infiere
leyendo esas huellas — sin estado adicional.

### Fases y sus huellas

| Fase | Huella en disco | Estado ✓ si… |
|------|-----------------|--------------|
| `propose` | `proposal.md` | archivo existe |
| `spec` | `specs/*/spec.md` | al menos un archivo coincide |
| `design` | `design.md` | archivo existe |
| `tasks` | `tasks.md` | archivo existe |
| `apply` | `tasks.md` | todas las tareas están marcadas `[x]` |
| `verify` | `tasks.md` + git | apply ✓ + sin cambios sin commitear en el repo |

> **Nota:** `ship` y `archive` quedan fuera de v1.

### Estados de fase

```python
class PhaseState(Enum):
    DONE = "done"       # ✓ huella presente / condición cumplida
    PENDING = "pending" # · huella ausente
```

### Comportamiento

**Dado** un `Change` con su `path`
**Cuando** se infiere el pipeline
**Entonces** se retorna un objeto `Pipeline` con el estado de cada fase

```python
@dataclass
class Pipeline:
    propose: PhaseState
    spec:    PhaseState
    design:  PhaseState
    tasks:   PhaseState
    apply:   PhaseState
    verify:  PhaseState
```

### Casos alternativos — pipeline

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Change vacío | Sin ningún archivo | Todas las fases `PENDING` |
| tasks.md sin tareas | Archivo existe pero sin líneas `[ ]` o `[x]` | `tasks=DONE`, `apply=DONE` (vacío = completo) |
| tasks.md con mezcla | Algunas `[x]`, algunas `[ ]` | `apply=PENDING` |

### Regla de apply

- **RB-04:** `apply` es `DONE` si y solo si `tasks.md` existe Y no contiene
  ninguna tarea sin marcar (`[ ]`). Un archivo con solo tareas `[x]` o vacío
  de tareas es `DONE`.

### Regla de verify

- **RB-05:** `verify` es `DONE` si `apply=DONE` Y el working tree del repo
  está limpio (excluyendo `openspec/` y `.claude/` del check)
- **RB-06:** Si `git` no está disponible o el directorio no es un repo git,
  `verify` es `PENDING` (sin error — degradación silenciosa)

---

## 3. Task Parser — Leer tareas de tasks.md

### Formato esperado en tasks.md

```
- [x] T01 Create Command
- [x] **T02** Create Handler   ← formato con negrita (también soportado)
- [ ] T03 Update services.yaml
── amendment: descripción ──
- [ ] T04 Fix validation
  - Commit: `[change-name] Add validation`
```

### Comportamiento

**Dado** un `tasks.md` existente
**Cuando** se parsea
**Entonces** se retorna lista de `Task` en orden de aparición,
preservando los separadores de amendment como metadato

```python
@dataclass
class Task:
    id: str                   # "T01", "T02"… formato TXX obligatorio
    description: str          # texto tras el ID
    done: bool                # True si [x], False si [ ]
    amendment: str | None     # nombre del amendment al que pertenece, si aplica
    commit_hint: str | None   # extraído de "  - Commit: `...`"
    git_state: TaskGitState   # COMMITTED o PENDING (por defecto PENDING)
    commit: CommitInfo | None # solo si COMMITTED
```

### Casos alternativos — task parser

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Línea sin formato TXX | Línea de tarea sin ID válido | Se ignora (línea malformada) |
| Línea de amendment | `── amendment: foo ──` | No genera Task, setea contexto |
| Línea en blanco | Línea vacía | Se ignora |
| tasks.md vacío | Archivo existe sin contenido | Lista vacía `[]` |
| Tarea con negrita | `- [x] **T01** Desc` | Parseada correctamente |
| Tarea sin negrita | `- [x] T01 Desc` | Parseada correctamente (retrocompatible) |
| Sin hint de commit | Tarea sin línea `- Commit:` | `commit_hint=None` |
| Hint con backticks | `` - Commit: `[x] msg` `` | hint = `[x] msg` (sin backticks) |

### Reglas de negocio

- **RB-07:** El parser debe aceptar tanto `T01` como `**T01**` (con o sin negrita markdown).
- **RB-07b:** El parser acepta cualquier prefijo de letras mayúsculas seguido de dígitos: `T01`, `BUG01`, `MEJ01`, etc.
- **RB-08:** El `commit_hint` se extrae eliminando los backticks envolventes si los hay.
- **RB-09:** Solo se captura el hint de la línea inmediatamente siguiente a la tarea (indentada con 2+ espacios).

---

## 4. Git Reader — Estado del working tree y commits

### is_clean — Estado del working tree

**Dado** un path de directorio
**Cuando** se consulta si el working tree está limpio
**Entonces** se resuelve el git toplevel desde el path dado, se ejecuta
`git status --porcelain -- . :(exclude)openspec/ :(exclude).claude/`
desde el toplevel, y se retorna `True` si la salida está vacía, `False` en caso contrario

### find_commit — Búsqueda de commit por mensaje

**Dado** un fragmento de mensaje de commit y un directorio de repo git
**Cuando** se busca en git log
**Entonces** se retorna el `CommitInfo` del commit más reciente que coincide,
o `None` si no se encuentra

```python
@dataclass
class CommitInfo:
    hash: str     # hash corto de 7 caracteres
    message: str  # mensaje completo del commit

class TaskGitState(Enum):
    COMMITTED = "committed"  # encontrado en git log
    PENDING   = "pending"    # no encontrado
```

### Casos alternativos — git reader

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| No es repo git | `git status` / `git log` falla | Retorna `None` |
| git no instalado | Comando no encontrado | Retorna `None` |
| Commit encontrado | `git log --grep` retorna línea | `CommitInfo(hash, message)` |
| No encontrado | Salida vacía | `None` |
| `message_fragment` es `None` | Sin hint | `None` (sin llamar a git) |

### Reglas de negocio

- **RB-10:** El hash siempre tiene 7 caracteres (`--abbrev-commit`).
- **RB-11:** Si `commit_hint` es `None`, no se ejecuta git — retorna `None` directamente.
- **RB-11b:** `find_commit` usa `--grep` con flag `-F` (fixed-strings) para que los corchetes en nombres de change (`[view-3]`) no se interpreten como regex.

---

## 5. Git Reader — get_diff y get_working_diff

### get_diff — Diff de un commit concreto

**Dado** un hash de commit y un path de repo
**Cuando** se llama a `get_diff(commit_hash, cwd)`
**Entonces** se ejecuta `git show --no-color {hash}` y se retorna el output como `str`

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Hash válido | `git show` retorna output | `str` con el diff completo (incluye header del commit) |
| Hash inválido o `None` | `git show` falla o hash es falsy | `None` |
| No es repo git | Comando falla | `None` |
| git no instalado | `FileNotFoundError` | `None` |

- **RB-12:** Si `commit_hash` es `None` o vacío, retorna `None` sin ejecutar git.
- **RB-13:** Errores de subprocess se capturan silenciosamente — retorna `None`.
- **RB-14:** El output incluye el header del commit (`commit`, `Author`, `Date`, mensaje) seguido del diff.

### get_working_diff — Diff del working tree actual

**Dado** un path de repo git
**Cuando** se llama a `get_working_diff(cwd)`
**Entonces** se ejecuta `git diff HEAD --no-color` y se retorna el output como `str`

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Hay cambios pendientes | `git diff HEAD` retorna output | `str` con el diff |
| Working tree limpio | `git diff HEAD` retorna vacío | `None` |
| Error de git | returncode != 0 o git no instalado | `None` |

- **RB-15:** `git diff HEAD` incluye cambios staged y unstaged respecto al último commit.
- **RB-16:** Si el output es string vacío, se retorna `None` (repo limpio).

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Inferencia sin estado propio | Base de datos SQLite | Máxima simplicidad, fuente de verdad = disco |
| `git status --porcelain` via subprocess | pygit2 / gitpython | Sin dependencias extra, git asumido instalado |
| Dataclasses para modelos | TypedDict / Pydantic | Suficiente para v1, sin overhead |
| `OpenspecNotFoundError` en lugar de `[]` | Retornar lista vacía | Distinguir "no hay changes" de "no hay openspec" |
| IDs de tarea siempre `TXX` | IDs libres | Formato fijo → parseado predecible, líneas sin ID ignoradas |
| Hint de commit en tasks.md | Buscar por TXX en git log | Formato de commit no incluye TXX; hint es preciso |
| `git log --grep` | `git log --all` manual | Comando nativo, un resultado basta |
| `TaskGitState` independiente de `done` | Unificar en un solo campo | `done` = estado en tasks.md; `git_state` = realidad en git. Pueden diferir |
| Hash 7 chars | Hash completo | Estándar git, suficiente para display |
| `find_commit` usa `-F` (fixed-strings) | grep regex por defecto | `[view-3]` como regex es clase de caracteres, nunca coincide |
| Transport Protocol eliminado (TmuxTransport, ZellijTransport, detect_transport) | Mantener como feature activa | Complejidad sin retorno: tmux/zellij targeting no fiable. Eliminado en cleanup-remove-transports (2026-03-03) |
| `git show` para diff de commit | `git diff {hash}^..{hash}` | `git show` incluye metadata del commit |
| `get_working_diff` retorna `None` si vacío | Retornar `""` | Permite distinción entre "sin cambios" y "error" en la TUI |
| TaskParser acepta `[A-Z]+\d+` | Solo `T\d+` | BUG01, MEJ01 son IDs válidos en el flujo SDD |

## Abierto / Pendiente

Ninguno.

---

## 12. Velocity — Throughput y Lead Time

### Propósito

Módulo `core/velocity.py` — infiere métricas de throughput y lead time del proceso SDD
a partir de `git log` sobre los changes archivados. Sin estado propio, sin dependencias nuevas.

### Modelo de Datos

```python
@dataclass
class ChangeVelocity:
    name: str                      # nombre del change (sin prefijo de fecha)
    project: str                   # basename del proyecto (resuelto de archive_dir)
    start_date: date | None        # fecha del primer commit del change
    end_date: date | None          # fecha del último commit del change
    lead_time_days: int | None     # end_date - start_date en días

@dataclass
class VelocityReport:
    changes: list[ChangeVelocity] = field(default_factory=list)
    weekly_throughput: list[tuple[date, int]] = field(default_factory=list)
    median_lead_time: float | None = None
    p90_lead_time: float | None = None
    slowest_change: ChangeVelocity | None = None
```

### `compute_velocity(archive_dirs, cwd) -> VelocityReport`

Para cada `archive_dir`:
1. `project_path = archive_dir.resolve().parent.parent.parent`
2. Iterar subdirectorios con prefijo `YYYY-MM-DD-`; extraer `change_name = dir.name.split("-", 3)[3]`
3. `git log --format=%ad --date=short -F --grep=[{change_name}]` — primera línea = end, última = start
4. `lead_time = (end - start).days`

Throughput: últimas 8 semanas ISO (lunes de cada semana); contar changes con `end_date` en el rango.

### Requisitos

- **REQ-VM01** `[Event]` When `compute_velocity(archive_dirs, cwd)` is called, the system SHALL return a `VelocityReport` aggregated from all archive dirs.
- **REQ-VM02** `[Ubiquitous]` The system SHALL infer start_date as the first git commit containing `[{change_name}]`.
- **REQ-VM03** `[Ubiquitous]` The system SHALL infer end_date as the last git commit containing `[{change_name}]`.
- **REQ-VM04** `[Ubiquitous]` The lead time SHALL be `end_date - start_date` in days.
- **REQ-VM05** `[Unwanted]` If no commits found, the system SHALL set all dates to `None` without raising.
- **REQ-VM06** `[Ubiquitous]` Throughput SHALL be computed per ISO week for the last 8 weeks.
- **REQ-VM07** `[Unwanted]` If a change has no `end_date`, it SHALL be excluded from calculations.
- **REQ-VM08** `[Ubiquitous]` `median_lead_time` and `p90_lead_time` SHALL aggregate across all projects.
- **REQ-VM09** `[Unwanted]` If fewer than 2 changes have lead time data, both SHALL be `None`.
- **REQ-VM10** `[Optional]` Where multi-project, the system SHALL aggregate all archive_dirs.
- **REQ-VM11** `[Unwanted]` If git fails, the system SHALL return an empty `VelocityReport` without raising.
- **REQ-VM12** `[Ubiquitous]` git queries SHALL use `-F` (fixed-strings).

### Casos Alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| archive/ vacío | Sin subdirectorios fecha | `VelocityReport` vacío |
| Subdirectorio sin prefijo fecha | Nombre inválido | Ignorado silenciosamente |
| Change sin commits | `git log` vacío | `ChangeVelocity` con fechas `None` |
| Un solo change con datos | `len(lead_times) == 1` | `median=None`, `p90=None` |
| git no instalado | `FileNotFoundError` | `VelocityReport` vacío |
| archive_dir no existe | Path ausente | Omitido silenciosamente |

### Reglas de negocio

- **RB-VL1:** `project_path = archive_dir.resolve().parent.parent.parent` — usa `.resolve()` para manejar rutas relativas.
- **RB-VL2:** `statistics.median` (stdlib) para median; P90 manual: `sorted[int(0.9 * len)]`.
- **RB-VL3:** `compute_velocity` no lanza excepciones — todos los errores se degradan silenciosamente.

---

## 11. Multi-project Config — AppConfig y load_all_changes

### Propósito

Módulo `core/config.py` — parser manual de `~/.sdd-tui/config.yaml`. Sin dependencias nuevas.
Módulo `core/reader.py` — `load_all_changes()` como punto de entrada multi-proyecto.

### Modelo

```python
@dataclass
class ProjectConfig:
    path: Path          # absoluto (expandido de ~)

@dataclass
class AppConfig:
    projects: list[ProjectConfig]  # vacío → single-project (legacy)
```

### `load_config() -> AppConfig`

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Config no existe | `~/.sdd-tui/config.yaml` ausente | `AppConfig(projects=[])` |
| Config sin `projects` key | YAML válido pero sin la clave | `AppConfig(projects=[])` |
| Config malformada | YAML inválido | `AppConfig(projects=[])` — sin excepción |
| Path con `~` | `path: ~/sites/sdd-tui` | Expandido con `Path.expanduser().resolve()` |

### `load_all_changes(config: AppConfig, cwd: Path, include_archived: bool = False) -> list[Change]`

Retorna lista plana de `Change`. La agrupación por proyecto se infiere de `change.project` en la TUI.

**Dado** `config.projects == []` (legacy)
**Entonces** equivale exactamente a `OpenspecReader.load(cwd / "openspec", include_archived, project_path=cwd)`.

**Dado** `config.projects` con N entradas
**Entonces** agrega changes de todos los proyectos válidos; proyectos con `OpenspecNotFoundError` se omiten silenciosamente.

### `OpenspecReader.load()` — parámetro `project_path`

```python
def load(self, openspec_path, include_archived=False, project_path=None):
    proj = project_path or openspec_path.parent
    # Cada Change lleva project=proj.name, project_path=proj
```

### Requisitos

- **REQ-01** `[Optional]` Where `~/.sdd-tui/config.yaml` exists and declares multiple projects, the system SHALL load changes from all declared project paths.
- **REQ-02** `[Ubiquitous]` The system SHALL use `Path.cwd()` as the single project when no config file exists.
- **REQ-03** `[Unwanted]` If a declared project path does not exist or has no `openspec/`, the system SHALL skip it silently.
- **REQ-04** `[Ubiquitous]` Each `Change` SHALL carry `project: str` and `project_path: Path`.
- **REQ-05** `[Ubiquitous]` In single-project mode, `Change.project` SHALL be the basename of `Path.cwd()`.
- **REQ-06** `[Unwanted]` If `config.yaml` is malformed, the system SHALL fall back to single-project mode silently.

### Reglas de negocio

- **RB-CFG1:** `config.yaml` se evalúa una vez al inicio — no se recarga en `r` (refresh).
- **RB-CFG2:** El path del proyecto se expande con `Path.expanduser().resolve()`.
- **RB-CFG3:** Errores de I/O, YAML o paths inválidos → `AppConfig(projects=[])` — nunca excepción.
- **RB-CFG4:** `load_all_changes` con `projects == []` equivale exactamente al comportamiento legacy.
- **RB-CFG5:** `Change.project_path` es la raíz del repo — todas las operaciones git del change usan este path.

---

## 8. Spec Parser — Delta format + decisions extractor

### Propósito

Módulo `core/spec_parser.py` — Python puro, sin dependencias de TUI, testable de forma aislada.
Dos capacidades: parsear secciones ADDED/MODIFIED/REMOVED de delta specs, y extraer
la tabla de decisiones de `design.md` archivados.

### `parse_delta` — Parser de delta spec

**Dado** un `spec_path: Path`
**Cuando** se llama a `parse_delta(spec_path)`
**Entonces** se retorna un `DeltaSpec` con las líneas bajo cada sección reconocida

```python
@dataclass
class DeltaSpec:
    added: list[str]      # líneas bajo ## ADDED
    modified: list[str]   # líneas bajo ## MODIFIED
    removed: list[str]    # líneas bajo ## REMOVED
    fallback: bool        # True si no hay marcadores → mostrar texto plano
```

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Con marcadores | `## ADDED/MODIFIED/REMOVED` presentes | `fallback=False`, listas pobladas |
| Sin marcadores | Ninguna sección reconocida | `DeltaSpec(fallback=True)`, listas vacías |
| Case-insensitive | `## added` o `## ADDED` | Ambas formas reconocidas |
| Líneas entre secciones | Blank lines en sección | Preservadas en la lista |

### `extract_decisions` — Extractor de decisiones

**Dado** un `design_path: Path` y un `change_name: str`
**Cuando** se llama a `extract_decisions(design_path, change_name)`
**Entonces** se retorna un `ChangeDecisions` con las filas de la tabla de decisiones

```python
@dataclass
class Decision:
    decision: str
    alternative: str
    reason: str

@dataclass
class ChangeDecisions:
    change_name: str       # nombre sin prefijo de fecha
    archive_date: date     # fecha del prefijo del directorio (rellenado por collect)
    decisions: list[Decision]
```

Reconoce tanto `## Decisiones Tomadas` como `## Decisiones de Diseño` (y variantes sin tilde).

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| `design.md` no existe | Archivo ausente | `ChangeDecisions` con `decisions=[]` |
| Sin tabla de decisiones | No hay `##` de decisiones | `decisions=[]` |
| Tabla presente | Filas `\| col1 \| col2 \| col3 \|` | Lista de `Decision` |

### `collect_archived_decisions` — Agregador por archive

**Dado** un `archive_dir: Path`
**Cuando** se llama a `collect_archived_decisions(archive_dir)`
**Entonces** itera subdirectorios con prefijo `YYYY-MM-DD-`, extrae decisiones de cada `design.md`,
y retorna lista `ChangeDecisions` ordenada por fecha ascendente

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Directorio no existe | `archive_dir` ausente | `[]` |
| Directorio sin prefijo YYYY-MM-DD | Nombre inválido | Ignorado silenciosamente |
| Prefijo con fecha inválida | `ValueError` en `date.fromisoformat` | Ignorado silenciosamente |

### Reglas de negocio

- **RB-SP-01:** `parse_delta` usa `errors="replace"` al leer el archivo — nunca lanza UnicodeDecodeError.
- **RB-SP-02:** `fallback=True` en lugar de excepción cuando no hay marcadores — specs legacy funcionales.
- **RB-SP-03:** `collect_archived_decisions` ordena por prefijo YYYY-MM-DD del nombre de directorio — no por metadata interna.
- **RB-SP-04:** `change_name` en `ChangeDecisions` es el nombre semántico sin el prefijo de fecha.

---

## 7. Metrics — Calidad de specs por change

### Propósito

Módulo `core/metrics.py` — Python puro, sin dependencias de TUI, testable de forma aislada.
Extrae métricas de calidad de un change: requisitos EARS, artefactos presentes, e inactividad git.

### `parse_metrics` — Función principal

**Dado** un `change_path` y un `repo_cwd`
**Cuando** se llama a `parse_metrics(change_path, repo_cwd)`
**Entonces** se retorna un `ChangeMetrics` con `req_count`, `ears_count`, `artifacts` e `inactive_days`

```python
@dataclass
class ChangeMetrics:
    req_count: int            # REQ únicos detectados
    ears_count: int           # REQ únicos con tipo EARS válido
    artifacts: list[str]      # orden fijo: proposal, spec, research, design, tasks
    inactive_days: int | None # días desde último commit del change (None si no hay o falla git)

INACTIVE_THRESHOLD_DAYS: int = 7
```

### Conteo de REQ únicos

**Dado** specs bajo `{change_path}/specs/`
**Cuando** se parsean
**Entonces** se detectan líneas que contienen `**REQ-XX**` (patrón `\*\*(REQ-\d+)\*\*`),
acumulando IDs únicos — el mismo REQ apareciendo en definición y en escenario cuenta solo una vez.

Un REQ se cuenta como EARS-typed si **alguna** de sus apariciones contiene uno de:
`[Event]`, `[State]`, `[Unwanted]`, `[Optional]`, `[Ubiquitous]`.

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin specs/ | Directorio ausente | `req_count=0`, `ears_count=0` |
| REQ en definición + escenario | Mismo ID, dos líneas | Cuenta como 1 único |
| REQ sin tag EARS | Solo aparece sin tag | `req_count+1`, `ears_count` sin cambio |

### Detección de artefactos

Orden fijo; `research` solo si el archivo existe:

| Artefacto | Huella en disco |
|-----------|----------------|
| `proposal` | `proposal.md` |
| `spec` | `specs/*/spec.md` (al menos uno) |
| `research` | `research.md` (opcional) |
| `design` | `design.md` |
| `tasks` | `tasks.md` |

### Días de inactividad

**Dado** un change name
**Cuando** se ejecuta `git log --format=%ad --date=short -1 -F --grep={change_name}`
**Entonces** se retorna `(date.today() - commit_date).days`

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin commits del change | Salida vacía | `None` |
| git no disponible | `FileNotFoundError` | `None` |
| No es repo git | returncode != 0 | `None` |

### Reglas de negocio

- **RB-M1:** `parse_metrics` no lanza excepciones — todos los errores se degradan silenciosamente.
- **RB-M2:** El conteo de REQs usa IDs únicos (no ocurrencias). Un mismo REQ en varias líneas cuenta como uno.
- **RB-M3:** `INACTIVE_THRESHOLD_DAYS = 7` es constante exportada — no hardcodeada en la TUI.
- **RB-M4:** `git log` usa `-F` (fixed-strings) para que `[view-8]` no se interprete como regex.
- **RB-M5:** Si existe `requirements.md` en el change, `parse_metrics` lo escanea además de `specs/*/spec.md` para conteo de REQs (IDs únicos — union de ambas fuentes).
- **RB-M6:** El orden de artefactos es fijo: `proposal`, `spec`, `research`, `requirements`, `design`, `tasks`.

---

## 9. Reader — load_steering y load_spec_json

### `load_steering(openspec_path: Path) -> str | None`

**Dado** un path al directorio `openspec/`
**Cuando** se llama a `load_steering(openspec_path)`
**Entonces** se retorna el contenido de `openspec/steering.md` como `str`,
o `None` si el archivo no existe

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Archivo existe | `steering.md` presente | `str` con el contenido completo |
| Archivo ausente | No existe `steering.md` | `None` |
| Archivo vacío | Existe pero sin contenido | `""` (string vacío) |
| Error de encoding | Caracteres inválidos | Reemplazados con `errors="replace"` — nunca lanza `UnicodeDecodeError` |

### `load_spec_json(change_path: Path) -> dict | None`

**Dado** un path al directorio de un change
**Cuando** se llama a `load_spec_json(change_path)`
**Entonces** se retorna el dict parseado de `spec.json`, o `None` si no existe o está malformado

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| JSON válido | `spec.json` presente y parseable | `dict` con los datos |
| Archivo ausente | No existe `spec.json` | `None` |
| JSON malformado | `json.JSONDecodeError` | `None` (excepción capturada) |
| Error de I/O | `OSError` | `None` (excepción capturada) |

### spec.json — Formato

```json
{
  "format": "openspec",
  "version": "1.0",
  "change": "string — nombre del change",
  "generated_at": "ISO 8601 timestamp",
  "pipeline": {
    "propose": "done|pending",
    "spec": "done|pending",
    "design": "done|pending",
    "tasks": "done|pending",
    "apply": "done|pending",
    "verify": "done|pending"
  },
  "tasks": {
    "total": 0,
    "done": 0,
    "pending": 0
  },
  "requirements": ["REQ-01", "REQ-02"]
}
```

### Reglas de negocio

- **RB-R01:** `spec.json` es informacional — la TUI y la inferencia de pipeline siempre recomputan desde disco. `spec.json` no es fuente de verdad.
- **RB-R02:** `load_spec_json` captura tanto `json.JSONDecodeError` como `OSError` — nunca lanza excepción.
- **RB-R03:** `load_steering` usa `errors="replace"` al leer — nunca lanza `UnicodeDecodeError`.

---

## 10. Deps — Detección de dependencias externas

### Propósito

Módulo `core/deps.py` — registro central de herramientas externas que la app requiere o puede aprovechar.
Proporciona detección uniforme y datos de instalación por plataforma.

### Modelo `Dep`

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

### Registro `DEPS`

Lista estática — única fuente de verdad de dependencias externas.

| `name` | `required` | `feature` |
|--------|-----------|-----------|
| `git`  | `True`    | `None` |
| `gh`   | `False`   | `"pr-status"` |

### `check_deps() -> tuple[list[Dep], list[Dep]]`

Retorna `(missing_required, missing_optional)`.

- **REQ-01** `[Ubiquitous]` The `check_deps()` function SHALL detect a dependency as missing when its `check_cmd` raises `FileNotFoundError` OR returns a non-zero exit code.
- **REQ-02** `[Ubiquitous]` The `check_deps()` function SHALL detect a dependency as present when its `check_cmd` exits with code 0.
- **REQ-03** `[Ubiquitous]` Each dependency check SHALL be independent — failure of one SHALL NOT prevent checking the rest.

### Reglas de negocio

- **RB-D1:** `check_deps()` captura `FileNotFoundError` — nunca lanza excepción.
- **RB-D2:** Los checks usan `capture_output=True` — no contaminan stdout/stderr.
- **RB-D3:** `DEPS` es la única fuente de verdad — ningún check de deps existe fuera de `core/deps.py`.

