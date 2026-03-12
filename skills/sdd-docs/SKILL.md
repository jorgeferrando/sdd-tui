---
name: sdd-docs
description: SDD Docs - Genera documentación MkDocs desde openspec/ usando AI. Corre sdd-docs --fill --force para producir docs publicables sin placeholders. Uso - /sdd-docs.
---

# SDD Docs

> Genera un site de documentación MkDocs para cualquier proyecto con `openspec/`.
> Usa la Claude API (o cualquier LLM configurado) para producir prosa narrativa directamente,
> sin placeholders ni paso manual de relleno.

## Usage

```
/sdd-docs          # Regenerar docs/ completo con contenido rico
```

## Prerequisitos

- `openspec/` existe en el proyecto (si no: ejecutar `/sdd-init` primero)
- `sdd-tui` instalado con el extra `[fill]`: `pip install sdd-tui[fill]`
- `ANTHROPIC_API_KEY` (u otro LLM env var soportado) disponible en el entorno

## Paso 1: Verificar entorno

Comprobar que el LLM está disponible:

```bash
echo $ANTHROPIC_API_KEY  # debe mostrar una key, no estar vacío
```

Si no está configurada:
1. Obtener una API key en https://console.anthropic.com
2. Exportarla: `export ANTHROPIC_API_KEY=sk-ant-...`
3. (Opcional) Añadirla a `~/.zshrc` o `~/.bashrc` para persistencia

## Paso 2: Generar documentación

```bash
sdd-docs --fill --force
```

El CLI leerá `openspec/` completo, construirá el contexto del proyecto, y generará:
- `mkdocs.yml` — configuración completa (nav, Mermaid, Material features)
- `docs/index.md` — home page narrativa (problema, herramientas, quick start, diagrama)
- `docs/reference/{domain}.md` — una página por dominio, con prosa + tablas REQ/decisiones
- `docs/changelog.md` — desde `openspec/changes/archive/`

Sin placeholders. Output directamente publicable.

## Paso 3: Verificar resultado

```bash
mkdocs serve
```

Revisar en el browser local. Si alguna sección no es satisfactoria, se puede editar
manualmente y commitear — el próximo `sdd-docs --fill --force` regenerará de nuevo.

## Fallback sin API key

Si `ANTHROPIC_API_KEY` no está disponible, el CLI avisa y genera con placeholders:

```bash
sdd-docs --force  # sin --fill: comportamiento anterior con placeholders
```

En ese caso, rellenar los placeholders manualmente editando los archivos generados.

## Providers soportados

| Env var | Provider |
|---------|----------|
| `ANTHROPIC_API_KEY` | Claude (Haiku por defecto) |
| _(futuro)_ `OPENAI_API_KEY` | GPT / Codex |
| _(futuro)_ `GEMINI_API_KEY` | Gemini |

El primer env var disponible gana. Ver `src/sdd_tui/ai_docs.py` → `make_provider()`.

## Output al usuario

```
sdd-docs: Overwritten 10 file(s) (AI-enriched), skipped 0

  +  mkdocs.yml
  +  docs/index.md
  +  docs/reference/core.md
  ...

Next: run 'mkdocs serve' to preview
```
