---
name: sdd-discover
description: SDD Discover - Analiza el codebase existente y genera specs canónicas iniciales en openspec/specs/ con Status inferred. Se ejecuta una vez por proyecto después de sdd-init. Uso - /sdd-discover.
---

# SDD Discover

> Reverse-spec: analiza el codebase existente e infiere specs canónicas iniciales.
> Cada dominio detectado se analiza en un subagente con contexto aislado.

## Usage

```
/sdd-discover              # Analizar proyecto completo
/sdd-discover {dominio}    # Analizar un dominio específico
```

Normalmente invocado tras `/sdd-init` cuando `openspec/specs/` está vacío.

## Prerequisitos

- `sdd-init` ejecutado (`openspec/` existe con `config.yaml`)
- Skills del proyecto cargados

## Paso 1: Detectar Dominios

Explorar la estructura del proyecto para inferir dominios arquitectónicos:

```bash
# Raíces de código fuente habituales
ls src/ app/ lib/ packages/ 2>/dev/null

# Contar archivos fuente por directorio candidato
find src app lib packages -maxdepth 1 -type d 2>/dev/null
find . -maxdepth 2 -name "*.py" -o -name "*.ts" -o -name "*.php" \
       -o -name "*.rb" -o -name "*.go" -o -name "*.rs" 2>/dev/null | head -50
```

**Reglas de inferencia:**

| Directorio encontrado | Dominio inferido |
|----------------------|-----------------|
| `src/{name}/` o `app/{name}/` | `{name}` |
| `tests/`, `spec/`, `__tests__/`, `test/` | `tests` |
| Archivos `.py/.ts/.php` en la raíz del proyecto | `{nombre del proyecto}` o `root` |

**Ignorar siempre:** `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`,
`__pycache__/`, `.venv/`, `coverage/`, `openspec/`, `.claude/`.

Si se proporciona `{dominio}` como argumento, omitir la detección automática y
analizar solo ese dominio.

## Paso 2: Resumen Interactivo

Antes de proceder, mostrar la lista de dominios detectados y pedir confirmación:

```
Dominios detectados:
  - core      (src/core/  — 12 archivos .py)
  - tui       (src/tui/   — 9 archivos .py)
  - tests     (tests/     — 28 archivos .py)

¿Proceder con el análisis? [S/n]
```

Si el usuario responde N o cancela → parar sin crear ningún archivo.

**Dominios a omitir:** si ya existe `openspec/specs/{dominio}/spec.md`, indicarlo:
```
  - core      → ya existe spec, se omitirá
```

Si todos los dominios ya tienen spec → informar y terminar sin crear nada.

## Paso 3: Análisis por Dominio (Subagentes en Paralelo)

Tras confirmación del usuario, lanzar **un subagente por dominio en paralelo**
usando el Agent tool (subagent_type: `general-purpose`).

**Prompt base para cada subagente:**

```
Eres un analizador de código. Tu tarea es generar una spec canónica del dominio
"{dominio}" del proyecto en {ruta_dominio}.

INSTRUCCIONES:
1. Usa Glob y Read para explorar los archivos del dominio.
   Lee los que necesites para entender el propósito y las entidades principales
   (prioriza: entry points, modelos, interfaces públicas).
2. Infiere: propósito del dominio, entidades clave, comportamiento principal.
3. Genera el archivo openspec/specs/{dominio}/spec.md siguiendo EXACTAMENTE
   este formato canónico:

---
# Spec: {Dominio} — {Título descriptivo}

## Metadata
- **Dominio:** {dominio}
- **Change:** sdd-discover
- **Fecha:** {fecha actual}
- **Versión:** 1.0
- **Estado:** inferred

## Contexto
{2-4 líneas: qué problema resuelve este dominio en el sistema}

## Comportamiento Actual
{Descripción de lo que implementa hoy el código, basada en lo leído}

## Requisitos (EARS)
{5-10 REQs inferidos del comportamiento observado}
- **REQ-01** `[Ubiquitous]` The {actor} SHALL {invariante}
- **REQ-02** `[Event]` When {trigger}, the {actor} SHALL {response}
...

<!-- inferred — validate with /sdd-spec -->

## Decisiones Tomadas
| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
{decisiones observadas en el código, si las hay}

## Abierto / Pendiente
- [ ] {Aspectos del dominio que no quedaron claros en el análisis}

> Spec generada automáticamente por /sdd-discover. Validar y completar con /sdd-spec.
---

4. Escribe el archivo con el tool Write.
5. Devuelve solo: "✓ {dominio} — spec escrita en openspec/specs/{dominio}/spec.md"
```

El orquestador recibe únicamente el mensaje de confirmación de cada subagente
(no el contenido de la spec), manteniendo el contexto del orquestador ligero.

## Paso 4: Actualizar openspec/INDEX.md

Tras recibir confirmación de todos los subagentes:

**Si `openspec/INDEX.md` existe:**
- Añadir una entrada por cada dominio nuevo generado
- NO modificar entradas ya existentes

**Si `openspec/INDEX.md` no existe:**
- Crearlo con header estándar + una entrada por cada dominio generado

Formato de entrada (estándar INDEX.md):
```markdown
## {dominio} (`specs/{dominio}/spec.md`)
{Descripción 1-2 líneas del dominio}
**Entidades:** {entidades principales}
**Keywords:** {keywords relevantes}
```

## Paso 5: Resumen Final

```
sdd-discover completado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Specs generados:
  ✓ core    → openspec/specs/core/spec.md
  ✓ tui     → openspec/specs/tui/spec.md
  ✓ tests   → openspec/specs/tests/spec.md
Omitidos: —

Próximos pasos:
  Validar specs con /sdd-spec {dominio}
```

## Reglas

- **Idempotente:** dominios con spec existente se omiten siempre, sin error.
- **Read-only sobre el código fuente:** solo escribe en `openspec/`.
- **No crea change activo:** opera directamente sobre `openspec/specs/`.
- **`Status: inferred`** es la señal explícita de que la spec es un borrador
  automático — no una spec validada por humanos.
- Si `openspec/steering/structure.md` existe, el subagente MAY leerlo para
  mejorar la inferencia, pero no es obligatorio.
