# Proposal: openspec-index-bootstrap

## Descripción

Extender `sdd-archive` Paso 2b para que **cree** `openspec/INDEX.md` desde cero
si no existe, en lugar de saltar silenciosamente. El índice se genera leyendo todas
las specs canónicas presentes en `openspec/specs/` en el momento del archive.

## Motivación

El change `openspec-index` implementó el índice y enseñó a `sdd-archive` a
**mantenerlo** cuando existe. Pero si INDEX.md no existe (proyecto nuevo, o proyecto
que adoptó SDD antes de este cambio), el Paso 2b salta silenciosamente y el índice
nunca se crea.

Flujo actual en proyecto nuevo:
1. `/sdd-init` → crea `openspec/` sin `INDEX.md`
2. Primer change → `sdd-archive` Paso 2b: no existe → salta
3. `INDEX.md` nunca existe → sdd-explore siempre usa fallback (sin ahorro de tokens)

El valor del índice es cero hasta que alguien lo crea manualmente.

## Impacto

### Archivos afectados
- `~/.claude/skills/sdd-archive/SKILL.md` — Paso 2b extendido con lógica de bootstrap
- `skills/sdd-archive/SKILL.md` — mismo cambio en el repo distribuible

### Sin cambios en
- Código Python, tests, specs canónicas (excepto `tooling` que se actualiza en archive)
- `openspec/INDEX.md` (ya existe en este proyecto)
- Resto de skills

## Criterios de éxito

1. Paso 2b de `sdd-archive` detecta si INDEX.md existe o no
2. Si **no existe** y hay specs en `openspec/specs/`: genera INDEX.md con una entrada por dominio
3. Si **existe**: comportamiento actual (actualizar entradas del change)
4. Si no hay specs: no crear un INDEX.md vacío (inútil)

## Notas

- El bootstrap lee las specs canónicas en el momento del archive → entradas siempre actualizadas
- No requiere nueva infraestructura — Claude genera el contenido leyendo las specs
- Cambio puramente en el skill (prompt Markdown), sin código ejecutable
