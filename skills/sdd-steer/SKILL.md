---
name: sdd-steer
description: SDD Steer - Genera y sincroniza archivos de steering en openspec/steering/. Bootstrap primera ejecución, sync detecta drift. Uso - /sdd-steer o /sdd-steer sync.
---

# SDD Steer

> Genera archivos de "memoria persistente" del proyecto en `openspec/steering/`.
> Captura convenciones invisibles que causan errores de PR — final, readonly, naming, capas.

## Usage

```
/sdd-steer          # Bootstrap: genera todos los archivos desde cero
/sdd-steer sync     # Sync: detecta drift y propone actualizaciones
```

## Prerequisitos

- Skills de arquitectura y code-quality del proyecto cargados (o cargarlos ahora)
- Estar en el directorio raíz del proyecto

## Modo Bootstrap (`/sdd-steer`)

### Paso 1: Detectar proyecto y cargar skills

Detectar el proyecto desde el working directory. Cargar en paralelo:
- `{project}-architecture`
- `{project}-code-quality`

Si ya están cargados, continuar directamente.

Si `openspec/steering/` ya existe con contenido:
```
⚠️  openspec/steering/ ya tiene contenido.
Usa `/sdd-steer sync` para actualizar en lugar de sobrescribir.
¿Continuar de todas formas? (s/n)
```
Esperar confirmación antes de continuar.

### Paso 2: Explorar codebase (read-only)

Explorar en paralelo:
- Estructura de directorios: `ls -la src/` (o equivalente del proyecto)
- Archivos de configuración: `pyproject.toml`, `composer.json`, `package.json`, etc.
- 2-3 archivos representativos de cada capa (handlers, controllers, entities, components)
- `MEMORY.md` del proyecto si existe en `.claude/projects/*/memory/`
- `openspec/specs/` para entender el dominio documentado

### Paso 3: Generar `openspec/steering/product.md`

```markdown
# Product: {Nombre del Proyecto}

## Qué construye
{1-2 párrafos: propósito, dominio, valor}

## Para quién
{usuarios/sistemas que lo consumen}

## Bounded context
{límites del sistema — qué no hace}
```

### Paso 4: Generar `openspec/steering/tech.md`

```markdown
# Tech Stack: {Proyecto}

## Lenguaje y runtime
- {lenguaje} {versión}
- {runtime / framework principal} {versión}

## Dependencias clave
- {dep}: {para qué}

## Herramientas
- Tests: {framework}
- Linting: {herramienta}
- Build: {herramienta}

## Entornos
- Dev: {cómo levantar}
- Test: {cómo ejecutar tests}
```

### Paso 5: Generar `openspec/steering/structure.md`

```markdown
# Structure: {Proyecto}

## Organización del código

{descripción de cada directorio principal y qué contiene}

## Capas y responsabilidades

| Capa | Directorio | Responsabilidad |
|------|-----------|----------------|
| {capa} | `{ruta}` | {qué hace, qué NO hace} |

## Flujo estándar de una request/operación

{diagrama ASCII o descripción del flujo típico}
```

### Paso 6: Generar `openspec/steering/conventions.md`

Este es el archivo más valioso. Derivar las convenciones de tres fuentes (en orden de prioridad):

1. **Skills de arquitectura/code-quality** — fuente más confiable
2. **MEMORY.md del proyecto** — patrones descubiertos en sesiones anteriores
3. **Código existente** — evidencia empírica (naming, estructura, decoradores)

Formato:

```markdown
# Conventions: {Proyecto}

> Reglas que causan errores de PR. Nivel RFC 2119: MUST / MUST NOT / SHOULD / MAY.

## {Área} — {Subárea}

- **MUST** {regla concreta} — {razón en una línea}
- **MUST NOT** {regla concreta} — {razón en una línea}
- **SHOULD** {regla concreta} — {razón en una línea}
```

Ejemplos de áreas comunes:

**Python / Textual:**
```markdown
## Python — Imports
- **MUST** use `from __future__ import annotations` in all modules — forward refs

## Textual — Navigation
- **MUST** use `push_screen` / `pop_screen` — no inline widget swap
- **MUST** use `call_after_refresh` for dynamic height — Textual render order
- **MUST NOT** use `pilot.type()` in tests — does not exist in Textual 8.x; use `widget.value = text`

## Workers
- **MUST** use `@work(thread=True, exclusive=True)` for blocking subprocess workers
- **MUST** use `self.app.call_from_thread` (not `self.call_from_thread`) — Screen doesn't expose it

## Commits
- **MUST** follow format `[change-name] Description in English`
- **MUST** be atomic: one logical change, one file per commit
```

**PHP / Symfony / CQRS:**
```markdown
## PHP — Classes
- **MUST** use `final` keyword — inheritance not used by convention
- **MUST** declare all Request properties as `readonly` — immutability contract

## CQRS — Handlers
- **MUST NOT** inject Repository directly — only via use case interfaces
- **MUST** receive a single Command/Query object as parameter

## Naming
- **MUST** name Commands as `{Verb}{Entity}Command` (e.g. CreateRateCommand)
- **MUST** name Handlers as `{Verb}{Entity}Handler` (e.g. CreateRateHandler)
```

### Paso 7: Crear directorio y escribir archivos

```bash
mkdir -p openspec/steering/
```

Escribir los cuatro archivos. Mostrar resumen al terminar:

```
STEER COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos generados:
  openspec/steering/product.md
  openspec/steering/tech.md
  openspec/steering/structure.md
  openspec/steering/conventions.md ← {N} convenciones documentadas

Próximo: /sdd-audit para verificar el codebase actual contra estas convenciones.
```

---

## Modo Sync (`/sdd-steer sync`)

### Paso 1: Leer estado actual

Leer en paralelo:
- `openspec/steering/conventions.md` (existente)
- Skills de arquitectura/code-quality del proyecto
- MEMORY.md del proyecto

### Paso 2: Detectar drift

Comparar:
- ¿Hay convenciones en los skills que no están en `conventions.md`?
- ¿Hay convenciones en `conventions.md` que ya no reflejan el código actual?
- ¿Han aparecido nuevos patrones en commits/MEMORY.md recientes?

### Paso 3: Proponer cambios

Presentar propuestas específicas al usuario. **NO modificar automáticamente.**

Formato:
```
DRIFT DETECTADO en conventions.md:

AÑADIR (nuevas convenciones encontradas):
+ ## Angular — Signals
+   - **MUST** use `signal()` for reactive state — no BehaviorSubject

ACTUALIZAR (convención desactualizada):
~ ## Tests — Patterns
~   OLD: **MUST NOT** use `async/await` directly
~   NEW: **MUST** use `async/await` with `asyncio` mode in pytest.ini

ELIMINAR (ya no aplica):
- ## Python — Compat
-   - **MUST** support Python 3.9 (no longer required — min is 3.13)

¿Aplicar estos cambios? (s/n/seleccionar)
```

---

## Notas

- `openspec/steering/` puede estar commiteado o en `.git/info/exclude` — decisión por proyecto.
- El steering no reemplaza los skills de arquitectura — los complementa con evidencia del código real.
- Actualizar `conventions.md` tras cada `/sdd-archive` si se descubrieron nuevas convenciones.
