# OpenSpec Index

> Índice de dominios canónicos. Actualizado por `sdd-archive` al cerrar cada change.
> **Uso:** leer este archivo primero; cargar solo los spec files de los dominios relevantes.
> Si este archivo no existe en un repo, explorar `openspec/specs/` directamente.

---

## tui (`specs/tui/spec.md`)
Capa de presentación Textual: todas las pantallas, bindings de teclado, navegación push/pop,
workers async y layout de widgets. Cubre desde EpicsView hasta pantallas de progreso, velocity y releases.
**Entidades:** `SddTuiApp`, `EpicsView`, `ChangeDetailScreen`, `SpecHealthScreen`, `SpecEvolutionScreen`, `DocumentViewerScreen`, `PipelinePanel`, `DecisionsTimeline`, `ProgressDashboard`, `VelocityScreen`, `ReleasesScreen`, `GitLogScreen`, `SkillPaletteScreen`, `HelpScreen`, `GitWorkflowSetupScreen`, `TodosScreen`
**Keywords:** screens, bindings, navigation, textual, widgets, async-workers, epics, detail, spec-health, evolution, progress, velocity, search, filter, milestone, clipboard, help, keyboard

---

## core (`specs/core/spec.md`)
Lógica de negocio central: modelos de datos, lectura de openspec/, inferencia de pipeline, git,
métricas de calidad, skills reader, deps check, config multi-proyecto, velocity, milestones y todos.
**Entidades:** `Change`, `Task`, `CommitInfo`, `TaskGitState`, `Pipeline`, `PhaseState`, `ChangeMetrics`, `Milestone`, `TodoItem`, `TodoFile`, `ChangeVelocity`, `VelocityReport`, `AppConfig`, `DeltaSpec`, `Decision`, `SkillInfo`, `Dep`; `load_changes()`, `load_all_changes()`, `load_config()`, `load_milestones()`, `load_todos()`, `compute_velocity()`, `parse_metrics()`, `repair_hints()`, `load_skills()`, `check_deps()`, `find_commit()`, `get_diff()`, `get_working_diff()`, `is_clean()`
**Keywords:** models, reader, git, pipeline, metrics, skills, deps, config, velocity, milestones, todos, task-parser, spec-parser, decisions, multi-project, openspec-not-found

---

## distribution (`specs/distribution/spec.md`)
Instalación y distribución end-to-end: CLI `sdd-setup`, Homebrew formula, instaladores Linux/Windows,
release workflow con changelog automático desde openspec/archive y version markers.
**Entidades:** `sdd-setup` CLI, `Formula/sdd-tui.rb`, `ReleaseWorkflowConfig`, `scripts/release.sh`, `scripts/changelog.py`, `openspec/versions/X.Y.Z.yaml`
**Keywords:** install, homebrew, brew, uv, pipx, setup, skills-install, release, changelog, versioning, semver, formula, linux, windows, powershell, package

---

## tooling (`specs/tooling/spec.md`)
Quality gates Python (ruff), skills SDD (steer, audit, init onboarding, apply bootstrap, living rules,
discover reverse-spec) y convención de diagramas Mermaid en design.md.
**Entidades:** `ruff`, `sdd-steer`, `sdd-audit`, `sdd-init`, `sdd-discover`, `openspec/steering/`, `conventions.md`, `project-rules.md`, `environment.md`, `project-skill.md`; Mermaid en `design.md`
**Keywords:** linting, ruff, steering, audit, conventions, init, onboarding, bootstrap, mermaid, diagram, project-rules, living-rules, rfc2119, quality-gate, index, openspec-index, two-level-lookup, sdd-explore, sdd-archive, index-bootstrap, discover, reverse-spec, inferred, canon-inicial, subagent

---

## docs (`specs/docs/spec.md`)
Generador de documentación MkDocs desde openspec/: CLI `sdd-docs` (mecánico) + skill `/sdd-docs`
(inteligente, rellena placeholders con Claude). Site en GitHub Pages.
**Entidades:** `sdd-docs` CLI, `sdd_tui/docs_gen.py`, `mkdocs.yml`, `docs/reference/{domain}.md`, `docs/changelog.md`, `<!-- sdd-docs:placeholder ... -->`
**Keywords:** docs, mkdocs, documentation, site, generator, placeholder, changelog, github-pages, material-theme, reference, scaffold

---

## tests (`specs/tests/spec.md`)
Infraestructura de tests TUI con pytest-asyncio: fixtures, patrones de mock de GitReader,
granularidad de tests y cobertura de pantallas Textual con Pilot.
**Entidades:** `pytest-asyncio`, `SddTuiApp.run_test()`, `Pilot`, `app_with_changes`, `openspec_with_archive`, `@pytest_asyncio.fixture`
**Keywords:** pytest, asyncio, testing, tui-tests, pilot, fixtures, mock, gitreader, conftest, run-test

---

## github (`specs/github/spec.md`)
Integración con GitHub vía `gh` CLI: CI status, ship shortcut (clipboard), pantalla de releases.
Cargado async en ChangeDetailScreen bajo demanda para evitar O(N) llamadas al abrir la app.
**Entidades:** `CiStatus`, `ReleaseInfo`, `get_ci_status()`, `get_releases()`, `PipelinePanel` (fila CI), `ReleasesScreen`
**Keywords:** github, ci, pipeline, releases, gh-cli, pr, workflow, ship, clipboard, async

---

## providers (`specs/providers/spec.md`)
Abstracción de proveedores externos (git hosting, issue tracking) mediante `typing.Protocol`.
Permite cambiar de GitHub a Bitbucket/JIRA/Trello sin cambiar código de presentación o dominio.
**Entidades:** `IssueTracker`, `GitHost`, `GitHubHost`, `GitHubIssueTracker`, `NullGitHost`, `NullIssueTracker`, `GitWorkflowConfig`, `make_git_host()`, `make_issue_tracker()`
**Keywords:** providers, abstraction, protocol, git-host, issue-tracker, config, wizard, setup, null-provider, github-flow, bitbucket, jira
