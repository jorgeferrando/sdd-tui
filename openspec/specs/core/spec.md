# Spec: Core — openspec reader + pipeline inference

## Metadata
- **Dominio:** core
- **Change:** bootstrap
- **Fecha:** 2026-03-02
- **Versión:** 0.1
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
```

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
- [ ] T02 Create Handler
- [x] T03 Update services.yaml
── amendment: descripción ──
- [ ] T04 Fix validation
```

### Comportamiento

**Dado** un `tasks.md` existente
**Cuando** se parsea
**Entonces** se retorna lista de `Task` en orden de aparición,
preservando los separadores de amendment como metadato

```python
@dataclass
class Task:
    id: str            # "T01", "T02"… formato TXX obligatorio
    description: str   # texto tras el ID
    done: bool         # True si [x], False si [ ]
    amendment: str | None  # nombre del amendment al que pertenece, si aplica
```

### Casos alternativos — task parser

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Línea sin formato TXX | Línea de tarea sin ID válido | Se ignora (línea malformada) |
| Línea de amendment | `── amendment: foo ──` | No genera Task, setea contexto |
| Línea en blanco | Línea vacía | Se ignora |
| tasks.md vacío | Archivo existe sin contenido | Lista vacía `[]` |

---

## 4. Git Reader — Estado del working tree

Responsabilidad limitada en v1: solo detectar si el repo tiene cambios
pendientes (para inferir `verify`).

### Comportamiento

**Dado** un path de directorio
**Cuando** se consulta si el working tree está limpio
**Entonces** se ejecuta `git status --porcelain` y se retorna `True` si
la salida está vacía, `False` en caso contrario

### Casos alternativos — git reader

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| No es repo git | `git status` falla | Retorna `None` (sin estado) |
| git no instalado | Comando no encontrado | Retorna `None` |

---

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Inferencia sin estado propio | Base de datos SQLite | Máxima simplicidad, fuente de verdad = disco |
| `git status --porcelain` via subprocess | pygit2 / gitpython | Sin dependencias extra, git asumido instalado |
| Dataclasses para modelos | TypedDict / Pydantic | Suficiente para v1, sin overhead |
| `OpenspecNotFoundError` en lugar de `[]` | Retornar lista vacía | Distinguir "no hay changes" de "no hay openspec" |
| IDs de tarea siempre `TXX` | IDs libres | Formato fijo → parseado predecible, líneas sin ID ignoradas |

## Abierto / Pendiente

Ninguno.
