# Proposal: SDD Tooling — Steering Generation + Architecture Audit

## Metadata
- **Change:** sdd-tooling-steer-audit
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Proyecto:** sdd-tui (skills globales)
- **Estado:** draft

## Problema / Motivación

### Problema 1 — Convenciones invisibles

Cuando un agente llega a un proyecto existente no conoce sus convenciones.
Las aprende gradualmente por errores: "esta clase necesita `final`",
"los handlers no pueden acceder al repositorio directamente", "los Request
son readonly". Cada convención no documentada cuesta un round de review de PR.

El costo no es solo tiempo — es fricción y ruido. Un revisor humano señala
"falta `final` en la clase" en lugar de discutir la lógica de negocio.

### Problema 2 — Drift entre intención y código

Los skills de arquitectura (`next-architecture`, `ms-crm-architecture`, etc.)
documentan cómo debería organizarse el código. Pero no hay ningún mecanismo
que detecte cuándo el código real se desvía de esos patrones.

Un agente puede implementar lógica de negocio en un Controller sin que nadie
lo señale hasta el PR review — cuando el costo de corregirlo es mayor.

## Solución Propuesta

### `/sdd-steer` — Generación de steering desde el codebase

Nuevo skill que analiza un proyecto existente y genera archivos de
"memoria persistente" en `openspec/steering/`:

```
openspec/steering/
├── product.md       ← qué construye el proyecto, para quién
├── tech.md          ← stack, versiones, herramientas clave
├── structure.md     ← organización del código, qué hace cada capa
└── conventions.md   ← reglas no escritas: final, readonly, naming, etc.
```

El skill tiene dos modos:
- **Bootstrap** (`/sdd-steer`): primera ejecución, genera todos los archivos
  analizando el código existente y los skills de arquitectura cargados
- **Sync** (`/sdd-steer sync`): detecta drift entre lo documentado y el
  código actual, propone actualizaciones

El archivo `conventions.md` es el más valioso: captura las reglas que
causan errores de PR pero que no están en ningún README:

```markdown
## PHP — Clases
- MUST use `final` keyword (no inheritance by convention)
- MUST declare all properties as `readonly` in Request objects

## CQRS — Handlers
- MUST NOT inject Repository directly — only via use case interfaces
- MUST receive a single Command/Query object as parameter

## Naming
- Commands: `{Verb}{Entity}Command` (CreateRateCommand)
- Handlers: `{Verb}{Entity}Handler` (CreateRateHandler)
```

### `/sdd-audit` — Detección de violaciones + prompts de corrección

Nuevo skill que analiza el codebase contra el steering generado y produce
un reporte de violaciones:

```
## Audit Report — next — 2026-03-04

### Crítico (bloquea PR review)
- [C01] `src/Handler/CreateRateHandler.php` — missing `final` keyword
- [C02] `src/Request/RateRequest.php` — property `$amount` is not readonly

### Importante (deuda técnica)
- [I01] `src/Controller/RateController.php` — contains business logic (lines 45-67)
- [I02] `src/Handler/UpdateRateHandler.php` — injects RateRepository directly

### Menor
- [M01] `src/Command/rate_create.php` — naming should be CreateRateCommand

## Acciones SDD

Para corregir los errores críticos:
/sdd-new "fix: missing final and readonly in Rate domain handlers and requests"

Para la deuda técnica:
/sdd-new "refactor: extract business logic from RateController to handler"
```

El reporte clasifica violaciones en tres niveles y genera los prompts
`/sdd-new` para iniciar la corrección con el flujo SDD completo.

## Alternativas Consideradas

| Alternativa | Ventajas | Desventajas | Decisión |
|------------|---------|------------|---------|
| Añadir reglas a skills existentes | Sin skill nuevo | No hay mecanismo de verificación activa | Descartada |
| Linter estático (PHPStan rules) | Automatizable en CI | No cubre patrones semánticos (dónde va la lógica) | Complementario, no excluyente |
| **Steering + Audit como skills separados** | Clara separación de responsabilidades | Dos skills nuevos a mantener | **Elegida** |

## Impacto Estimado

- **Dominio:** skills globales (`~/.claude/skills/`)
- **Archivos:** 2 nuevos SKILL.md
  - `~/.claude/skills/sdd-steer/SKILL.md`
  - `~/.claude/skills/sdd-audit/SKILL.md`
- **Archivos de output por proyecto:**
  - `openspec/steering/*.md` (generados por `/sdd-steer`)
- **Tests nuevos:** N/A (son prompt skills, no código ejecutable)
- **Breaking changes:** No
- **Dependencias:** Se apoya en los skills de arquitectura existentes
  (`next-architecture`, `ms-crm-architecture`, etc.) como fuente de patrones

## Criterios de Éxito

- [ ] `/sdd-steer` genera `conventions.md` con al menos las reglas de `final`
  y `readonly` detectadas en el proyecto next
- [ ] `/sdd-steer sync` detecta una clase nueva sin `final` y propone actualizar conventions.md
- [ ] `/sdd-audit` produce un reporte con al menos C/I/M clasificados
- [ ] Cada violación crítica tiene un prompt `/sdd-new` para corregirla
- [ ] El reporte de audit se puede usar como checklist en `/sdd-verify`

## Preguntas Abiertas

- [ ] ¿`openspec/steering/` va en el repo o en `.git/info/exclude` como el resto de openspec/?
- [ ] ¿`/sdd-audit` se ejecuta sobre archivos modificados o sobre todo el codebase?
- [ ] ¿El audit debe integrarse en `/sdd-verify` como paso automático o es manual?

## Notas

`/sdd-steer` es la respuesta directa al concepto de steering de cc-sdd
(Amazon Kiro). La diferencia: nuestro steering vive en `openspec/steering/`
y está versionado con el proyecto, no en `.kiro/`.

`/sdd-audit` responde al gap detectado en el reporte ejecutivo de 2026-03-04:
ninguna herramienta del ecosistema analizado tiene un mecanismo de verificación
activa de patrones de arquitectura. Es nuestra ventaja diferencial.

El skill de audit puede evolucionar para integrar su output directamente
en la View 8 (SpecHealthView) de sdd-tui, mostrando violaciones activas
junto a las métricas de spec quality.
