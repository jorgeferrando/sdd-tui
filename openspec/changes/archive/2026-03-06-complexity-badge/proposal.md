# Proposal: complexity-badge

## Descripción

Añadir una columna `SIZE` en `EpicsView` que muestre una métrica de complejidad por change,
calculada a partir de datos ya disponibles (tareas, archivos git modificados, líneas de spec).
El badge sirve como señal visual para identificar changes sobredimensionados que deberían dividirse.

## Motivación

Actualmente `EpicsView` muestra el estado de cada fase (propose/spec/design/tasks/apply/verify)
pero no da información sobre el tamaño del change. Un change con 15 tareas y 20 archivos
modificados tiene un riesgo de aplicación muy diferente a uno con 3 tareas y 2 archivos.

Sin esta métrica, el usuario solo descubre que un change es demasiado grande cuando ya está
a mitad de la implementación — demasiado tarde para dividirlo limpiamente.

## Diseño propuesto

### Cálculo de la métrica

La complejidad se calcula con tres inputs, todos disponibles sin overhead significativo:

| Input | Fuente | Ya disponible |
|-------|--------|---------------|
| Número de tareas | `change.tasks` | ✓ |
| Líneas de spec | `specs/*/spec.md` en el change | lectura de archivo |
| Archivos git modificados | `git diff --name-only` del change | nuevo subprocess |

**Score numérico** (suma ponderada):
```
score = task_count * 3 + spec_lines // 50 + git_files
```

**Badge de texto** basado en rangos:
```
score  0-5   → "XS"
score  6-12  → "S"
score 13-24  → "M"
score 25-40  → "L"
score 41+    → "XL"   (coloreado en amarillo = warning)
```

### Ubicación en EpicsView

Nueva columna `SIZE` entre `change` y `propose`:

```
change              SIZE  propose  spec  design  tasks  apply  verify
skill-palette       M     ✓        ✓     ✓       ✓      8/8    ✓
complexity-badge    XS    ✓        ·     ·       ·      ·      ·
```

### Función en core/metrics.py

```python
@dataclass
class ChangeMetrics:
    req_count: int
    ears_count: int
    artifacts: list[str]
    inactive_days: int | None
    complexity_score: int       # nuevo
    complexity_label: str       # nuevo: XS/S/M/L/XL
```

## Alternativas consideradas

**Alternativa A — Solo contar tareas.**
Más simple, pero incompleto: un change puede tener pocas tareas pero specs largas y muchos archivos.

**Alternativa B — Score en SpecHealthScreen en lugar de EpicsView.**
SpecHealth ya tiene las métricas, pero EpicsView es la pantalla principal donde el usuario necesita
esta visibilidad. La columna en SpecHealth puede añadirse también, pero el valor primario está en
EpicsView donde el usuario decide si dividir antes de empezar.

**Alternativa C — Umbral configurable.**
Configurar los umbrales en `config.yaml`. Añade complejidad sin valor claro — los umbrales
propuestos son suficientemente universales y siempre se pueden ajustar después.

## Impacto

- **core/metrics.py** — añadir `complexity_score` + `complexity_label` a `ChangeMetrics` y cálculo
- **tui/epics.py** — añadir columna `SIZE` en `_populate` y `_add_change_row`
- **tests/** — tests de cálculo de score y tests TUI de la nueva columna

Sin cambios en modelos, reader, pipeline, ni otras pantallas. Alcance mínimo.

## Criterios de éxito

- `EpicsView` muestra columna `SIZE` con badge XS/S/M/L/XL por cada change activo
- Changes con score ≥ 41 muestran badge en amarillo como warning visual
- `parse_metrics()` retorna `complexity_score` y `complexity_label`
- Tests unitarios cubren el cálculo del score para cada rango
