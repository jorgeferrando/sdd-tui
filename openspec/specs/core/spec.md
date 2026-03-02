# Spec: Core — openspec reader + pipeline inference + task git state

## Metadata
- **Dominio:** core
- **Change:** view-2-change-detail
- **Fecha:** 2026-03-02
- **Versión:** 0.2
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
    name: str          # nombre del directorio (ej: "bootstrap", "di-450-rate")
    path: Path         # ruta absoluta al directorio del change
    pipeline: Pipeline # estado inferido de cada fase
    tasks: list[Task]  # tareas con estado git poblado
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
  está limpio (`git status --porcelain` retorna vacío)
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
- **RB-08:** El `commit_hint` se extrae eliminando los backticks envolventes si los hay.
- **RB-09:** Solo se captura el hint de la línea inmediatamente siguiente a la tarea (indentada con 2+ espacios).

---

## 4. Git Reader — Estado del working tree y commits

### is_clean — Estado del working tree

**Dado** un path de directorio
**Cuando** se consulta si el working tree está limpio
**Entonces** se ejecuta `git status --porcelain` y se retorna `True` si
la salida está vacía, `False` en caso contrario

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

## Abierto / Pendiente

Ninguno.
