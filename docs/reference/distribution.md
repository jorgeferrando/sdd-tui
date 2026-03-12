# Distribution Reference

The distribution domain covers how sdd-tui reaches users across platforms. On macOS the primary path is a Homebrew formula (`Formula/sdd-tui.rb`) that installs the Python package and exposes the `sdd-tui`, `sdd-docs`, and `sdd-setup` binaries. On Linux, `scripts/install.sh` auto-detects `uv`, `pipx`, or `pip` and installs the wheel. On Windows, `scripts/Install-SddTui.ps1` handles the equivalent flow. After the TUI is installed, `sdd-setup` (run by all installers) downloads the Claude Code skills from the GitHub repository and places them in `~/.claude/skills/` (global) or `.claude/skills/` (local), ready to be invoked as `/sdd-*` inside Claude Code.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-SETUP01` | Event | When `sdd-setup` is invoked without flags, the CLI SHALL present |
| `REQ-SETUP02` | Event | When `--global` or `--local` flag is provided, the CLI SHALL |
| `REQ-SETUP03` | Event | When a skill directory already exists at the destination, |
| `REQ-SETUP04` | Event | When the user chooses "update", the CLI SHALL overwrite the |
| `REQ-SETUP05` | Event | When the user chooses "skip", the CLI SHALL leave the existing |
| `REQ-SETUP06` | Ubiquitous | The CLI SHALL download skills from the GitHub repository |
| `REQ-SETUP07` | Event | When `claude` is not found in PATH after installation completes, |
| `REQ-SETUP08` | Event | When installation completes successfully, the CLI SHALL print |
| `REQ-SETUP09` | Ubiquitous | The CLI SHALL accept `--help` and display all available |
| `REQ-SETUP10` | Unwanted | If the destination directory cannot be created (permissions), |
| `REQ-SETUP11` | Optional | Where `--check` flag is provided, the CLI SHALL report: |
| `REQ-PKG01` | Ubiquitous | Skills SHALL NOT be bundled in the wheel. They SHALL always |
| `REQ-PKG02` | Ubiquitous | `pyproject.toml` SHALL declare `sdd-setup` as a second |
| `REQ-PKG03` | Ubiquitous | `sdd-setup` SHALL reuse the same download mechanism as |
| `REQ-BREW01` | Event | When `brew install sdd-tui` is run (after tap), the formula |
| `REQ-BREW02` | Ubiquitous | The formula SHALL use `pip install` with the PyPI-compatible |
| `REQ-BREW03` | Ubiquitous | `Formula/sdd-tui.rb` SHALL live in the repository root |
| `REQ-BREW04` | Ubiquitous | The formula's `test` block SHALL verify that `sdd-tui --help` |
| `REQ-LINUX01` | Event | When `scripts/install.sh` is run, it SHALL detect the available |
| `REQ-LINUX02` | Event | When no supported Python package manager is found, the script |
| `REQ-LINUX03` | Event | After TUI install, `install.sh` SHALL invoke `sdd-setup --global` |
| `REQ-LINUX04` | Ubiquitous | `install.sh` SHALL work on bash 4.x+ and SHALL NOT require |
| `REQ-WIN01` | Event | When `scripts/Install-SddTui.ps1` is run, it SHALL detect uv, |
| `REQ-WIN02` | Event | When no Python package manager is found, the script SHALL print |
| `REQ-WIN03` | Event | After TUI install, the script SHALL invoke `sdd-setup --global` |
| `REQ-WIN04` | Ubiquitous | The script SHALL target PowerShell 5.1+ (compatible with |
| `REQ-DOC01` | Ubiquitous | The Install section SHALL be organized by platform: |
| `REQ-DOC02` | Ubiquitous | Each platform section SHALL show the minimal 2-step experience: |
| `REQ-DOC03` | Ubiquitous | The skills install section SHALL reference `sdd-setup` as |
| `REQ-CFG01` | Ubiquitous | `openspec/config.yaml` SHALL support a `release_workflow:` section with fields: `enabled`, `versioning`, `changelog_source`, `homebrew_formula`. |
| `REQ-CFG02` | Ubiquitous | Default values when absent: `enabled=false`, `versioning="semver"`, `changelog_source="openspec"`, `homebrew_formula=null`. |
| `REQ-CFG03` | Ubiquitous | `ReleaseWorkflowConfig` SHALL be a dataclass loaded by `load_release_config` from `config.yaml`. |
| `REQ-WZ06` | Event | When the user reaches the release step in `GitWorkflowSetupScreen`, the system SHALL ask: "Does this project publish releases?" (yes / no). |
| `REQ-WZ07` | Event | When `yes`, the wizard SHALL ask versioning scheme: semver / calver / none. |
| `REQ-WZ08` | Event | When `yes`, the wizard SHALL ask for Homebrew formula path. |
| `REQ-WZ09` | Event | When the wizard completes, the system SHALL write `release_workflow:` to `openspec/config.yaml`. |
| `REQ-OB01` | Event | When the app mounts and `release_workflow:` is absent, the system SHALL display: `"Release workflow not configured — press S to set up"`. |
| `REQ-OB03` | Unwanted | If `release_workflow.enabled = false`, the system SHALL NOT show the notification. |
| `REQ-VM01` | Ubiquitous | `openspec/versions/X.Y.Z.yaml` represents a version marker with `date: YYYY-MM-DD`. |
| `REQ-VM02` | Event | When `scripts/changelog.py --mark-version X.Y.Z` is invoked, the script SHALL create `openspec/versions/X.Y.Z.yaml` with today's date. |
| `REQ-VM03` | Ubiquitous | `changelog.py` SHALL use version markers as primary source when `release_workflow.enabled = false`. |
| `REQ-VM04` | State | While `release_workflow.enabled = true`, git tags take precedence; markers are fallback. |

## Decisions

| Decision | Discarded Alternative | Reason |
|----------|----------------------|--------|
| Skills descargados de GitHub en el momento | Bundlear en el wheel | Skills y TUI evolucionan a ritmos distintos |
| Skills existentes → preguntar (update/skip/per-skill) | Saltar silenciosamente | El usuario puede tener customizaciones |
| Claude Code → solo avisar, no bloquear | Bloquear si no está | El usuario puede instalar Claude Code después |
| Formula en el mismo repo (`Formula/sdd-tui.rb`) | Repo separado `homebrew-sdd-tui` | Menos overhead; tap funciona igual |
| PyPI fuera de scope | Publicar ahora | Requiere cuenta + tokens + CI/CD |
| Release workflow optativo via config.yaml | Siempre activo | No todos los proyectos publican releases formales |
| Sin releases → historial en openspec/ | Sin historial | openspec/archive ya es el registro canónico |
| `openspec/versions/X.Y.Z.yaml` como marcador | Campo en config.yaml o milestones | Un fichero por versión, no mezcla conceptos |
| Auto-bump pyproject.toml en release.sh | Pre-bump manual | Menos pasos, menos error-prone |
| CHANGELOG regenerado completo | Append sección nueva | Siempre consistente con openspec/ |
| Changelog desde openspec/archive | Desde git log | openspec contiene el "por qué", no solo el "qué" |
