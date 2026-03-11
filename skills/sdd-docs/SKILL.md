---
name: sdd-docs
description: SDD Docs - Genera documentación MkDocs desde openspec/. Capa mecánica via CLI + capa inteligente que rellena placeholders con prosa. Uso - /sdd-docs.
---

# SDD Docs

> Genera un site de documentación MkDocs para cualquier proyecto con `openspec/`.
> Combina el CLI `sdd-docs` (scaffold mecánico) con Claude Code (prosa inteligente).

## Usage

```
/sdd-docs          # Generar o completar docs/ para el proyecto actual
/sdd-docs --check  # Solo verificar qué placeholders quedan pendientes
```

## Prerequisitos

- `openspec/` existe en el proyecto (si no: ejecutar `/sdd-init` primero)
- `sdd-tui` instalado (`sdd-docs` disponible en PATH)
- Estar en el directorio raíz del proyecto (o cualquier subdirectorio)

## Paso 1: Verificar scaffold

Comprobar si `docs/` y `mkdocs.yml` ya existen:

```bash
ls docs/ 2>/dev/null && echo "scaffold exists" || echo "no scaffold"
ls mkdocs.yml 2>/dev/null && echo "mkdocs.yml exists" || echo "no mkdocs.yml"
```

- Si **no existen**: ejecutar `sdd-docs` para generar el scaffold.
- Si **existen**: saltar al Paso 3 para buscar placeholders.

## Paso 2: Generar scaffold mecánico

```bash
sdd-docs
```

El CLI lee `openspec/` y genera:
- `mkdocs.yml` — site config con nav derivado del contenido disponible
- `docs/index.md` — home page
- `docs/reference/{domain}.md` — una página por dominio en `openspec/specs/`
- `docs/changelog.md` — desde `openspec/changes/archive/` (si existe)

Revisar el output del CLI para confirmar qué archivos fueron generados.

Si ya existían archivos (skipped): usar `sdd-docs --force` para regenerar, o
trabajar con los existentes.

## Paso 3: Identificar placeholders

Buscar todos los placeholders en los archivos generados:

```bash
grep -r "sdd-docs:placeholder" docs/
```

Cada placeholder tiene este formato:
```
<!-- sdd-docs:placeholder type="{type}" description="{what goes here}" -->
```

Tipos posibles:
- `description` — descripción del proyecto o dominio para usuarios finales
- `quickstart` — pasos de instalación y primer uso
- `prose` — párrafo narrativo sobre un concepto o dominio
- `example` — ejemplo de uso concreto con código
- `diagram` — diagrama de arquitectura o flujo

## Paso 4: Cargar contexto del proyecto

Leer los steering files disponibles para tener contexto del proyecto:

```
openspec/steering/product.md    ← qué construye, para quién
openspec/steering/tech.md       ← stack, versiones, herramientas
openspec/steering/structure.md  ← organización del código, capas
```

Si alguno no existe, continuar con el contexto disponible.

## Paso 5: Rellenar placeholders

Para cada placeholder encontrado:

1. Leer el contexto de la página (título, sección, REQs circundantes si es reference page)
2. Usar el steering como fuente de verdad para nombres, stack, convenciones
3. Generar prosa apropiada según el tipo:

**`description`** — 2-3 frases orientadas al usuario final. Qué hace el proyecto,
qué problema resuelve, quién lo usa. Sin detalles técnicos internos.

**`quickstart`** — Pasos numerados: instalar → configurar → primer uso. Incluir
comandos reales derivados del `tech.md`. Máximo 5-6 pasos.

**`prose`** — Párrafo explicativo sobre el dominio o concepto. Orientado a alguien
que no conoce el proyecto. Derivar de los REQs circundantes en la misma página.

**`example`** — Bloque de código con comentarios. Usar el stack real del proyecto.
Mostrar el caso de uso más común del dominio, no edge cases.

**`diagram`** — Diagrama Mermaid apropiado al contexto. Ver tipos disponibles en
el skill `sdd-design`. Para docs: preferir `flowchart LR` para navegación/flujo,
`classDiagram` para estructuras de datos.

Reemplazar el HTML comment con el contenido generado. Mantener la estructura
Markdown circundante intacta.

## Paso 6: Verificar resultado

Tras rellenar todos los placeholders:

```bash
grep -r "sdd-docs:placeholder" docs/ && echo "placeholders remain" || echo "all filled"
```

Reportar al usuario:
- Páginas actualizadas
- Total placeholders rellenados
- Si quedan placeholders: listarlos con su ubicación

## Reglas

- **NO modificar** secciones generadas mecánicamente: tablas de REQs, tablas de decisiones,
  entradas del changelog. Solo tocar los placeholders.
- **NO inventar** nombres de comandos, versiones o rutas. Derivar del steering o del código.
- Si `openspec/steering/` no existe: generar prosa best-effort basada en los specs disponibles.
  Advertir al usuario que la calidad será menor sin steering.
- Si un placeholder es ambiguo: preguntar al usuario antes de rellenar.
- La prosa debe ser en el **idioma del proyecto** (detectar desde steering o README).

## Output al usuario

```
sdd-docs complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scaffold: X archivos generados
Placeholders rellenados: Y
Páginas actualizadas: [lista]

Próximo: mkdocs serve  # para preview local
         mkdocs build  # para generar site/
```
