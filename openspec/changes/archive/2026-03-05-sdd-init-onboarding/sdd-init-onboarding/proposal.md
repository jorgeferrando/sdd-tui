# Proposal: sdd-init-onboarding

## Metadata
- **Change:** sdd-init-onboarding
- **Fecha:** 2026-03-05
- **Estado:** approved

## Descripción

Ampliar `/sdd-init` con un flujo de onboarding guiado que, mediante preguntas interactivas,
recoge suficiente contexto para generar los artefactos que definen la idiosincrasia de un
proyecto nuevo: stack, patrones, convenciones, y entorno disponible.

Los artefactos generados alimentan directamente `sdd-apply` y el resto del flujo SDD,
permitiendo que Claude genere código correcto desde el primer commit sin que el usuario
tenga que re-explicar el stack en cada sesión.

La skill del proyecto es un artefacto vivo: se actualiza cada vez que el usuario corrige
una decisión de Claude, acumulando las convenciones reales del proyecto a lo largo del tiempo.

## Motivación

Actualmente `/sdd-init` hace bootstrap de la estructura `openspec/` pero no captura el
contexto del proyecto. El usuario arranca en un vacío: no hay steering, no hay convenciones,
no hay skills específicos del proyecto. Esto obliga a que cada sesión comience "desde cero"
o a que el usuario cargue manualmente los skills correctos.

Para proyectos nuevos el problema es mayor: hay que tomar decisiones de stack, patrones y
organización antes de escribir la primera línea de código. Sin una ceremonia guiada, esas
decisiones quedan implícitas y dispersas.

## Approach

### Fase 1 — Environment Discovery (automática, sin preguntas)

`/sdd-init` ejecuta un escaneo del entorno antes de hacer preguntas:

**Herramientas disponibles:**
- MCPs activos: context7, angular-guidelines, atlassian, etc.
- Skills cargados en `~/.claude/skills/`
- Agentes/subagentes disponibles
- Runtimes instalados: node, python, php, ruby, go, rust, etc.
- Herramientas CLI: git, docker, gh, uv, bun, composer, etc.
- Contenedores Docker activos

**Estado del proyecto:**
- ¿Existe código? (detectar `src/`, archivos de configuración conocidos)
- ¿Existe `openspec/`? ¿Tiene steering? ¿Tiene changes activos?
- ¿Existe `CLAUDE.md` local?
- Stack detectado desde archivos existentes (`package.json`, `pyproject.toml`, etc.)

El resultado del escaneo pre-rellena respuestas y acorta el cuestionario.

### Fase 2 — Cuestionario interactivo

Si el proyecto no tiene código: cuestionario completo (stack, patrones, equipo, etc.)
Si el proyecto tiene código: cuestionario reducido (confirmar detecciones, completar gaps)

**Principios del cuestionario:**
- Asume que el usuario no tiene conocimiento técnico
- Para cada opción con trade-offs, presentar ventajas e inconvenientes en lenguaje llano
- Si Claude tiene alta confianza en la mejor opción para el contexto dado, la recomienda
  explícitamente con justificación (ej: "Para un MVP solo recomiendo X porque...")
- El usuario siempre puede aceptar la recomendación o elegir otra opción

**Dimensiones del cuestionario:**

1. **Proyecto**
   - ¿Qué construye? (descripción libre, 1-3 frases)
   - ¿Para quién? (usuarios, sistemas, audiencia)
   - ¿Cuál es el bounded context? (qué NO hace)

2. **Stack** (si no detectado)
   - Tipo: web app / API / CLI / mobile / library / otro
   - Lenguaje principal — con trade-offs si el usuario no tiene preferencia
   - Framework principal — idem
   - Base de datos (si aplica)
   - Stack de testing preferido

3. **Equipo y rigor**
   - Tamaño del equipo: solo / 2-5 / >5
   - Nivel de rigor: MVP rápido / producción robusta / open source
   - ¿Tiene CI/CD? ¿Dónde? (GitHub Actions, GitLab CI, etc.)

4. **MCPs disponibles** (si se detectaron)
   - Confirmar cuáles quiere usar en este proyecto
   - ¿Context7 para documentación de librerías? (si disponible)
   - ¿Jira/Linear para tickets? (si disponible)

5. **Patrones preferidos** (opcionales, Claude recomienda según stack)
   - ¿Arquitectura preferida? (hexagonal, MVC, CQRS, etc.) — o "la que recomiende Claude"
   - ¿TDD? ¿Cobertura mínima?
   - ¿Formato de commits? (Conventional Commits, custom, etc.)

### Fase 3 — Generación de artefactos

Con las respuestas + escaneo del entorno, generar en paralelo:

**En `openspec/steering/`:**
- `product.md` — descripción, audiencia, bounded context
- `tech.md` — stack, versiones, herramientas
- `structure.md` — organización del código, capas propuestas
- `conventions.md` — reglas RFC 2119 derivadas del stack elegido
- `environment.md` *(nuevo)* — MCPs, herramientas, contenedores disponibles

**Skill del proyecto en `openspec/steering/`:**
- `project-skill.md` — skill de arquitectura y calidad específico del proyecto
  - Referenciado desde `openspec/config.yaml` como skill local
  - Cargado automáticamente por `/sdd-init` en sesiones futuras

**Archivo de reglas del proyecto en `openspec/steering/`:**
- `project-rules.md` — reglas de implementación granulares (convenciones de código,
  patrones de test, estilo, decisiones de librería, etc.)
  - Complementa `conventions.md` (que es más de arquitectura/diseño)
  - Es el archivo que se actualiza cuando el usuario corrige a Claude
  - Se mantiene referenciado desde `project-skill.md` para no duplicar contenido

**En `openspec/config.yaml`:**
- Añadir sección `environment:` con MCPs/tools disponibles
- Añadir sección `skills:` con lista de skills del proyecto (local: `openspec/steering/project-skill.md`)

### Fase 4 — Verificación de bootstrap (proyectos con código)

Si se detectó código existente, verificar:
- ¿El onboarding se ha ejecutado antes? (`openspec/steering/` existe y tiene contenido)
- Si no: advertir y sugerir ejecutar `/sdd-init` antes de cualquier `/sdd-new`
- `sdd-apply` comprobará que `openspec/steering/conventions.md` existe antes de implementar

### Fase 5 — Skill vivo: actualización por correcciones

Cuando el usuario corrige una decisión de Claude durante el desarrollo:
- Claude identifica qué convención/regla debe añadirse o actualizarse
- Actualiza `project-rules.md` con la nueva regla en formato RFC 2119
- Opcionalmente actualiza `conventions.md` si es una decisión de arquitectura
- Confirma al usuario qué ha aprendido y dónde lo ha guardado

El skill del proyecto crece de forma orgánica, acumulando el "estilo real" del proyecto.
`project-rules.md` es el archivo principal de crecimiento; `project-skill.md` y
`conventions.md` solo se tocan para cambios estructurales.

### Integración con Context7 (opcional)

Si `mcp__context7` está disponible y el stack tiene librerías reconocidas:
- Resolver IDs de librerías del stack detectado
- Añadir referencias en `tech.md` para que `sdd-apply` las use automáticamente
- No bloquear el onboarding si Context7 no responde

## Gestión del tamaño de los artefactos

Para evitar que los archivos crezcan sin control, el sistema de steering sigue una
jerarquía de archivos con responsabilidades separadas:

```
openspec/steering/
├── product.md          ← qué construye, para quién (estable, raramente cambia)
├── tech.md             ← stack, versiones (cambia con upgrades)
├── structure.md        ← capas, organización (cambia con refactors mayores)
├── conventions.md      ← reglas de arquitectura RFC 2119 (cambia con decisiones grandes)
├── environment.md      ← MCPs, tools, contenedores (cambia con el entorno)
├── project-skill.md    ← skill de arquitectura del proyecto (referencia los demás)
└── project-rules.md    ← reglas granulares de implementación (crece con el proyecto)
```

`project-skill.md` actúa como índice: es el archivo que Claude carga en sesión y que
referencia al resto. Así se mantiene pequeño y los detalles quedan en archivos específicos.

## Alternativas consideradas

**A. Ampliar `/sdd-steer` en lugar de `/sdd-init`**
Descartado: `sdd-steer` asume que el proyecto ya tiene código. El onboarding es para
proyectos en blanco. Son momentos distintos del ciclo de vida.

**B. Nuevo skill `/sdd-onboard` separado**
Descartado: el punto de entrada natural para un proyecto nuevo es `/sdd-init`.
Ampliar es más coherente que añadir un comando extra.

**C. Skill global en `~/.claude/skills/{project}/`**
Descartado: los skills globales afectan todas las sesiones de Claude en todos los contextos.
El skill del proyecto debe ser local a `openspec/` para que sea parte del proyecto mismo
y se pueda versionar junto con él si el usuario lo decide.

**D. Un único archivo `project-rules.md` para todo**
Descartado: separar arquitectura (conventions.md) de implementación (project-rules.md)
permite que `sdd-audit` use conventions.md como fuente de verdad arquitectural sin
contaminarlo con reglas de estilo granulares.

## Impacto

**Artefactos modificados:**
- `~/.claude/skills/sdd-init/SKILL.md` — añadir fases de onboarding
- `~/.claude/skills/sdd-apply/SKILL.md` — añadir verificación de bootstrap

**Artefactos nuevos:**
- `~/.claude/scripts/sdd-env-scan.sh` — script de escaneo de entorno
- `openspec/steering/environment.md` — spec del nuevo artefacto de entorno
- `openspec/steering/project-skill.md` — skill local del proyecto
- `openspec/steering/project-rules.md` — reglas granulares del proyecto

**No toca código Python del proyecto** — es cambio puramente de skills y scripts.

## Criterios de éxito

- Un proyecto nuevo puede arrancar con `/sdd-init` y obtener un `openspec/steering/`
  completo sin conocimiento técnico previo
- `sdd-apply` puede generar código correcto para el stack del proyecto usando solo
  el contexto de `openspec/steering/`
- El escaneo de entorno detecta correctamente MCPs, runtimes y tools disponibles
- Si Context7 está disponible, `tech.md` contiene referencias a documentación de librerías
- Cuando el usuario corrige a Claude, `project-rules.md` se actualiza y la corrección
  no se repite en sesiones futuras
- Los archivos de steering se mantienen legibles: ninguno supera ~150 líneas en un
  proyecto típico
