# Distribution Reference

The distribution domain covers how sdd-tui reaches end users: a Homebrew formula for macOS/Linux, `pipx`/`pip` via PyPI, and the `sdd-setup` CLI that installs SDD skills into `~/.claude/skills/` (globally or per-project). It also defines the release workflow: `scripts/changelog.py` generates `CHANGELOG.md` from `openspec/changes/archive/`, version markers live in `openspec/versions/`, and `scripts/release.sh` orchestrates tagging and publishing.

## Requirements

| ID | Type | Description |
|----|------|-------------|
| `REQ-SETUP01` | Event | When `sdd-setup` is invoked without flags, the CLI SHALL present an interactive menu asking the user to choose between global (`~/.claude/skills/`) and project-local (`.claude/skills/`) installation destination. |
| `REQ-SETUP02` | Event | When `--global` or `--local` flag is provided, the CLI SHALL skip the interactive menu and use the specified destination. |
| `REQ-SETUP03` | Event | When a skill directory already exists at the destination, the CLI SHALL list the existing skills and ask the user to choose: update all, skip all, or decide per skill. |
| `REQ-SETUP04` | Event | When the user chooses "update", the CLI SHALL overwrite the existing skill directory with the bundled version. |
| `REQ-SETUP05` | Event | When the user chooses "skip", the CLI SHALL leave the existing skill unchanged and report it as skipped. |
| `REQ-SETUP06` | Ubiquitous | The CLI SHALL download skills from the GitHub repository (`github.com/jorgeferrando/sdd-tui`) at install time, ensuring the latest version is always installed regardless of which TUI package version is installed. |
| `REQ-SETUP07` | Event | When `claude` is not found in PATH after installation completes, the CLI SHALL display an informational message with the Claude Code install URL but SHALL NOT fail or return a non-zero exit code. |
| `REQ-SETUP08` | Event | When installation completes successfully, the CLI SHALL print a summary: skills installed/updated/skipped, destination, and next step message ("Restart Claude Code and run /sdd-init in your project"). |
| `REQ-SETUP09` | Ubiquitous | The CLI SHALL accept `--help` and display all available flags with a one-line description each. |
| `REQ-SETUP10` | Unwanted | If the destination directory cannot be created (permissions), the CLI SHALL exit with a non-zero code and a clear error message. |
| `REQ-SETUP11` | Optional | Where `--check` flag is provided, the CLI SHALL report: the installed package version, the skills source URL (GitHub), which skills are installed, and their location — without making any changes. ### Skills Source |
| `REQ-PKG01` | Ubiquitous | Skills SHALL NOT be bundled in the wheel. They SHALL always be fetched from the GitHub repository at install time. |
| `REQ-PKG02` | Ubiquitous | `pyproject.toml` SHALL declare `sdd-setup` as a second entry point script alongside `sdd-tui`. |
| `REQ-PKG03` | Ubiquitous | `sdd-setup` SHALL reuse the same download mechanism as `scripts/install-skills.sh` (shallow clone via `git clone --depth=1` or GitHub archive tarball) to fetch the latest skills from `main`. ### Homebrew Formula |
| `REQ-BREW01` | Event | When `brew install sdd-tui` is run (after tap), the formula SHALL install the TUI using the Python bundled by Homebrew. |
| `REQ-BREW02` | Ubiquitous | The formula SHALL use `pip install` with the PyPI-compatible wheel or the GitHub archive URL as source. |
| `REQ-BREW03` | Ubiquitous | `Formula/sdd-tui.rb` SHALL live in the repository root so the tap works as `brew tap jorgeferrando/sdd-tui`. |
| `REQ-BREW04` | Ubiquitous | The formula's `test` block SHALL verify that `sdd-tui --help` and `sdd-setup --help` exit with code 0. ### Linux Installer |
| `REQ-LINUX01` | Event | When `scripts/install.sh` is run, it SHALL detect the available Python runtime (python3) and package manager (uv, pipx, pip — in that order of preference) and use the first available to install the TUI. |
| `REQ-LINUX02` | Event | When no supported Python package manager is found, the script SHALL print installation instructions for uv and exit with code 1. |
| `REQ-LINUX03` | Event | After TUI install, `install.sh` SHALL invoke `sdd-setup --global` automatically unless `--skip-skills` flag is provided. |
| `REQ-LINUX04` | Ubiquitous | `install.sh` SHALL work on bash 4.x+ and SHALL NOT require root/sudo for the default installation. ### Windows Installer |
| `REQ-WIN01` | Event | When `scripts/Install-SddTui.ps1` is run, it SHALL detect uv, pipx, or pip (in that order) and install the TUI using the first available. |
| `REQ-WIN02` | Event | When no Python package manager is found, the script SHALL print installation instructions and exit with a non-zero exit code. |
| `REQ-WIN03` | Event | After TUI install, the script SHALL invoke `sdd-setup --global` automatically unless `-SkipSkills` parameter is provided. |
| `REQ-WIN04` | Ubiquitous | The script SHALL target PowerShell 5.1+ (compatible with Windows 10 built-in PowerShell). ### README |
| `REQ-DOC01` | Ubiquitous | The Install section SHALL be organized by platform: macOS (Homebrew + uv/pipx), Linux (install.sh + uv/pipx), Windows (PS1 + manual). |
| `REQ-DOC02` | Ubiquitous | Each platform section SHALL show the minimal 2-step experience: install TUI → run `sdd-setup`. |
| `REQ-DOC03` | Ubiquitous | The skills install section SHALL reference `sdd-setup` as the primary method, with `install-skills.sh` documented as the legacy/manual alternative. ## Escenarios de Verificación **REQ-SETUP03 — skills ya instalados, usuario elige skip** **Dado** que `~/.claude/skills/sdd-init` existe **Cuando** el usuario ejecuta `sdd-setup --global` **Entonces** el CLI lista "sdd-init (already installed)" y pregunta: [update / skip / decide per skill] **Y** si el usuario elige skip, el skill no se modifica y el summary muestra "sdd-init: skipped" **REQ-SETUP07 — Claude Code no instalado** **Dado** que `claude` no está en PATH **Cuando** el CLI completa la instalación de skills **Entonces** imprime: "Note: Claude Code not found in PATH. Install it at claude.ai/code" **Y** el exit code es 0 **REQ-PKG01/03 — skills desde GitHub** **Dado** que el usuario instaló sdd-tui via `uv tool install sdd-tui` **Cuando** ejecuta `sdd-setup` **Entonces** el CLI hace un shallow clone de `github.com/jorgeferrando/sdd-tui` a un directorio temporal, copia los skills al destino, y limpia el temporal ## Interfaces / Contratos ### `sdd-setup` flags \| Flag \| Tipo \| Descripción \| \|------\|------\|-------------\| \| `--global` \| bool \| Instalar en `~/.claude/skills/` sin preguntar \| \| `--local` \| bool \| Instalar en `.claude/skills/` sin preguntar \| \| `--check` \| bool \| Solo reportar estado, sin modificar \| \| `--skip-skills` / `-SkipSkills` \| bool \| Para install.sh / PS1: no invocar sdd-setup \| \| `--help` \| bool \| Mostrar ayuda \| ### Exit codes \| Código \| Significado \| \|--------\|-------------\| \| 0 \| Éxito (incluyendo "claude not found" — solo aviso) \| \| 1 \| Error de permisos, package manager no encontrado, o error inesperado \| --- ## Release Workflow (v2.0 — release-workflow) ### Configuración en `config.yaml` |
| `REQ-CFG01` | Ubiquitous | `openspec/config.yaml` SHALL support a `release_workflow:` section with fields: `enabled`, `versioning`, `changelog_source`, `homebrew_formula`. |
| `REQ-CFG02` | Ubiquitous | Default values when absent: `enabled=false`, `versioning="semver"`, `changelog_source="openspec"`, `homebrew_formula=null`. |
| `REQ-CFG03` | Ubiquitous | `ReleaseWorkflowConfig` SHALL be a dataclass loaded by `load_release_config` from `config.yaml`. ### Setup Wizard |
| `REQ-WZ06` | Event | When the user reaches the release step in `GitWorkflowSetupScreen`, the system SHALL ask: "Does this project publish releases?" (yes / no). |
| `REQ-WZ07` | Event | When `yes`, the wizard SHALL ask versioning scheme: semver / calver / none. |
| `REQ-WZ08` | Event | When `yes`, the wizard SHALL ask for Homebrew formula path. |
| `REQ-WZ09` | Event | When the wizard completes, the system SHALL write `release_workflow:` to `openspec/config.yaml`. ### Startup check |
| `REQ-OB01` | Event | When the app mounts and `release_workflow:` is absent, the system SHALL display: `"Release workflow not configured — press S to set up"`. |
| `REQ-OB03` | Unwanted | If `release_workflow.enabled = false`, the system SHALL NOT show the notification. ### Version markers (`openspec/versions/`) |
| `REQ-VM01` | Ubiquitous | `openspec/versions/X.Y.Z.yaml` represents a version marker with `date: YYYY-MM-DD`. |
| `REQ-VM02` | Event | When `scripts/changelog.py --mark-version X.Y.Z` is invoked, the script SHALL create `openspec/versions/X.Y.Z.yaml` with today's date. |
| `REQ-VM03` | Ubiquitous | `changelog.py` SHALL use version markers as primary source when `release_workflow.enabled = false`. |
| `REQ-VM04` | State | While `release_workflow.enabled = true`, git tags take precedence; markers are fallback. ### Scripts |

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
