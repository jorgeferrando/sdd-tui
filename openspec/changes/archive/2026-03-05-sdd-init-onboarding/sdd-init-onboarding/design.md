# Design: SDD Init Onboarding

## Metadata
- **Change:** sdd-init-onboarding
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-05
- **Estado:** approved

## Resumen Técnico

Cambio puramente de skills y scripts — sin tocar código Python del TUI. Se reescribe
`skills/sdd-init/SKILL.md` para incorporar un flujo de onboarding guiado de 5 fases:
escaneo de entorno, cuestionario interactivo, generación de steering, verificación de
skills instalados. Se modifica `skills/sdd-apply/SKILL.md` para añadir bootstrap
verification al inicio. Se añaden al repo los skills `sdd-audit` y `sdd-steer` que
existían solo en `~/.claude/skills/` (distribución incompleta). Se añade un script
bash `sdd-env-scan.sh` que realiza el escaneo de entorno de forma portable.

## Arquitectura del flujo

```
Usuario ejecuta /sdd-init
        │
        ▼
  [ENV SCAN]  scripts/sdd-env-scan.sh
  runtimes · CLI tools · Docker · detectar stack desde config files
        │
        ├─ openspec/steering/ ya existe? → mostrar estado + ofrecer sync
        │
        ▼
  [QUESTIONNAIRE]  skill prompt interactivo
  proyecto · stack · equipo · MCPs · patrones
  (reducido si hay código detectado)
        │
        ▼
  [ARTIFACT GENERATION]  skill genera en paralelo
  product.md · tech.md · structure.md · conventions.md
  environment.md · project-skill.md · project-rules.md
        │
        ├─ Context7 disponible? → resolver IDs de librerías → tech.md
        │
        ▼
  [SKILLS CHECK]
  ~/.claude/skills/sdd-apply/ existe? → OK
                                      → guiar a sdd-setup / install-skills.sh
        │
        ▼
  SDD INIT COMPLETE — next: /sdd-new

─────────────────────────────────────────

Usuario ejecuta /sdd-apply
        │
        ▼
  [BOOTSTRAP VERIFICATION]  (nuevo Step 0)
  openspec/steering/conventions.md existe?
        │
        ├─ No → STOP: "Run /sdd-init first"
        │
        ▼
  [STEERING LOAD]  silencioso
  Lee project-skill.md (si existe) o conventions.md + project-rules.md + tech.md
        │
        ▼
  [IMPLEMENTACIÓN]  flujo existente sin cambios
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `skills/sdd-init/SKILL.md` | skill (rewrite) | Onboarding completo: ENV scan + cuestionario + steering generation + skills check |
| `skills/sdd-audit/SKILL.md` | skill (nuevo en repo) | Audit contra `conventions.md` + `project-rules.md`; faltaba en distribución |
| `skills/sdd-steer/SKILL.md` | skill (nuevo en repo) | Steer sync para proyectos existentes; faltaba en distribución |
| `scripts/sdd-env-scan.sh` | script bash | Detecta runtimes, CLI tools, Docker; output para el skill |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `skills/sdd-apply/SKILL.md` | Añadir Step 0: bootstrap verification + steering load | REQ-BOOT01-04 |

## Scope

- **Total archivos:** 5
- **Resultado:** Ideal

## Dependencias Técnicas

- Sin dependencias externas — solo bash y herramientas estándar
- `sdd-env-scan.sh` usa `command -v` para detectar tools (portable, sin deps)
- La integración con Context7 usa `mcp__context7__resolve-library-id` — si no está disponible, el onboarding continúa sin error

## Patrones Aplicados

- **Skill como prompt template**: los skills son archivos Markdown con instrucciones para Claude; no son código ejecutable. La lógica de decisión vive en el texto del skill, no en scripts.
- **Script para lógica portable**: el escaneo de entorno sí es bash puro — necesita ejecutarse en el sistema, no en Claude.
- **Separación skill/script**: el skill orquesta y decide; el script recolecta datos del sistema.
- **Referencia al patrón existente**: `sdd-steer` ya genera `openspec/steering/`; `sdd-init` onboarding lo hace guiado para proyectos nuevos. No duplican — son momentos distintos del ciclo de vida.

## Diseño detallado por archivo

### `skills/sdd-init/SKILL.md` (rewrite)

Estructura de pasos:

```
Step 1 — Skills check
  Verificar que ~/.claude/skills/sdd-apply/ existe
  Si no: mostrar instrucciones para instalar con install-skills.sh
  No bloquear el onboarding — el usuario puede continuar sin skills

Step 2 — Detect project state
  Ejecutar scripts/sdd-env-scan.sh
  Detectar: openspec/ existe?, steering/ existe?, código detectado?
  Si steering/ existe con contenido → ir a "show state" (no onboarding)

Step 3 — Questionnaire (si no hay steering)
  Modo completo (sin código) o reducido (con código detectado)
  Para cada pregunta con opciones: mostrar trade-offs en lenguaje llano
  Si Claude tiene alta confianza → recomendar con justificación de 1 línea
  Dimensiones: proyecto · stack · equipo · rigor · MCPs · patrones

Step 4 — Generate openspec/steering/
  Generar 7 archivos en paralelo:
    product.md, tech.md, structure.md, conventions.md,
    environment.md, project-skill.md, project-rules.md
  Si mcp__context7 disponible → resolver IDs y añadir refs a tech.md
  project-skill.md: ≤ 100 líneas, actúa como índice

Step 5 — Show state
  Mostrar resumen del steering generado o existente
  Next steps: /sdd-new para empezar primera feature
```

### `skills/sdd-apply/SKILL.md` (modificar)

Insertar **Step 0** antes del Step 1 actual:

```
Step 0 — Bootstrap verification + steering load
  ¿Existe openspec/steering/conventions.md?
    No → STOP: "Run /sdd-init first to set up your project context"
    Sí → continuar

  Cargar steering silenciosamente:
    Si project-skill.md existe → leerlo (es el índice)
    Si no → leer conventions.md + project-rules.md + tech.md directamente
  No mostrar output al usuario — solo cargar el contexto
```

### `skills/sdd-audit/SKILL.md` (nuevo en repo)

Basado en `~/.claude/skills/sdd-audit/SKILL.md` existente + extensión:

```
Paso 1: Leer convenciones
  Leer conventions.md (siempre requerido)
  Si project-rules.md existe → leer también (ruleset unificado)

Paso 2: Analizar código
  Archivos modificados desde base branch (default)
  O scope específico si se proporcionó argumento

Paso 3: Clasificar violaciones
  Critical (MUST/MUST NOT) · Important (SHOULD) · Minor (MAY)
  Aplica igual a convenciones de ambos archivos
  No reportar violaciones cubiertas por el linter (audit es semántico)

Paso 4: Output
  Reporte clasificado con: archivo, línea aprox, convención violada, fix sugerido
  Si no hay violaciones → confirmación clean
  Si violaciones críticas → generar prompts /sdd-new para corrección
```

### `scripts/sdd-env-scan.sh`

```bash
#!/usr/bin/env bash
# sdd-env-scan — detecta el entorno disponible para /sdd-init onboarding
# Output: texto estructurado que el skill parsea

# Runtimes
check_runtime() { command -v "$1" &>/dev/null && echo "runtime:$1:$(\"$1\" --version 2>&1 | head -1)" || echo "runtime:$1:missing"; }

# CLI tools
check_tool() { command -v "$1" &>/dev/null && echo "tool:$1:available" || echo "tool:$1:missing"; }

# Project files (stack detection)
check_file() { [ -f "$1" ] && echo "file:$1:found" || echo "file:$1:missing"; }

check_runtime node
check_runtime python3
check_runtime php
check_runtime ruby
check_runtime go
check_runtime rustc

check_tool git
check_tool gh
check_tool docker
check_tool uv
check_tool bun
check_tool composer

check_file package.json
check_file pyproject.toml
check_file composer.json
check_file go.mod
check_file Cargo.toml
check_file Gemfile
check_file requirements.txt

# Docker containers (si docker disponible)
if command -v docker &>/dev/null; then
  docker ps --format "container:{{.Names}}:{{.Status}}" 2>/dev/null || echo "container:docker:unavailable"
fi

# openspec state
[ -d "openspec/steering" ] && echo "steering:exists" || echo "steering:missing"
[ -f "openspec/steering/conventions.md" ] && echo "conventions:exists" || echo "conventions:missing"
```

### `skills/sdd-steer/SKILL.md` (nuevo en repo)

Copia del skill instalado en `~/.claude/skills/sdd-steer/SKILL.md` — sin cambios
de comportamiento. Solo se añade al repo para que `install-skills.sh` lo distribuya.

## Plantillas de steering generadas por sdd-init

El skill genera los 7 archivos con esta estructura mínima garantizada:

```
project-skill.md  → frontmatter + secciones que referencian los demás archivos
project-rules.md  → ## Style · ## Tests · ## Architecture (vacío inicialmente)
conventions.md    → ## Bootstrap decisions + decisiones tomadas en onboarding
environment.md    → ## Available tools + ## Available MCPs
product.md        → ## What · ## For whom · ## Bounded context
tech.md           → ## Stack · ## Dependencies · ## Tools · ## Context7 refs (si aplica)
structure.md      → ## Directories · ## Layers · ## Standard flow
```

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| sdd-env-scan.sh bash puro | Script Python | Sin deps adicionales; `command -v` es portable en macOS/Linux |
| Output texto línea por línea | JSON | Más fácil de parsear en el skill sin herramientas adicionales |
| Step 0 en sdd-apply (no Step 1) | Modificar Step 1 | El bootstrap check debe ser lo primero, antes de leer tasks.md |
| sdd-steer incluido en este change | Change separado | Faltaba en la distribución — un archivo, sin cambios de comportamiento |
| project-skill.md como índice ≤ 100 líneas | Un único archivo grande | Mantiene el tiempo de carga inicial pequeño; detalles en archivos referenciados |

## Tests Planificados

Este change no incluye tests Python. Los skills son prompt-only y no son ejecutables.
El script `sdd-env-scan.sh` puede verificarse manualmente ejecutándolo en diferentes entornos.

Verificación manual del cambio:
1. Ejecutar `/sdd-init` en un proyecto nuevo (sin código) → debe presentar cuestionario completo
2. Ejecutar `/sdd-init` en un proyecto con `package.json` → debe detectar Node y reducir cuestionario
3. Ejecutar `/sdd-apply` sin `openspec/steering/conventions.md` → debe parar con mensaje claro
4. Ejecutar `/sdd-audit` con `project-rules.md` presente → debe usar ambos archivos

## Notas de Implementación

- El skill generado `project-skill.md` debe cargar explícitamente los demás archivos de steering
  con instrucciones como "Read openspec/steering/conventions.md and project-rules.md before implementing"
- La detección de MCPs en el cuestionario es informativa: Claude ya sabe qué MCPs tiene disponibles
  desde las herramientas activas — el escaneo los confirma para registrarlos en `environment.md`
- `sdd-steer` sigue siendo relevante para proyectos que ya tienen código pero no tienen steering —
  el onboarding de `sdd-init` es para proyectos nuevos; no son redundantes
