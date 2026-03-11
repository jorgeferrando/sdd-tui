# Design: OpenSpec Index Bootstrap

## Metadata
- **Change:** openspec-index-bootstrap
- **Jira:** —
- **Proyecto:** sdd-tui (skill SDD)
- **Fecha:** 2026-03-11
- **Estado:** approved

## Resumen Técnico

Modificación quirúrgica del Paso 2b de `sdd-archive`: añadir un bloque condicional
al inicio que detecta si INDEX.md existe. Si no existe y hay specs, lo genera desde
cero antes de proceder con el flujo normal de actualización.

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `skills/sdd-archive/SKILL.md` | Paso 2b: añadir bloque "Si INDEX.md no existe → bootstrap" |
| `~/.claude/skills/sdd-archive/SKILL.md` | Mismo cambio (skill activo en sesión) |

## Scope

- **Total archivos:** 1 (2 ubicaciones)
- **Resultado:** Ideal

## Detalle del cambio en Paso 2b

**Estructura actual:**
```
Si existe INDEX.md:
  1. Actualizar entradas del change
  2. Añadir entrada si dominio nuevo
  3. Verificar cobertura
Si no existe → saltar
```

**Estructura nueva:**
```
Si NO existe INDEX.md Y openspec/specs/ tiene dominios:
  → Bootstrap: leer cada specs/{domain}/spec.md
  → Generar INDEX.md completo con todas las entradas
  → (continuar con actualización normal del change actual)

Si existe INDEX.md:
  1. Actualizar entradas del change
  2. Añadir entrada si dominio nuevo
  3. Verificar cobertura

Si no existe INDEX.md Y specs/ está vacío → saltar
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Bloque bootstrap al inicio del Paso 2b | Paso 2c separado | Mantiene la lógica de INDEX.md en un solo lugar |
| Tras bootstrap, continuar con update normal | Solo bootstrap, sin update | El change actual también puede tener nuevas entidades — update garantiza consistencia |
