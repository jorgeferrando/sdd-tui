# Proposal: sdd-init-reverse-spec

## Metadata
- **Change:** sdd-init-reverse-spec
- **Fecha:** 2026-03-11
- **Estado:** draft

---

## Descripción

Añadir una fase de **reverse-spec** a `sdd-init` que, al ejecutarse en un proyecto con código existente, analiza el codebase y genera specs canónicas iniciales en `openspec/specs/{dominio}/spec.md`.

Hoy `sdd-init` es puramente estructural: crea directorios, excluye de git, genera `config.yaml`. Cuando termina, `openspec/specs/` queda vacío — el dev tiene que escribir los specs desde cero sin ningún punto de partida.

## Motivación

Al llegar a un proyecto empresarial con código heredado, el gap entre "ejecuté sdd-init" y "tengo specs útiles" es enorme. Un dev nuevo necesita semanas para entender los dominios, modelos y relaciones. La reverse-spec comprime ese tiempo generando una base documentada a partir del código existente, aunque sea incompleta o aproximada.

El spec resultante no es perfecto (no puede serlo sin contexto humano), pero:
- Da un punto de partida concreto mejor que una página en blanco
- Fuerza a identificar los dominios arquitectónicos desde el inicio
- Los specs marcados `Status: inferred` son explícitamente "borradores del análisis" — invitan a validarlos con `/sdd-spec`, no a confiar en ellos ciegamente

## Estado actual

- `sdd-init` (SKILL.md): 6 pasos, puramente estructural. No hay análisis de código.
- `openspec/specs/` después de init: vacío.
- REQ-ENV02 en `tooling/spec.md`: ya define detección automática de stack. Reverse-spec es la extensión natural: de "detectar stack" a "inferir dominios y generar specs".
- `sdd-explore`: usa Glob/Grep/Read para navegar el codebase — mismos primitivos que necesita reverse-spec.

## Alternativas consideradas

| Alternativa | Descartada porque |
|------------|-------------------|
| Script Python separado (`sdd-discover`) | Añade dependencia de ejecución. Los skills son prompt-only. El análisis con Glob/Grep en el skill tiene la misma capacidad. |
| Guía manual ("lee estos archivos y escribe los specs") | Ya existe: es lo que hace el dev hoy. No aporta valor. |
| Integrar en `/sdd-explore` en lugar de `/sdd-init` | `sdd-explore` es read-only y orientado a un change concreto. Reverse-spec es bootstrap del proyecto completo — pertenece a init. |
| Solo generar `INDEX.md` sin specs | Insuficiente. Un índice sin contenido no ayuda a entender el comportamiento del sistema. |

## Diseño — dos comandos separados

| Comando | Responsabilidad |
|---------|----------------|
| `/sdd-init` | Estructural. Si `openspec/specs/` queda vacío al final → hint "sin canon inicial — lanza `/sdd-discover`" |
| `/sdd-discover` | Analiza codebase, presenta listado de dominios detectados, genera specs `Status: inferred` tras confirmación del usuario |

Esta separación mantiene `sdd-init` rápido y predecible. El hint hace `sdd-discover` discoverable justo cuando se necesita, sin forzar el análisis en el bootstrap.

## Impacto

**Archivos modificados/creados:**
- `~/.claude/skills/sdd-init/SKILL.md` — añadir hint en Paso 6 si `openspec/specs/` vacío
- `~/.claude/skills/sdd-discover/SKILL.md` — skill nuevo
- `openspec/specs/tooling/spec.md` — añadir REQ-RS-XX para sdd-discover
- `openspec/INDEX.md` — actualizar dominio `tooling`

**Sin cambios de código Python** (skills son prompt-only).

## Flujo de sdd-discover

```
/sdd-discover
│
├── Detectar dominios desde estructura del proyecto
│   (src/, app/, lib/, tests/, etc. + archivos por extensión)
│
├── Mostrar listado:
│   "Dominios detectados:
│    - core      (src/core/ — 12 archivos .py)
│    - tui       (src/tui/  — 8 archivos .py)
│    - tests     (tests/    — 24 archivos .py)
│    ¿Proceder con el análisis? [s/N]"
│
├── Para cada dominio confirmado:
│   ├── Leer archivos representativos (Glob + Read)
│   ├── Inferir: propósito, entidades, comportamiento clave
│   └── Generar openspec/specs/{dominio}/spec.md
│       ├── Status: inferred
│       ├── Contexto derivado del análisis
│       └── REQs EARS aproximados
│
└── Actualizar/crear openspec/INDEX.md
```

## Criterios de éxito

- [ ] `sdd-init` muestra hint "sin canon — lanza `/sdd-discover`" cuando `openspec/specs/` está vacío
- [ ] `sdd-discover` detecta dominios desde estructura de directorios y extensiones de archivos
- [ ] Muestra listado de dominios con conteo de archivos antes de proceder
- [ ] Genera un `openspec/specs/{dominio}/spec.md` válido (formato canónico) por cada dominio
- [ ] Los specs generados tienen `Status: inferred`
- [ ] `openspec/INDEX.md` queda actualizado con los dominios detectados
- [ ] La spec canónica `tooling` v5.2 documenta los nuevos REQ-RS-XX

## Abierto / Pendiente

- ¿`sdd-discover` forma parte del directorio de un change activo o es siempre a nivel de proyecto?
