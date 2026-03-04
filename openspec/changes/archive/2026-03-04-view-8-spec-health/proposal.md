# Proposal: View 8 — Spec Health Dashboard

## Metadata
- **Change:** view-8-spec-health
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui
- **Estado:** draft

## Problema / Motivación

sdd-tui navega y muestra el estado de los changes pero no evalúa su calidad.
Dos problemas concretos:

1. **Specs huérfanas de requisitos**: tras adoptar EARS en `sdd-spec`, no hay
   forma visual de saber cuántos requisitos tiene un change ni si están
   correctamente tipificados (`[Event]`, `[Unwanted]`, etc.).

2. **Cambios bloqueados sin señal**: un change puede llevar días en la misma
   fase sin que el TUI lo indique. El usuario lo descubre al revisar la lista
   manualmente.

El resultado es que la información de calidad existe en los archivos pero no
es visible sin abrirlos uno a uno.

## Solución Propuesta

Nueva pantalla `SpecHealthView` accesible con `H` desde View 1 (EpicsView).
Muestra, por cada change activo:

- **Requisitos**: número de REQ-XX detectados en specs + % tipificados con EARS
- **Cobertura de tareas**: tareas completadas / total
- **Tiempo en fase actual**: días desde el último commit relacionado
- **Artefactos presentes**: indicador por cada artifact
  (`proposal` / `spec` / `research` / `design` / `tasks`)
- **Alertas**: cambios sin actividad > N días o sin ningún REQ-XX definido

Adicionalmente, View 2 muestra un badge `REQ: 5` en el Pipeline sidebar
si la spec tiene requisitos EARS, o `REQ: —` si no los tiene.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Score numérico (ej. CQRS 73/100) | Visual llamativo | Falsa precisión, no accionable | Descartada |
| Métricas inline en View 1 (EpicsView) | Sin pantalla nueva | Columnas saturan la lista | Descartada |
| **View separada `H`** | Espacio completo, detalles por change | Una tecla extra | **Elegida** |

## Impacto Estimado

- **Dominio:** tui + core
- **Archivos:** < 10
  - `core/metrics.py` — nuevo: parser de REQ-XX en specs, contador de artefactos
  - `tui/spec_health.py` — nuevo: SpecHealthView (DataTable por change)
  - `tui/change_detail.py` — modificado: badge REQ en PipelinePanel
  - `tui/epics.py` — modificado: binding `H` → push SpecHealthView
- **Tests nuevos:** unit tests para `core/metrics.py`
- **Breaking changes:** No
- **Dependencias:** Requiere specs con formato EARS (view-8 asume EARS ya adoptado)

## Criterios de Éxito

- [ ] `H` desde View 1 abre SpecHealthView con datos de todos los changes activos
- [ ] El parser detecta REQ-XX en cualquier spec bajo `openspec/changes/`
- [ ] Changes sin ningún REQ-XX muestran alerta visual diferenciada
- [ ] El badge `REQ: N` aparece en Pipeline sidebar de View 2
- [ ] Changes con > 7 días en la misma fase muestran indicador de inactividad

## Preguntas Abiertas

- [ ] ¿El umbral de inactividad es configurable o fijo (7 días)?
- [ ] ¿`research.md` se incluye como artefacto esperado o es opcional?

## Notas

Esta view es la primera pieza del roadmap v0.7 del reporte ejecutivo de
2026-03-04. Sienta las bases para el parsing de specs que reutilizarán
`view-9-delta-specs` y `observatory-v1`.

El parser `core/metrics.py` no debe ser un parser completo de Markdown —
solo necesita detectar líneas que coincidan con `\*\*REQ-\d+\*\*\s+\[`.
