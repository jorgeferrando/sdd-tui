# Tasks: Pipeline Next Action

## Metadata
- **Change:** pipeline-next-action
- **Rama:** main (commits directos)
- **Fecha:** 2026-03-06

## Tareas de Implementación

- [x] **T01** Añadir RED tests para `next_command` y línea NEXT en `PipelinePanel` — `tests/test_tui_change_detail.py`
  - Commit: `[pipeline-next-action] Add RED tests for next_command and PipelinePanel NEXT line`

- [x] **T02** Implementar `next_command` + línea NEXT en `PipelinePanel` — `src/sdd_tui/tui/change_detail.py`
  - Commit: `[pipeline-next-action] Add next_command function and NEXT line to PipelinePanel`

## Quality Gate Final

- [x] **QG** Ejecutar todos los tests
  - `cd /Users/jorge/sites/sdd-tui && uv run pytest`

## Notas

- T01 escribe tests que fallan (RED): `next_command` no existe aún, panel no tiene NEXT
- T02 hace pasar todos los tests (GREEN): extraer función, añadir parámetro `name`, actualizar `_build_content`
- `name=""` como default en `PipelinePanel` para no romper tests existentes que no pasan name
- Eliminar `_build_next_command` al extraer `next_command`
