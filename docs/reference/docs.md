# Docs Reference

The `docs` domain provides the `sdd-docs` CLI that turns an `openspec/` directory into a deployable MkDocs Material site. Running `sdd-docs` generates `mkdocs.yml`, a home page, one reference page per spec domain (with requirements and decisions tables), and a changelog derived from the archive. Existing files are skipped unless `--force` is passed. Pages that require human judgement — overviews, quickstarts, examples — are emitted as typed HTML comment placeholders, which the **`/sdd-docs` skill** then fills in with context-aware prose using Claude Code. The result is a fully navigable, searchable documentation site generated from the same source of truth as the implementation.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-CLI01` | Event | When `sdd-docs` is invoked, the CLI SHALL search for `openspec/` starting from the current working directory, traversing up to the git root. |
| `REQ-CLI02` | Unwanted | If no `openspec/` directory is found, the CLI SHALL exit with code 1 and print: `"openspec/ not found. Run /sdd-init in Claude Code first."`. |
| `REQ-CLI03` | Ubiquitous | The CLI SHALL accept `--help` and display all flags with one-line descriptions. #### Flags |
| `REQ-CLI04` | Optional | Where `--dry-run` is provided, the CLI SHALL list all files that would be generated or skipped, without writing anything. |
| `REQ-CLI05` | Optional | Where `--output <dir>` is provided, the CLI SHALL write `docs/` and `mkdocs.yml` under `<dir>` instead of the default (git root). |
| `REQ-CLI06` | Optional | Where `--force` is provided, the CLI SHALL overwrite existing files. Without `--force`, existing files SHALL be skipped with a warning. |
| `REQ-CLI07` | Event | When generation completes, the CLI SHALL print a summary: files created, skipped, and a next step message. #### Generación de `mkdocs.yml` |
| `REQ-MKD01` | Ubiquitous | The generated `mkdocs.yml` SHALL use MkDocs Material theme with: light/dark toggle, navigation tabs, navigation top, content.code.copy, search.highlight. |
| `REQ-MKD02` | Ubiquitous | `site_name` SHALL be derived from `openspec/steering/product.md` (first H1), `openspec/config.yaml` (project name field if present), or the git repo directory name as fallback — in that order. |
| `REQ-MKD03` | Ubiquitous | `site_description` SHALL be derived from the first paragraph of `openspec/steering/product.md`, or left as a placeholder if steering is absent. |
| `REQ-MKD04` | Ubiquitous | The nav structure SHALL be derived from available content: one nav entry per spec domain, plus standard sections (Changelog, Reference) when the corresponding source exists in openspec/. |
| `REQ-MKD05` | Unwanted | If a nav entry points to a page that was not generated, the CLI SHALL NOT include that entry in the nav. #### Generación de páginas desde `openspec/specs/` |
| `REQ-SPEC01` | Ubiquitous | For each domain in `openspec/specs/`, the CLI SHALL generate `docs/reference/{domain}.md` with: spec title, requirements table, decisions table. |
| `REQ-SPEC02` | Ubiquitous | The requirements table SHALL include columns: ID, Type (EARS), Description. Content is extracted directly from the spec's EARS requirements. |
| `REQ-SPEC03` | Ubiquitous | The decisions table SHALL include columns: Decision, Discarded Alternative, Reason. Content is extracted from the spec's decisions section. |
| `REQ-SPEC04` | Optional | Where `openspec/steering/product.md` exists, the CLI SHALL inject a one-sentence domain summary at the top of each reference page. Where steering is absent, it SHALL insert a placeholder. #### Generación de Changelog |
| `REQ-CL01` | Event | When `openspec/changes/archive/` contains at least one change, the CLI SHALL generate `docs/changelog.md` from the archive. |
| `REQ-CL02` | Ubiquitous | Each archived change SHALL appear as a list item with: change name, archive date (from directory prefix), and first line of `proposal.md` description field (if parseable), or change name as fallback. |
| `REQ-CL03` | Ubiquitous | Changes SHALL be ordered newest-first. |
| `REQ-CL04` | Unwanted | If `openspec/changes/archive/` is absent or empty, the CLI SHALL NOT generate `docs/changelog.md` and SHALL NOT include it in the nav. #### Generación de página Home |
| `REQ-HOME01` | Ubiquitous | The CLI SHALL generate `docs/index.md` with: project name (from REQ-MKD02), a placeholder for the project description, and a placeholder for the "quick start" section. |
| `REQ-HOME02` | Optional | Where `openspec/steering/product.md` exists, the CLI SHALL use its content to populate the description section instead of a placeholder. #### Placeholders |
| `REQ-PH01` | Ubiquitous | Placeholders SHALL use the format: `<!-- sdd-docs:placeholder type="{type}" description="{what goes here}" -->`. |
| `REQ-PH02` | Ubiquitous | Placeholder types: `description`, `quickstart`, `prose`, `example`, `diagram`. |
| `REQ-PH03` | Ubiquitous | Every generated page SHALL contain at most one placeholder per logical section. Placeholder density SHALL NOT exceed 50% of a page's content. #### Idempotencia |
| `REQ-IDEM01` | Ubiquitous | Running `sdd-docs` twice without `--force` SHALL produce no changes — existing files are skipped, not overwritten. |
| `REQ-IDEM02` | Ubiquitous | Running `sdd-docs --force` twice SHALL produce identical output — the generation is deterministic given the same openspec/ state. ### Skill `/sdd-docs` |
| `REQ-SK01` | Event | When `/sdd-docs` is invoked, the skill SHALL check if `docs/` and `mkdocs.yml` exist. If absent, it SHALL run `sdd-docs` first. |
| `REQ-SK02` | Event | When scaffold exists, the skill SHALL scan all generated files for placeholders matching `<!-- sdd-docs:placeholder ... -->`. |
| `REQ-SK03` | Ubiquitous | For each placeholder, the skill SHALL read the relevant steering files (`product.md`, `tech.md`, `structure.md`) to generate appropriate prose. |
| `REQ-SK04` | Ubiquitous | The skill SHALL replace each placeholder with generated prose, preserving the surrounding Markdown structure. |
| `REQ-SK05` | Ubiquitous | The skill SHALL NOT modify sections of pages that were mechanically generated (requirements tables, decisions tables, changelog entries). |
| `REQ-SK06` | Event | When the skill completes, it SHALL report: pages updated, total placeholders filled, and a reminder to review before publishing. |
| `REQ-SK07` | Unwanted | If `openspec/steering/` does not exist, the skill SHALL warn that output quality will be lower (no project context) and proceed with best-effort prose. ### Distribución |
| `REQ-DIST01` | Ubiquitous | `sdd-docs` SHALL be declared as an entry point in `pyproject.toml`: `sdd-docs = "sdd_tui.docs_gen:main"`. |
| `REQ-DIST02` | Ubiquitous | The `/sdd-docs` skill SHALL be distributed via `sdd-setup` alongside the other SDD skills, fetched from the GitHub repository. |
| `REQ-DIST03` | Ubiquitous | The Homebrew formula's `test` block SHALL verify that `sdd-docs --help` exits with code 0 (alongside existing `sdd-tui` and `sdd-setup` checks). ## Escenarios de Verificación **REQ-CLI01/02 — openspec/ no encontrado** **Dado** que el directorio actual no contiene `openspec/` ni ningún padre hasta el root **Cuando** el usuario ejecuta `sdd-docs` **Entonces** el CLI imprime `"openspec/ not found. Run /sdd-init in Claude Code first."` y sale con código 1 **REQ-CLI06 / REQ-IDEM01 — no sobreescribir sin --force** **Dado** que `docs/index.md` ya existe **Cuando** el usuario ejecuta `sdd-docs` (sin --force) **Entonces** `docs/index.md` no se modifica y el summary muestra "index.md: skipped (use --force to overwrite)" **REQ-SPEC01/02 — generación de página de referencia** **Dado** que `openspec/specs/core/spec.md` existe con requisitos EARS **Cuando** se ejecuta `sdd-docs` **Entonces** se genera `docs/reference/core.md` con tabla de requisitos (ID \| Type \| Description) y tabla de decisiones si la spec tiene sección de decisiones **REQ-CL01-03 — changelog desde archive** **Dado** que `openspec/changes/archive/` tiene 5 directorios con prefijo fecha **Cuando** se ejecuta `sdd-docs` **Entonces** `docs/changelog.md` lista los 5 changes ordenados newest-first con nombre, fecha, y descripción del proposal.md **REQ-SK01 — scaffold ausente** **Dado** que `docs/` no existe **Cuando** el usuario invoca `/sdd-docs` **Entonces** el skill ejecuta `sdd-docs` primero, luego procede a rellenar placeholders ## Interfaces / Contratos ### CLI `sdd-docs` — flags \| Flag \| Tipo \| Descripción \| \|------\|------\|-------------\| \| `--dry-run` \| bool \| Listar archivos sin escribir \| \| `--output <dir>` \| str \| Directorio de salida alternativo \| \| `--force` \| bool \| Sobreescribir archivos existentes \| \| `--help` \| bool \| Mostrar ayuda \| ### Exit codes `sdd-docs` \| Código \| Significado \| \|--------\|-------------\| \| 0 \| Éxito (incluyendo "archivos skipped") \| \| 1 \| `openspec/` no encontrado o error de escritura \| ### Formato de placeholder ```html <!-- sdd-docs:placeholder type="description" description="2-3 sentence overview of the project for end users" --> ``` ### Estructura de salida generada ``` docs/ ├── index.md ← home page ├── reference/ │ ├── {domain1}.md ← una por cada openspec/specs/{domain}/ │ └── {domain2}.md └── changelog.md ← de openspec/changes/archive/ (si existe) mkdocs.yml ← site config con nav derivado del contenido ``` ## Decisiones Tomadas \| Decisión \| Alternativa Descartada \| Motivo \| \|---------\|----------------------\|--------\| \| CLI separado del TUI \| Integrar en la TUI \| Más componible, testeable, invocable desde CI/CD \| \| Skill como capa separada \| CLI con LLM integrado \| Separación de concerns; CLI sin dependencia de API \| \| Placeholders en HTML comments \| Marcadores propietarios \| Compatible con MkDocs/Markdown renderers \| \| Un `docs/reference/{domain}.md` por dominio \| Todos en una página \| Navegación más limpia; secciones independientes \| \| Changelog desde openspec/archive \| Desde git log \| openspec contiene "por qué", no solo "qué" \| \| `sdd_tui/docs_gen.py` \| Módulo standalone \| Misma distribución que sdd-setup; un paquete \| \| `docs/` en git root por defecto \| `docs/` junto a openspec/ \| Convención MkDocs estándar \| \| No generar Getting Started ni workflow pages \| Generar todo \| Esas páginas son muy específicas del proyecto — mejor generarlas con el skill \| ## Abierto / Pendiente _(ninguno — scope claro)_ |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| CLI separado del TUI | Integrar en la TUI | Más componible, testeable, invocable desde CI/CD |
| Skill como capa separada | CLI con LLM integrado | Separación de concerns; CLI sin dependencia de API |
| Placeholders en HTML comments | Marcadores propietarios | Compatible con MkDocs/Markdown renderers |
| Un `docs/reference/{domain}.md` por dominio | Todos en una página | Navegación más limpia; secciones independientes |
| Changelog desde openspec/archive | Desde git log | openspec contiene "por qué", no solo "qué" |
| `sdd_tui/docs_gen.py` | Módulo standalone | Misma distribución que sdd-setup; un paquete |
| `docs/` en git root por defecto | `docs/` junto a openspec/ | Convención MkDocs estándar |
| No generar Getting Started ni workflow pages | Generar todo | Esas páginas son muy específicas del proyecto — mejor generarlas con el skill |
