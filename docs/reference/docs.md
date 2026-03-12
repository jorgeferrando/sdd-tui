# Docs Reference

The docs domain is the documentation generation layer of sdd-tui. The `sdd-docs` CLI reads `openspec/` and produces a complete MkDocs Material site: `mkdocs.yml` with Material theme and nav, `docs/index.md` home page, one `docs/reference/{domain}.md` per canonical spec, and `docs/changelog.md` from the archive. Pages are generated with placeholder comments (`<!-- sdd-docs:placeholder ... -->`) that the `/sdd-docs` Claude Code skill then fills with context-aware prose by reading `openspec/steering/` and surrounding requirements. Running `sdd-docs` is idempotent — existing pages are skipped unless `--force` is used.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-CLI01` | Event | When `sdd-docs` is invoked, the CLI SHALL search for `openspec/` |
| `REQ-CLI02` | Unwanted | If no `openspec/` directory is found, the CLI SHALL exit with |
| `REQ-CLI03` | Ubiquitous | The CLI SHALL accept `--help` and display all flags with |
| `REQ-CLI04` | Optional | Where `--dry-run` is provided, the CLI SHALL list all files |
| `REQ-CLI05` | Optional | Where `--output <dir>` is provided, the CLI SHALL write |
| `REQ-CLI06` | Optional | Where `--force` is provided, the CLI SHALL overwrite existing |
| `REQ-CLI07` | Event | When generation completes, the CLI SHALL print a summary: |
| `REQ-MKD01` | Ubiquitous | The generated `mkdocs.yml` SHALL use MkDocs Material theme |
| `REQ-MKD02` | Ubiquitous | `site_name` SHALL be derived from `openspec/steering/product.md` |
| `REQ-MKD03` | Ubiquitous | `site_description` SHALL be derived from the first paragraph |
| `REQ-MKD04` | Ubiquitous | The nav structure SHALL be derived from available content: |
| `REQ-MKD05` | Unwanted | If a nav entry points to a page that was not generated, |
| `REQ-SPEC01` | Ubiquitous | For each domain in `openspec/specs/`, the CLI SHALL generate |
| `REQ-SPEC02` | Ubiquitous | The requirements table SHALL include columns: ID, Type (EARS), |
| `REQ-SPEC03` | Ubiquitous | The decisions table SHALL include columns: Decision, |
| `REQ-SPEC04` | Optional | Where `openspec/steering/product.md` exists, the CLI SHALL |
| `REQ-CL01` | Event | When `openspec/changes/archive/` contains at least one change, |
| `REQ-CL02` | Ubiquitous | Each archived change SHALL appear as a list item with: |
| `REQ-CL03` | Ubiquitous | Changes SHALL be ordered newest-first. |
| `REQ-CL04` | Unwanted | If `openspec/changes/archive/` is absent or empty, the CLI |
| `REQ-HOME01` | Ubiquitous | The CLI SHALL generate `docs/index.md` with: project |
| `REQ-HOME02` | Optional | Where `openspec/steering/product.md` exists, the CLI SHALL |
| `REQ-PH01` | Ubiquitous | Placeholders SHALL use the format: |
| `REQ-PH02` | Ubiquitous | Placeholder types: `description`, `quickstart`, `prose`, |
| `REQ-PH03` | Ubiquitous | Every generated page SHALL contain at most one placeholder |
| `REQ-IDEM01` | Ubiquitous | Running `sdd-docs` twice without `--force` SHALL produce |
| `REQ-IDEM02` | Ubiquitous | Running `sdd-docs --force` twice SHALL produce identical |
| `REQ-SK01` | Event | When `/sdd-docs` is invoked, the skill SHALL check if `docs/` and |
| `REQ-SK02` | Event | When scaffold exists, the skill SHALL scan all generated files for |
| `REQ-SK03` | Ubiquitous | For each placeholder, the skill SHALL read the relevant |
| `REQ-SK04` | Ubiquitous | The skill SHALL replace each placeholder with generated prose, |
| `REQ-SK05` | Ubiquitous | The skill SHALL NOT modify sections of pages that were |
| `REQ-SK06` | Event | When the skill completes, it SHALL report: pages updated, total |
| `REQ-SK07` | Unwanted | If `openspec/steering/` does not exist, the skill SHALL warn |
| `REQ-DIST01` | Ubiquitous | `sdd-docs` SHALL be declared as an entry point in |
| `REQ-DIST02` | Ubiquitous | The `/sdd-docs` skill SHALL be distributed via `sdd-setup` |
| `REQ-DIST03` | Ubiquitous | The Homebrew formula's `test` block SHALL verify that |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| CLI separado del TUI | Integrar en la TUI | Más componible, testeable, invocable desde CI/CD |
| LLM integrado en CLI via `--fill` | Skill como única capa AI | `--force` ya no destruye contenido enriquecido; un solo comando |
| `LLMProvider` Protocol + factory `make_provider()` | Hardcodear Anthropic | Añadir Codex/Gemini en el futuro = una clase + un `if` |
| Provider inyectado en `fill_*` functions | Singleton global | Tests simples: mock del Protocol, sin parchear SDKs externos |
| `anthropic` como optional dep `[fill]` | Dep runtime obligatoria | No rompe instalaciones base |
| Flag `--fill` explícito | AI siempre activo si hay API key | Comportamiento predecible; el usuario elige cuándo generar |
| Haiku como modelo por defecto | Sonnet/Opus | Docs generation es token-heavy; Haiku equilibra calidad/coste |
| Fallback a placeholders sin API key | Error fatal | Compatible hacia atrás; sin dependencia forzada |
| Placeholders en HTML comments | Marcadores propietarios | Compatible con MkDocs/Markdown renderers (modo fallback) |
| Un `docs/reference/{domain}.md` por dominio | Todos en una página | Navegación más limpia; secciones independientes |
| Changelog desde openspec/archive | Desde git log | openspec contiene "por qué", no solo "qué" |
| `sdd_tui/docs_gen.py` + `ai_docs.py` | Módulo standalone | Misma distribución que sdd-setup; un paquete |
| `docs/` en git root por defecto | `docs/` junto a openspec/ | Convención MkDocs estándar |
