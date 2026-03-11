# Proposal: openspec-index

## Descripción

Añadir un índice estructurado de dos niveles (`openspec/INDEX.md`) que permita a los skills SDD identificar qué dominios son relevantes para un change sin necesidad de leer todas las specs canónicas.

## Motivación

Al iniciar un change (`/sdd:new`, `/sdd:continue`, `/sdd:spec`), los skills leen ad-hoc los archivos de `openspec/specs/` para orientarse. Con 8 dominios actuales (3308 líneas en total), esto ya supone un coste de contexto significativo. A medida que el proyecto crece, este coste crece linealmente.

**Estado actual:**
- `tui/spec.md` — 1253 líneas
- `core/spec.md` — 951 líneas
- 6 specs más — 1104 líneas
- Orientación completa = ~3300 líneas = ~5000-8000 tokens

**Con INDEX.md:**
- Orientación completa = ~300 tokens (el índice)
- Lectura de 1-2 specs relevantes = ~1500-2000 tokens adicionales
- **Ahorro estimado: 70-80% en fase de exploración**

## Alternativas consideradas

| Opción | Coste | Valor | Veredicto |
|--------|-------|-------|-----------|
| SQLite + FTS | Alto (indexer, binario en repo) | Medio | Overkill < 30 dominios |
| Grafo de dependencias | Alto (formato + herramienta) | Alto futuro | Prematuro ahora |
| Tags + INDEX.md (esta propuesta) | Muy bajo | Alto | Sweet spot |
| Status quo | Cero | Negativo (crece con el tiempo) | Insostenible |

## Impacto

### Archivos afectados
- `openspec/INDEX.md` — nuevo, generado y mantenido manualmente + auto-actualizado por `sdd-archive`
- `~/.claude/skills/sdd-archive/SKILL.md` — añadir Paso 2b: actualizar INDEX.md al cerrar un change
- `~/.claude/skills/sdd-explore/SKILL.md` — añadir Paso 0: leer INDEX.md antes de cargar specs individuales

### Sin cambios en
- Specs canónicas (estructura intacta)
- Código Python del proyecto
- Tests

## Criterios de éxito

1. `openspec/INDEX.md` existe y cubre los 8 dominios actuales
2. Cada entrada tiene: nombre, ruta, sumario 2 líneas, entidades clave, keywords
3. `sdd-archive` actualiza INDEX.md al cerrar cualquier change
4. `sdd-explore` lee INDEX.md primero y carga solo specs relevantes
5. Si INDEX.md no existe, los skills hacen fallback al comportamiento actual

## Formato propuesto de INDEX.md

```markdown
# OpenSpec Index

> Índice de dominios canónicos. Actualizado automáticamente por sdd-archive.
> Uso: leer este archivo primero para identificar qué specs cargar.

## core (`specs/core/spec.md`)
Lógica de negocio central: modelos de datos, lectura de openspec, git, métricas, providers, velocidad, milestones, todos.
**Entidades:** Change, Task, CommitInfo, load_changes(), load_git_workflow_config(), ChangeMetrics, Milestone, TodoItem
**Keywords:** models, reader, git, metrics, pipeline, providers, velocity, milestones, todos, config

## tui (`specs/tui/spec.md`)
Capa de presentación Textual: todas las pantallas, bindings, navegación, workers async.
**Entidades:** SddTuiApp, EpicsView, ChangeDetailScreen, SpecHealthScreen, SpecEvolutionScreen, PipelinePanel
**Keywords:** screens, bindings, navigation, widgets, workers, async, epics, detail, health, evolution, search, filter
```

## Notas

- El índice es source-of-truth para **orientación rápida**, no para detalle. El detalle sigue en las specs.
- Si un dominio no está en INDEX.md, los skills deben advertirlo tras un archive.
- Evolución futura: si aparecen dependencias complejas entre dominios, considerar añadir sección `depends_on` por entrada (paso hacia grafo ligero).
