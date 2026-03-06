# Proposal: pipeline-next-action

## Descripción

Añadir una línea `NEXT` al `PipelinePanel` de View 2 que muestra visualmente
cuál es la siguiente acción del flujo SDD para el change activo.

Actualmente, el usuario debe pulsar `space` para copiar el comando siguiente
al clipboard — pero no tiene feedback visual de qué viene sin pulsar la tecla.

## Motivación

El `PipelinePanel` ya muestra el estado de cada fase (✓/·). Saber *qué toca ahora*
es la pregunta más frecuente al abrir un change. Tenerlo visible elimina fricción.

La lógica existe en `ChangeDetailScreen._build_next_command()` — el cambio
es puramente de presentación: exponer ese valor en el panel.

## Alcance

**Incluye:**
- Nueva línea `NEXT: {comando}` al final del `PipelinePanel`
- Extraer `next_command(pipeline, tasks, change_name) -> str` a función pura en `tui/change_detail.py` (o `core/pipeline.py`) para poder testarla aislada
- Tests unitarios de la función pura
- Tests de integración: `PipelinePanel._text` contiene `NEXT:`

**Excluye:**
- Cambiar el comportamiento de `space` (sigue copiando al clipboard)
- Colorear o resaltar la línea NEXT (puede venir en UX posterior)

## Alternativas consideradas

| Alternativa | Descartada porque |
|-------------|-------------------|
| Tooltip o popup al hover | Textual no tiene hover TUI-nativo; más complejo |
| Mover lógica a `core/pipeline.py` | Lógica de comando es TUI-concern; over-engineering para este cambio |
| Línea al inicio del panel | El pipeline flow top→down es el diseño actual; NEXT al final es natural |

## Impacto estimado

- 2 archivos modificados: `change_detail.py`, `tests/`
- ~10 tests nuevos
- Complejidad: XS

## Criterios de éxito

- `PipelinePanel._text` contiene `NEXT: /sdd-spec foo` cuando spec está pendiente
- `PipelinePanel._text` contiene `NEXT: /sdd-archive foo` cuando todo está DONE
- La lógica de next command está cubierta por tests unitarios aislados
- `space` binding sigue funcionando (sin regresión)
