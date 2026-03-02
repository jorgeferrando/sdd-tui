# Spec: Core — Task git state + CommitInfo (delta v0.2)

## Metadata
- **Dominio:** core
- **Change:** view-2-change-detail
- **Fecha:** 2026-03-02
- **Versión:** 0.2
- **Estado:** draft

## Contexto

Extensión del dominio core para soportar estado git por tarea individual.
View 2 necesita saber si cada tarea está commiteada en git (con su hash)
o pendiente.

---

## 1. Task — Extensión del modelo

### Comportamiento actual

`Task` tiene: `id`, `description`, `done`, `amendment`.
`done` refleja el estado en `tasks.md` (`[x]`/`[ ]`).

### Nuevos campos

```python
@dataclass
class CommitInfo:
    hash: str     # hash corto de 7 caracteres
    message: str  # mensaje completo del commit

class TaskGitState(Enum):
    COMMITTED = "committed"  # encontrado en git log
    PENDING   = "pending"    # no encontrado

@dataclass
class Task:
    id: str
    description: str
    done: bool
    amendment: str | None = None
    commit_hint: str | None = None   # ← nuevo: extraído de "- Commit: ..."
    git_state: TaskGitState = TaskGitState.PENDING  # ← nuevo
    commit: CommitInfo | None = None  # ← nuevo: solo si COMMITTED
```

---

## 2. TaskParser — Extensiones

### Comportamiento actual

Parsea líneas `- [x] T01 Description` con regex `T\d+`.

### Bug a corregir

El formato real de `tasks.md` usa negrita: `- [x] **T01** Description`.
El parser actual no maneja este caso — las tareas no son detectadas.

- **RB-07:** El parser debe aceptar tanto `T01` como `**T01**` (con o sin negrita markdown).

### Nueva funcionalidad: captura de commit hint

Líneas inmediatamente tras una tarea con formato `  - Commit: \`...\`` se
asocian a la tarea anterior como `commit_hint`.

**Dado** un `tasks.md` con:
```
- [x] **T01** Create pyproject.toml
  - Commit: `[bootstrap] Add pyproject.toml`
```
**Cuando** se parsea
**Entonces** `tasks[0].commit_hint == "[bootstrap] Add pyproject.toml"`
(sin los backticks envolventes)

### Casos alternativos — TaskParser v0.2

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin hint de commit | Tarea sin línea `- Commit:` | `commit_hint=None` |
| Hint con backticks | `` - Commit: `[x] msg` `` | hint = `[x] msg` (sin backticks) |
| Hint sin backticks | `- Commit: [x] msg` | hint = `[x] msg` |
| Tarea con negrita | `- [x] **T01** Desc` | Parseada correctamente |
| Tarea sin negrita | `- [x] T01 Desc` | Parseada correctamente (retrocompatible) |

- **RB-08:** El `commit_hint` se extrae eliminando los backticks envolventes si los hay.
- **RB-09:** Solo se captura el hint de la línea inmediatamente siguiente a la tarea (indentada con 2+ espacios).

---

## 3. GitReader — find_commit()

### Comportamiento esperado

**Dado** un fragmento de mensaje de commit y un directorio de repo git
**Cuando** se busca en git log
**Entonces** se retorna el `CommitInfo` del commit más reciente que coincide,
o `None` si no se encuentra

```python
def find_commit(self, message_fragment: str, cwd: Path) -> CommitInfo | None:
    # git log --oneline --grep="fragment" -1
    # Si hay resultado → CommitInfo(hash=7chars, message=full_line)
    # Si no hay resultado → None
    # Si git falla → None
```

### Casos alternativos — find_commit

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Commit encontrado | `git log --grep` retorna línea | `CommitInfo(hash, message)` |
| No encontrado | Salida vacía | `None` |
| No es repo git | `git log` falla | `None` |
| `message_fragment` es `None` | Sin hint | `None` (sin llamar a git) |

- **RB-10:** El hash siempre tiene 7 caracteres (`--abbrev-commit`).
- **RB-11:** Si `commit_hint` es `None`, no se ejecuta git — retorna `None` directamente.

---

## 4. Reader — Población de task git states

### Comportamiento esperado

**Dado** un `Change` con `tasks.md` que contiene hints de commit
**Cuando** se carga el change
**Entonces** cada `Task` tiene su `git_state` y `commit` poblados

**Dado** que `TaskGitState.COMMITTED` requiere que `find_commit()` retorne resultado
**Entonces** `task.git_state = COMMITTED` y `task.commit = CommitInfo(...)`

### Casos alternativos — Reader con git states

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Sin `tasks.md` | Change sin tareas | `change.tasks = []` |
| Tarea sin hint | `commit_hint=None` | `git_state=PENDING`, `commit=None` |
| Hint no encontrado en log | `find_commit()` retorna `None` | `git_state=PENDING` |
| Hint encontrado | `find_commit()` retorna info | `git_state=COMMITTED`, `commit=CommitInfo` |

### Nuevo campo en Change

```python
@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline = field(default_factory=Pipeline)
    tasks: list[Task] = field(default_factory=list)  # ← nuevo
```

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Hint de commit en tasks.md | Buscar por TXX en git log | Formato de commit no incluye TXX; hint es preciso |
| `git log --grep` | `git log --all` manual | Comando nativo, un resultado basta |
| `TaskGitState` independiente de `done` | Unificar en un solo campo | `done` = estado en tasks.md; `git_state` = realidad en git. Pueden diferir |
| Hash 7 chars | Hash completo | Estándar git, suficiente para display |

## Abierto / Pendiente

Ninguno.
