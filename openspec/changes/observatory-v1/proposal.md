# Proposal: Observatory v1 — Multi-project Dashboard

## Metadata
- **Change:** observatory-v1
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

sdd-tui inspecciona un proyecto a la vez. Un tech lead o desarrollador que
trabaja con múltiples repositorios (ej: next + front + ms-delivery en
Parclick) necesita abrir una instancia separada por proyecto y cambiar
manualmente entre ellas.

Además, el estado del pipeline SDD está desconectado del estado de
revisión del código (PR en GitHub). Un change puede tener todas las tareas
completadas pero su PR puede estar en "changes requested" — información
que el TUI no muestra.

Por último, no hay forma de responder preguntas como "¿cuánto tardamos
en media en pasar de spec a PR?" o "¿qué porcentaje de changes se archivan
en < 5 días?". Esa información está en git y en los archivos pero no se
agrega.

## Solución Propuesta

### Multi-proyecto en la misma sesión

View 1 (EpicsView) muestra changes de **todos los proyectos configurados**,
agrupados por proyecto con separador visual:

```
─── sdd-tui ───────────────────────────────────────
  view-8-spec-health    · · · · ·  [propose]
  view-9-delta-specs    · · · · ·  [propose]
─── next ──────────────────────────────────────────
  di-464-parking        ✓ ✓ ✓ ✓ ·  [apply T03]
  di-471-rates          ✓ ✓ · · ·  [design]
```

Configuración en `~/.sdd-tui/config.yaml`:
```yaml
projects:
  - path: ~/sites/sdd-tui
  - path: ~/PhpstormProjects/next
  - path: ~/PhpstormProjects/front
```

### GitHub PR status en Pipeline sidebar

Si existe `gh` CLI y hay un PR abierto para la rama del change, el Pipeline
sidebar de View 2 añade una fila:

```
  PIPELINE

  ✓  propose
  ✓  spec
  ✓  design
  ✓  tasks
  ✓  apply
  ✓  verify
  ⧗  PR #1234   ← 2 approvals, 1 changes_requested
```

### Velocity metrics

View nueva `V` desde View 1: métricas agregadas por proyecto.

- **Throughput**: changes archivados por semana (últimas 8 semanas)
- **Lead time por fase**: tiempo medio en cada fase (propose → spec → ... → archive)
- **Bottleneck detector**: fase con mayor tiempo medio destacada
- **Change size**: distribución de tareas por change (P50, P90)

### Export a Markdown

`E` en la Velocity view exporta un reporte en Markdown al clipboard
o a un archivo, listo para pegar en una retro o en una wiki.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Dashboard web separado | Más flexible visualmente | Infraestructura extra, fuera del terminal | Descartada |
| Múltiples instancias TUI en paneles tmux | Sin cambios en sdd-tui | Fragmentado, sin agregación | Descartada |
| **Multi-proyecto en View 1 + config.yaml** | Un único punto de verdad en el terminal | Más complejo el routing de navegación | **Elegida** |

## Impacto Estimado

- **Dominio:** tui + core + config
- **Archivos:** > 20 — split recomendado si el scope crece
  - `core/config.py` — nuevo: lector de `~/.sdd-tui/config.yaml`
  - `core/github.py` — nuevo: consulta de PR via `gh` CLI
  - `core/velocity.py` — nuevo: métricas agregadas
  - `tui/epics.py` — modificado: multi-proyecto con separadores
  - `tui/velocity.py` — nuevo: VelocityView
  - `tui/change_detail.py` — modificado: PR row en PipelinePanel
  - Múltiples tests nuevos
- **Tests nuevos:** unit + integration para github.py y velocity.py
- **Breaking changes:** No para usuario single-project. Config.yaml es opcional.
- **Dependencias:** Se apoya en `core-universal-reader` para leer múltiples formatos.

## Criterios de Éxito

- [ ] Con config.yaml definido, View 1 muestra changes de todos los proyectos agrupados
- [ ] El PR status aparece en Pipeline sidebar cuando `gh` está disponible y hay PR abierto
- [ ] `V` abre VelocityView con métricas de lead time por fase
- [ ] El bottleneck (fase más lenta) está visualmente destacado
- [ ] `E` en VelocityView exporta el reporte al clipboard en Markdown

## Preguntas Abiertas

- [ ] ¿La config va en `~/.sdd-tui/config.yaml` (global) o en `openspec/config.yaml` (por proyecto)?
- [ ] ¿Las métricas de velocity requieren `spec.json` con timestamps o se infieren de git log?
- [ ] ¿Mostrar changes archivados de todos los proyectos en VelocityView o solo los activos?

## Notas

Este es el change más ambicioso del roadmap (v1.0). Tiene sentido abordarlo
último, después de que el Universal Reader y las vistas de calidad estén
estables.

El PR status via `gh` CLI es el puente entre el flujo SDD (qué hemos hecho)
y el flujo de revisión (si ya está aprobado). Cierra el loop completo del
ciclo de desarrollo.
