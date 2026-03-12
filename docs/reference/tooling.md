# Tooling Reference

The tooling domain covers every Claude Code skill that drives the SDD workflow: `/sdd-init` (project bootstrap with guided onboarding), `/sdd-new` (explore + propose), `/sdd-ff` (fast-forward through all documentation phases), `/sdd-apply` (task-by-task implementation with atomic commits), `/sdd-verify` (tests + quality gates + self-review checklist), `/sdd-archive` (close a change, merge deltas into canonical specs, update INDEX.md), `/sdd-steer` (generate and sync steering conventions), `/sdd-audit` (detect convention violations), and `/sdd-discover` (infer canonical specs from an existing codebase). Together these skills form the AI-assisted loop that turns a ticket into working, documented, tested code without leaving your editor.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-01` | Ubiquitous | The proyecto SHALL tener ruff como dependencia de desarrollo. |
| `REQ-02` | Ubiquitous | The configuración SHALL estar en `pyproject.toml` con `line-length = 100` y reglas `E`, `F`, `I`. |
| `REQ-03` | Ubiquitous | The código en `src/` y `tests/` SHALL pasar `ruff check` y `ruff format --check` sin errores. |
| `REQ-04` | Ubiquitous | The script `~/.claude/scripts/sdd-tui-lint.sh` SHALL ejecutar el quality gate. |
| `REQ-ST01` | Event | When invoked, the skill SHALL create `openspec/steering/` if it does not exist. |
| `REQ-ST02` | Event | When bootstrapping, the skill SHALL generate all four steering files. |
| `REQ-ST03` | Ubiquitous | Conventions SHALL be derived from: architecture/code-quality skills, MEMORY.md, and actual code patterns. |
| `REQ-ST04` | Ubiquitous | Each convention SHALL include: scope, RFC 2119 level (MUST/SHOULD/MAY), and a one-line rationale. |
| `REQ-ST05` | Unwanted | If `openspec/steering/` already has content, the skill SHALL warn and offer sync instead. |
| `REQ-ST06-08` | Event | Sync mode SHALL detect drift and propose changes — NOT auto-modify steering files. |
| `REQ-AU01` | Event | When invoked, the skill SHALL read `openspec/steering/conventions.md` first. |
| `REQ-AU02` | Unwanted | If `conventions.md` does not exist, the skill SHALL stop and instruct the user to run `/sdd-steer`. |
| `REQ-AU03` | Optional | Where a scope argument is provided, the skill SHALL restrict analysis to that path. |
| `REQ-AU04` | Ubiquitous | Without a scope, the skill SHALL analyze files modified since the base branch (`git diff --name-only`). |
| `REQ-AU05` | Ubiquitous | Each violation SHALL include: file path, approximate line, violated convention, and fix suggestion. |
| `REQ-AU06` | Event | When critical violations are found, the skill SHALL generate `/sdd-new` prompts for correction. |
| `REQ-AU07` | Unwanted | If no violations are found, the skill SHALL output a clean confirmation. |
| `REQ-AU08` | Optional | Where `conventions.md` exists, `/sdd-verify` SHOULD run `/sdd-audit` as Paso 5b. |
| `REQ-ENV01` | Event | When `/sdd-init` is invoked, the skill SHALL scan the environment |
| `REQ-ENV02` | Event | When source files or known config files exist in the project root |
| `REQ-ENV03` | Event | When `openspec/steering/` already exists with content, the skill |
| `REQ-ENV04` | Ubiquitous | The environment scan SHALL complete silently — no intermediate |
| `REQ-Q01` | Event | When the project has no existing code, the skill SHALL present the |
| `REQ-Q02` | Event | When existing code is detected, the skill SHALL present a reduced |
| `REQ-Q03` | Ubiquitous | For each technical decision with multiple valid options, the |
| `REQ-Q04` | Ubiquitous | When Claude has high confidence in the best option given the |
| `REQ-Q05` | Ubiquitous | The questionnaire SHALL never require the user to know specific |
| `REQ-ART01` | Event | When all questionnaire answers are collected, the skill SHALL |
| `REQ-ART02` | Optional | Where `mcp__context7` is available, the skill SHALL resolve |
| `REQ-ART03` | Ubiquitous | The onboarding SHALL NOT block or fail if optional MCPs are unavailable. |
| `REQ-ART04` | Ubiquitous | `project-skill.md` SHALL act as an index file and SHALL NOT exceed 100 lines. |
| `REQ-ART05` | Ubiquitous | `project-rules.md` SHALL be the primary file for granular |
| `REQ-ART06` | Ubiquitous | `environment.md` SHALL document confirmed available tools and MCPs. |
| `REQ-AUDIT-EXT01` | Event | When `/sdd-audit` is invoked and `project-rules.md` exists, |
| `REQ-AUDIT-EXT02` | Ubiquitous | Violations from `project-rules.md` SHALL follow the same |
| `REQ-AUDIT-EXT03` | Ubiquitous | Rules in `project-rules.md` that duplicate linter coverage |
| `REQ-BOOT01` | Event | When `/sdd-apply` is invoked, the skill SHALL verify that |
| `REQ-BOOT02` | Unwanted | If `openspec/steering/conventions.md` does not exist, the |
| `REQ-BOOT03` | Event | When bootstrap verification passes, the skill SHALL read |
| `REQ-BOOT04` | Optional | Where `openspec/steering/project-skill.md` exists, the skill |
| `REQ-LIVE01` | Event | When the user explicitly instructs Claude to remember a rule, |
| `REQ-LIVE02` | Event | When Claude detects an implicit correction during implementation, |
| `REQ-LIVE03` | Ubiquitous | Rules added to `project-rules.md` SHALL follow RFC 2119 |
| `REQ-LIVE04` | Ubiquitous | Granular implementation rules SHALL go to `project-rules.md`. |
| `REQ-LIVE05` | Event | When a rule is saved, Claude SHALL confirm what was saved and where. |
| `REQ-LIVE06` | Unwanted | If `project-rules.md` does not exist when a rule needs saving, |
| `REQ-MD-01` | Ubiquitous | When generating `design.md`, the `## Arquitectura` section SHALL |
| `REQ-MD-02` | Ubiquitous | The diagram type SHALL be chosen according to the situation: |
| `REQ-MD-03` | Ubiquitous | The diagram SHALL be placed within the `## Arquitectura` section, |
| `REQ-MD-04` | Optional | When generating `proposal.md`, the `## Solución Propuesta` section |
| `REQ-MD-05` | Ubiquitous | Mermaid blocks in TUI render as code blocks (rich.Markdown fallback). |
| `REQ-MD-06` | Ubiquitous | Diagrams are snapshots of the design at authoring time. If the |
| `REQ-IDX-01` | Ubiquitous | The `openspec/INDEX.md` SHALL exist at the root of `openspec/` |
| `REQ-IDX-02` | Ubiquitous | Each domain entry SHALL contain: |
| `REQ-IDX-03` | Ubiquitous | The INDEX.md SHALL include a header note explaining its purpose |
| `REQ-IDX-04` | Ubiquitous | The INDEX.md SHALL remain under 400 lines regardless of the |
| `REQ-IDX-05` | Unwanted | If a domain in `openspec/specs/` has no entry in INDEX.md, |
| `REQ-ARC-01` | Event | When closing a change that adds or modifies a canonical spec, |
| `REQ-ARC-02` | Event | When closing a change that adds a new domain, |
| `REQ-ARC-03` | Ubiquitous | The INDEX.md update SHALL happen after merging delta specs |
| `REQ-BOOT-01` | Event | When sdd-archive runs Paso 2b and `openspec/INDEX.md` does not |
| `REQ-BOOT-02` | Ubiquitous | The bootstrapped INDEX.md SHALL follow the standard format: |
| `REQ-BOOT-03` | Unwanted | If `openspec/specs/` is empty or does not exist, |
| `REQ-BOOT-04` | Ubiquitous | After bootstrap, sdd-archive SHALL continue with the |
| `REQ-EXP-01` | Event | When `openspec/INDEX.md` exists, sdd-explore SHALL read it |
| `REQ-EXP-02` | Event | When INDEX.md is available, sdd-explore SHALL use it to identify |
| `REQ-EXP-03` | Unwanted | If `openspec/INDEX.md` does not exist, sdd-explore SHALL |
| `REQ-EXP-04` | Ubiquitous | Domain selection SHALL be based on keyword matching between |
| `REQ-HINT-01` | Event | When `/sdd-init` completes and `openspec/specs/` is empty, |
| `REQ-HINT-02` | State | While `openspec/specs/` contains at least one spec file, |
| `REQ-HINT-03` | Ubiquitous | The hint SHALL appear as the last item in the "Próximos pasos" |
| `REQ-DISC-01` | Event | When `/sdd-discover` is invoked, the skill SHALL scan the |
| `REQ-DISC-02` | Ubiquitous | Domain detection SHALL consider top-level subdirectories |
| `REQ-DISC-03` | Unwanted | If no source files are found, the skill SHALL stop and |
| `REQ-DISC-04` | Event | When domains are identified, the skill SHALL present a summary |
| `REQ-DISC-05` | Event | When the user confirms, the skill SHALL proceed. When the user |
| `REQ-DISC-06` | Event | When analyzing each domain, the skill SHALL delegate the analysis |
| `REQ-DISC-06b` | Ubiquitous | Subagents SHALL run in parallel — each writes its spec to |
| `REQ-DISC-07` | Event | When generating a spec, the subagent SHALL produce a valid |
| `REQ-DISC-08` | Ubiquitous | All generated specs SHALL have `Status: inferred` in Metadata. |
| `REQ-DISC-09` | Ubiquitous | REQs in inferred specs SHALL be marked with |
| `REQ-DISC-10` | Ubiquitous | Inferred specs SHALL include a closing note: |
| `REQ-DISC-11` | Unwanted | If a spec already exists at `openspec/specs/{dominio}/spec.md`, |
| `REQ-DISC-12` | Event | When all specs are generated, the skill SHALL create or update |
| `REQ-DISC-13` | Event | When `openspec/INDEX.md` already exists, the skill SHALL only |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| Skill separado `/sdd-discover` | Fase integrada en `sdd-init` | `sdd-init` se mantiene rápido y predecible |
| Hint en `sdd-init` | Auto-ejecutar `sdd-discover` | El usuario decide cuándo hacer el análisis |
| `Status: inferred` como diferenciador | Badge visual en SpecHealthScreen | El estado en el archivo es señal suficiente; evita cambios en el TUI |
| Confirmación interactiva con listado | Análisis silencioso | El usuario valida dominios antes de escribir archivos |
| Subagentes en paralelo | Análisis secuencial en un contexto | Contexto aislado por dominio; proyectos grandes no saturan el orquestador |
