# Proposal: spec-health-hints

## Descripción

Añadir una columna `HINT` en `SpecHealthScreen` que muestre el comando SDD más
urgente para arreglar el problema detectado en cada change.

Actualmente la pantalla detecta problemas (fila en amarillo, `—` en REQ, `.` en
artefactos ausentes) pero no dice qué hacer. El usuario tiene que interpretar los
datos y recordar qué skill invocar. La columna HINT cierra ese gap mostrando
directamente el comando de acción.

## Motivación

En la sesión de análisis de GSD (2026-03-06), el patrón `--repair` de
`/gsd:health` fue identificado como de alto valor: no solo detecta problemas,
sino que sugiere la corrección exacta. Esta es la implementación equivalente para
sdd-tui con openspec como fuente de verdad.

## Comportamiento propuesto

La columna `HINT` muestra el hint más urgente inferido del estado del change:

| Condición | Hint |
|-----------|------|
| `spec` ausente en artifacts | `/sdd-spec {name}` |
| `design` ausente | `/sdd-design {name}` |
| `tasks` ausente | `/sdd-tasks {name}` |
| Tasks pendientes (done < total) | `/sdd-apply {name}` |
| Apply done, working tree sucio | `/sdd-verify {name}` |
| REQ = 0 (spec existe) | `add REQ-XX tags` |
| EARS% < 100% | `add EARS tags` |
| Inactivo > 7d | `resume: /sdd-apply {name}` |
| Todo OK | `✓` |

La lógica de prioridad es: pipeline first (flujo SDD), luego calidad de specs,
luego actividad.

## Implementación

- `core/metrics.py` — nueva función pura `repair_hints(metrics, change) -> list[str]`
  que retorna hints ordenados por prioridad. Testable de forma aislada.
- `tui/spec_health.py` — nueva columna `HINT` al final de la tabla usando el
  primer elemento de la lista (hint más urgente).

## Alternativas descartadas

- **Modal de detalle al hacer Enter**: ya existe navegación a `ChangeDetailScreen`.
  La columna en tabla es más escaneable sin interacción.
- **Múltiples hints en una celda**: demasiado ruido visual. Un hint = acción más urgente.
- **Hints en `ChangeDetailScreen`**: el usuario llega ahí después de SpecHealth. La
  pantalla de salud es el lugar de diagnóstico, no el detalle.

## Impacto

- Archivos afectados: `core/metrics.py`, `tui/spec_health.py`, tests correspondientes
- Scope: ~2-3 tareas atómicas
- Sin cambios en modelos de datos ni en otras pantallas

## Criterios de éxito

- [ ] `repair_hints()` retorna el hint correcto para cada condición
- [ ] La columna HINT aparece en `SpecHealthScreen` con el hint más urgente
- [ ] Tests unitarios para `repair_hints()` con cobertura de todos los casos
- [ ] Tests TUI que verifican la columna HINT en la tabla
