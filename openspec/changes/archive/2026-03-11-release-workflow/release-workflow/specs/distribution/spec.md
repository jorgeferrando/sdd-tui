# Spec: Distribution — Release Workflow

## Metadata
- **Dominio:** distribution
- **Change:** release-workflow
- **Jira:** N/A
- **Fecha:** 2026-03-11
- **Versión:** 2.0
- **Estado:** draft

## Contexto

Extensión del dominio `distribution` (v1.0 — sdd-setup-experience) para cubrir el
ciclo de vida completo de releases: versionado semántico, automatización del proceso
de release, generación de changelog desde `openspec/`, y actualización de la
Homebrew formula.

El release workflow es **optativo** — no todos los proyectos que usan sdd-tui publican
releases. La configuración se hace durante el setup inicial del proyecto (`S` en EpicsView)
y se persiste en `openspec/config.yaml`. Si no está configurado al abrir la TUI, el
usuario recibe una notificación que invita a configurarlo.

## Comportamiento Actual

- `pyproject.toml` tiene `version = "0.1.0"` fijo, nunca bumpeado
- `Formula/sdd-tui.rb` referencia `v0.1.0.tar.gz` con SHA256 como placeholder
- Sin tags git publicados
- Sin `release_workflow:` en `config.yaml`
- `ReleasesScreen` en la TUI siempre muestra "No releases found"
- `CHANGELOG.md` no existe en el repo

## Requisitos (EARS)

### Configuración en `config.yaml`

- **REQ-CFG01** `[Ubiquitous]` `openspec/config.yaml` SHALL support a `release_workflow:`
  section with fields: `enabled`, `versioning`, `changelog_source`, `homebrew_formula`.

- **REQ-CFG02** `[Ubiquitous]` Default values when `release_workflow:` is absent or
  fields are missing: `enabled=false`, `versioning="semver"`,
  `changelog_source="openspec"`, `homebrew_formula=null`.

- **REQ-CFG03** `[Ubiquitous]` `ReleaseWorkflowConfig` SHALL be a dataclass loaded
  by `load_git_workflow_config` (or a new `load_release_config`) from `config.yaml`.

### Setup Wizard — nuevos pasos

- **REQ-WZ06** `[Event]` When the user reaches the release configuration step in
  `GitWorkflowSetupScreen`, the system SHALL ask: "Does this project publish releases?"
  with options `yes` / `no`.

- **REQ-WZ07** `[Event]` When the user selects `yes`, the wizard SHALL present a
  versioning scheme question: `semver` / `calver` / `none`.

- **REQ-WZ08** `[Event]` When the user selects `yes`, the wizard SHALL ask for a
  Homebrew formula path (default `Formula/{project}.rb`) with an option `none`.

- **REQ-WZ09** `[Event]` When the wizard completes, the system SHALL write
  `release_workflow:` to `openspec/config.yaml` alongside the existing `git_workflow:`
  section.

### Startup check — `App.on_mount`

- **REQ-OB01** `[Event]` When the app mounts and `release_workflow:` is absent from
  `openspec/config.yaml`, the system SHALL display a one-time notification:
  `"Release workflow not configured — press S to set up"`.

- **REQ-OB02** `[Ubiquitous]` The notification SHALL appear only once per session,
  not on every screen change.

- **REQ-OB03** `[Unwanted]` If `release_workflow.enabled = false`, the system SHALL
  NOT show the notification. The user has explicitly opted out.

### Script `scripts/release.sh`

- **REQ-REL01** `[Event]` When `scripts/release.sh <version>` is invoked, the script
  SHALL validate that the version argument matches the format `X.Y.Z` (semver) and
  exit with code 1 if not.

- **REQ-REL02** `[Event]` When invoked with a valid version, the script SHALL update
  `version` in `pyproject.toml` to the given value automatically before creating the tag.

- **REQ-REL03** `[Event]` When invoked, the script SHALL run `uv run pytest` and abort
  with exit code 1 if any test fails. The tag SHALL NOT be created if tests fail.

- **REQ-REL04** `[Unwanted]` If the working tree is dirty (excluding `openspec/` and
  `.claude/`), the script SHALL abort with exit code 1 and print which files are modified.

- **REQ-REL05** `[Event]` When preconditions pass, the script SHALL commit the version
  bump in `pyproject.toml` with message `[release] Bump version to X.Y.Z`.

- **REQ-REL06** `[Event]` When `changelog_source = "openspec"` in config, the script
  SHALL invoke `python scripts/changelog.py`, commit `CHANGELOG.md` with message
  `[release] Update CHANGELOG.md for vX.Y.Z`, before creating the tag.

- **REQ-REL07** `[Event]` When the CHANGELOG commit is done (or skipped if
  `changelog_source != "openspec"`), the script SHALL create an annotated git tag
  `vX.Y.Z` and push it to `origin`.

- **REQ-REL08** `[Event]` After the tag is pushed, the script SHALL invoke
  `gh release create vX.Y.Z` with the release notes for that version from
  `CHANGELOG.md` section `## [X.Y.Z]`.

- **REQ-REL09** `[Event]` When `homebrew_formula` is set in config and the file exists,
  the script SHALL compute the SHA256 of the release tarball, update the formula with
  the new URL and SHA256, commit with message `[release] Update Homebrew formula for
  vX.Y.Z`, and push.

- **REQ-REL10** `[Optional]` Where `homebrew_formula = null` or the formula file does
  not exist, the script SHALL skip the formula update step without error.

- **REQ-REL11** `[Unwanted]` If `gh` is not found in PATH, the script SHALL abort
  before creating the tag and print instructions to install GitHub CLI.

- **REQ-REL12** `[Unwanted]` If the tag already exists locally or remotely, the script
  SHALL abort with exit code 1 before making any changes.

- **REQ-REL13** `[Ubiquitous]` The script SHALL print each step with a status prefix
  (`✓` done, `✗` failed, `→` in progress) so the user can follow progress.

### Script `scripts/changelog.py`

- **REQ-CL01** `[Event]` When invoked, the script SHALL locate `openspec/changes/archive/`
  relative to the git repository root (`git rev-parse --show-toplevel`).

- **REQ-CL02** `[Ubiquitous]` For each archived change, the script SHALL extract:
  - Date from the directory name prefix (`YYYY-MM-DD`)
  - Change name from the directory name suffix
  - Description: first non-empty, non-heading line from `## Descripción` in
    `proposal.md`; falls back to first non-empty, non-heading line in the file

- **REQ-CL03** `[Ubiquitous]` The script SHALL read existing git tags
  (`git tag --sort=-version:refname`) to assign changes to releases by tag date.
  Changes archived on or before the tag date belong to that release.

- **REQ-CL04** `[Ubiquitous]` Changes with no matching tag SHALL be grouped under
  `## [Unreleased]` at the top of `CHANGELOG.md`.

- **REQ-CL05** `[Ubiquitous]` The script SHALL write `CHANGELOG.md` to the git
  repository root, overwriting any existing file completely.

- **REQ-CL06** `[Ubiquitous]` Each release section SHALL be formatted as:
  ```
  ## [X.Y.Z] — YYYY-MM-DD
  - {change-name}: {description}
  ```
  ordered from newest to oldest.

- **REQ-CL07** `[Ubiquitous]` The script SHALL append reference links at the end of
  `CHANGELOG.md` with GitHub compare/release URLs for each version.

- **REQ-CL08** `[Optional]` Where `--version <X.Y.Z>` flag is provided, the script
  SHALL print only the release notes for that version to stdout (for use by `release.sh`).

### Versionado semántico

- **REQ-SEM01** `[Ubiquitous]` Version numbers SHALL follow `MAJOR.MINOR.PATCH`:
  - `PATCH`: bugfixes, UI tweaks, minor improvements
  - `MINOR`: new features (screens, bindings, providers)
  - `MAJOR`: breaking changes in `openspec/` structure or config format incompatibility

- **REQ-SEM02** `[Ubiquitous]` A hotfix SHALL use the same `scripts/release.sh` flow
  with a PATCH bump. No separate hotfix branches (single `main` branch).

### Version markers (`openspec/versions/`)

- **REQ-VM01** `[Ubiquitous]` `openspec/versions/` SHALL be a directory where each
  file `X.Y.Z.yaml` represents a version marker with at minimum a `date: YYYY-MM-DD` field.

- **REQ-VM02** `[Event]` When `scripts/changelog.py --mark-version X.Y.Z` is invoked,
  the script SHALL create `openspec/versions/X.Y.Z.yaml` with `date: <today>` and
  print the path created.

- **REQ-VM03** `[Ubiquitous]` `changelog.py` SHALL use version markers as the primary
  source for version boundaries when `release_workflow.enabled = false` (no git tags
  required).

- **REQ-VM04** `[State]` While `release_workflow.enabled = true`, `changelog.py` SHALL
  use git tags as the primary source and fall back to `openspec/versions/` only if no
  tags exist.

- **REQ-VM05** `[Unwanted]` If both a git tag `vX.Y.Z` and a marker `X.Y.Z.yaml` exist
  for the same version, git tag date SHALL take precedence.

### CHANGELOG.md

- **REQ-CH01** `[Ubiquitous]` `CHANGELOG.md` is a **generated artifact** — manual
  edits SHALL NOT be preserved between regenerations.

- **REQ-CH02** `[Ubiquitous]` `CHANGELOG.md` SHALL be committed in the repository root
  and regenerated from `openspec/changes/archive/` using version markers or git tags
  as boundaries.

- **REQ-CH03** `[State]` While `release_workflow.enabled = false`, the version history
  SHALL be tracked through `openspec/versions/` markers + `openspec/changes/archive/`.
  No git tags, no GitHub Releases — the version record lives entirely in openspec/.

- **REQ-CH04** `[Optional]` Where no version markers and no git tags exist,
  `changelog.py` SHALL group all archived changes under `## [Unreleased]`.

## Escenarios de Verificación

**REQ-OB01 — primera apertura sin config**
**Dado** que `openspec/config.yaml` no tiene `release_workflow:`
**Cuando** el usuario abre sdd-tui
**Entonces** aparece la notificación `"Release workflow not configured — press S to set up"`
**Y** la app funciona normalmente (la notificación no es bloqueante)

**REQ-OB03 — usuario optó por no releases**
**Dado** que `config.yaml` tiene `release_workflow: {enabled: false}`
**Cuando** el usuario abre sdd-tui
**Entonces** NO aparece ninguna notificación sobre releases

**REQ-REL03 — tests fallan, no se crea tag**
**Dado** que `uv run pytest` tiene un test en rojo
**Cuando** se ejecuta `scripts/release.sh 0.2.0`
**Entonces** el script imprime `✗ tests failed` y sale con código 1
**Y** no existe el tag `v0.2.0` ni ningún commit nuevo

**REQ-REL04 — working tree sucio**
**Dado** que `src/sdd_tui/tui/app.py` tiene cambios sin commitear
**Cuando** se ejecuta `scripts/release.sh 0.2.0`
**Entonces** el script imprime `✗ working tree dirty: src/sdd_tui/tui/app.py` y sale con código 1

**REQ-VM02/03 — marcar versión sin GitHub**
**Dado** que `release_workflow.enabled = false` y hay 40 changes archivados
**Cuando** el usuario ejecuta `python scripts/changelog.py --mark-version 0.2.0`
**Entonces** se crea `openspec/versions/0.2.0.yaml` con `date: 2026-03-11`
**Y** al ejecutar `changelog.py` sin flags, `CHANGELOG.md` muestra `## [0.2.0] — 2026-03-11` con los 40 changes

**REQ-CL04/05 — primer release, todos los changes sin tag previo**
**Dado** que no hay ningún tag git y `archive/` tiene 40 changes
**Cuando** se crea el tag `v0.2.0` en fecha 2026-03-11 y se ejecuta `changelog.py`
**Entonces** `CHANGELOG.md` tiene `## [0.2.0] — 2026-03-11` con los 40 changes
**Y** la sección `## [Unreleased]` tiene solo `release-workflow`

## Interfaces / Contratos

### `config.yaml` — sección `release_workflow`

```yaml
release_workflow:
  enabled: true                        # false = proyecto no hace releases
  versioning: semver                   # semver | calver | none
  changelog_source: openspec           # openspec | manual | none
  homebrew_formula: Formula/sdd-tui.rb # ruta relativa al root, o null
```

### `ReleaseWorkflowConfig` dataclass

```python
@dataclass
class ReleaseWorkflowConfig:
    enabled: bool = False
    versioning: str = "semver"          # "semver" | "calver" | "none"
    changelog_source: str = "openspec"  # "openspec" | "manual" | "none"
    homebrew_formula: str | None = None # ruta relativa o None
```

### `scripts/release.sh`

```
scripts/release.sh <version>

Arguments:
  version    Semver string, e.g. "0.2.0"

Exit codes:
  0    Release completed successfully
  1    Precondition failed or step error

Requires: git, uv, gh, curl, python3
```

### `scripts/changelog.py`

```
python scripts/changelog.py [--version X.Y.Z] [--mark-version X.Y.Z]

--version X.Y.Z       Print only release notes for that version to stdout
--mark-version X.Y.Z  Create openspec/versions/X.Y.Z.yaml with today's date

Version boundary resolution (in order):
  1. git tags (if release_workflow.enabled = true and tags exist)
  2. openspec/versions/*.yaml markers
  3. No boundaries → all changes under [Unreleased]

Exit codes:
  0    Success
  1    openspec/ not found, git not available
```

### Flujo completo de `release.sh 0.2.0`

```
validate semver format
check gh available
check no existing tag v0.2.0
uv run pytest                              (abort if fail)
check git status --porcelain clean         (abort if dirty, excl. openspec/ .claude/)
bump pyproject.toml → version = "0.2.0"
commit "[release] Bump version to 0.2.0"
python scripts/changelog.py               (si changelog_source = openspec)
commit "[release] Update CHANGELOG.md for v0.2.0"
git tag -a v0.2.0 -m "v0.2.0"
git push origin main --tags
python scripts/changelog.py --version 0.2.0  → release notes
gh release create v0.2.0 --notes "<notes>"
curl tarball → sha256sum                  (si homebrew_formula configurado)
update Formula/sdd-tui.rb (url + sha256)
commit "[release] Update Homebrew formula for v0.2.0"
git push origin main
✓ Release v0.2.0 complete
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Release workflow optativo via config.yaml | Siempre activo | Distintos proyectos tienen distintas necesidades; no todos publican releases formales |
| Sin releases → historial en openspec/ | Sin historial | openspec/archive ya es el registro canónico de versiones; no se pierde trazabilidad |
| `openspec/versions/X.Y.Z.yaml` como marcador | Campo en config.yaml o milestones | Un fichero por versión es independiente, versionable y fácil de listar; no mezcla conceptos con milestones |
| git tags tienen precedencia sobre markers | Markers siempre | Evita inconsistencias cuando el proyecto migra de no-releases a releases formales |
| Notificación en startup si no configurado | Wizard bloqueante al inicio | No interrumpe el flujo principal; el usuario decide cuándo configurar |
| Auto-bump pyproject.toml en el script | Pre-bump manual | Menos pasos, menos error-prone |
| CHANGELOG regenerado completo | Append sección nueva | Siempre consistente con openspec/; sin drift por ediciones manuales |
| changelog.py desde git root | Desde cwd | Funciona desde cualquier subdirectorio |
| Changelog desde openspec/archive | Desde git log | openspec contiene el "por qué" de cada change, no solo el "qué" de cada commit |
| Tag después de commit CHANGELOG | Tag antes | El CHANGELOG del tag debe incluir el propio release |
| Nuevos pasos en GitWorkflowSetupScreen | Wizard separado | Mantiene un único punto de configuración del proyecto |

## Abierto / Pendiente

_(ninguno)_
