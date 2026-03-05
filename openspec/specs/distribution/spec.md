# Spec: Distribution — Setup Experience

## Metadata
- **Dominio:** distribution
- **Change:** sdd-setup-experience (initial)
- **Fecha:** 2026-03-05
- **Versión:** 1.0
- **Estado:** canonical

## Contexto

sdd-tui es una herramienta para desarrolladores que trabajan con el flujo SDD (Spec-Driven Development).
La instalación actual requiere 4 pasos manuales separados (TUI + skills + reinicio + /sdd-init),
sin soporte para gestores de paquetes nativos (Homebrew, apt). Este dominio cubre la experiencia
de instalación end-to-end: canales de distribución, CLI de setup unificado, y bundling de skills.

## Comportamiento Actual

- TUI instalable via `uv tool install git+https://...` / pipx / pip
- Skills instalables por separado via `install-skills.sh` (desde repo clonado o curl)
- Sin Homebrew formula ni instaladores para Linux/Windows
- Los skills no están incluidos en el paquete Python — requieren repo o conexión a GitHub

## Requisitos (EARS)

### CLI `sdd-setup`

- **REQ-SETUP01** `[Event]` When `sdd-setup` is invoked without flags, the CLI SHALL present
  an interactive menu asking the user to choose between global (`~/.claude/skills/`) and
  project-local (`.claude/skills/`) installation destination.

- **REQ-SETUP02** `[Event]` When `--global` or `--local` flag is provided, the CLI SHALL
  skip the interactive menu and use the specified destination.

- **REQ-SETUP03** `[Event]` When a skill directory already exists at the destination,
  the CLI SHALL list the existing skills and ask the user to choose: update all, skip all,
  or decide per skill.

- **REQ-SETUP04** `[Event]` When the user chooses "update", the CLI SHALL overwrite the
  existing skill directory with the bundled version.

- **REQ-SETUP05** `[Event]` When the user chooses "skip", the CLI SHALL leave the existing
  skill unchanged and report it as skipped.

- **REQ-SETUP06** `[Ubiquitous]` The CLI SHALL download skills from the GitHub repository
  (`github.com/jorgeferrando/sdd-tui`) at install time, ensuring the latest version is
  always installed regardless of which TUI package version is installed.

- **REQ-SETUP07** `[Event]` When `claude` is not found in PATH after installation completes,
  the CLI SHALL display an informational message with the Claude Code install URL but SHALL
  NOT fail or return a non-zero exit code.

- **REQ-SETUP08** `[Event]` When installation completes successfully, the CLI SHALL print
  a summary: skills installed/updated/skipped, destination, and next step message
  ("Restart Claude Code and run /sdd-init in your project").

- **REQ-SETUP09** `[Ubiquitous]` The CLI SHALL accept `--help` and display all available
  flags with a one-line description each.

- **REQ-SETUP10** `[Unwanted]` If the destination directory cannot be created (permissions),
  the CLI SHALL exit with a non-zero code and a clear error message.

- **REQ-SETUP11** `[Optional]` Where `--check` flag is provided, the CLI SHALL report:
  the installed package version, the skills source URL (GitHub), which skills are installed,
  and their location — without making any changes.

### Skills Source

- **REQ-PKG01** `[Ubiquitous]` Skills SHALL NOT be bundled in the wheel. They SHALL always
  be fetched from the GitHub repository at install time.

- **REQ-PKG02** `[Ubiquitous]` `pyproject.toml` SHALL declare `sdd-setup` as a second
  entry point script alongside `sdd-tui`.

- **REQ-PKG03** `[Ubiquitous]` `sdd-setup` SHALL reuse the same download mechanism as
  `scripts/install-skills.sh` (shallow clone via `git clone --depth=1` or GitHub archive
  tarball) to fetch the latest skills from `main`.

### Homebrew Formula

- **REQ-BREW01** `[Event]` When `brew install sdd-tui` is run (after tap), the formula
  SHALL install the TUI using the Python bundled by Homebrew.

- **REQ-BREW02** `[Ubiquitous]` The formula SHALL use `pip install` with the PyPI-compatible
  wheel or the GitHub archive URL as source.

- **REQ-BREW03** `[Ubiquitous]` `Formula/sdd-tui.rb` SHALL live in the repository root
  so the tap works as `brew tap jorgeferrando/sdd-tui`.

- **REQ-BREW04** `[Ubiquitous]` The formula's `test` block SHALL verify that `sdd-tui --help`
  and `sdd-setup --help` exit with code 0.

### Linux Installer

- **REQ-LINUX01** `[Event]` When `scripts/install.sh` is run, it SHALL detect the available
  Python runtime (python3) and package manager (uv, pipx, pip — in that order of preference)
  and use the first available to install the TUI.

- **REQ-LINUX02** `[Event]` When no supported Python package manager is found, the script
  SHALL print installation instructions for uv and exit with code 1.

- **REQ-LINUX03** `[Event]` After TUI install, `install.sh` SHALL invoke `sdd-setup --global`
  automatically unless `--skip-skills` flag is provided.

- **REQ-LINUX04** `[Ubiquitous]` `install.sh` SHALL work on bash 4.x+ and SHALL NOT require
  root/sudo for the default installation.

### Windows Installer

- **REQ-WIN01** `[Event]` When `scripts/Install-SddTui.ps1` is run, it SHALL detect uv,
  pipx, or pip (in that order) and install the TUI using the first available.

- **REQ-WIN02** `[Event]` When no Python package manager is found, the script SHALL print
  installation instructions and exit with a non-zero exit code.

- **REQ-WIN03** `[Event]` After TUI install, the script SHALL invoke `sdd-setup --global`
  automatically unless `-SkipSkills` parameter is provided.

- **REQ-WIN04** `[Ubiquitous]` The script SHALL target PowerShell 5.1+ (compatible with
  Windows 10 built-in PowerShell).

### README

- **REQ-DOC01** `[Ubiquitous]` The Install section SHALL be organized by platform:
  macOS (Homebrew + uv/pipx), Linux (install.sh + uv/pipx), Windows (PS1 + manual).

- **REQ-DOC02** `[Ubiquitous]` Each platform section SHALL show the minimal 2-step experience:
  install TUI → run `sdd-setup`.

- **REQ-DOC03** `[Ubiquitous]` The skills install section SHALL reference `sdd-setup` as
  the primary method, with `install-skills.sh` documented as the legacy/manual alternative.

## Escenarios de Verificación

**REQ-SETUP03 — skills ya instalados, usuario elige skip**
**Dado** que `~/.claude/skills/sdd-init` existe
**Cuando** el usuario ejecuta `sdd-setup --global`
**Entonces** el CLI lista "sdd-init (already installed)" y pregunta: [update / skip / decide per skill]
**Y** si el usuario elige skip, el skill no se modifica y el summary muestra "sdd-init: skipped"

**REQ-SETUP07 — Claude Code no instalado**
**Dado** que `claude` no está en PATH
**Cuando** el CLI completa la instalación de skills
**Entonces** imprime: "Note: Claude Code not found in PATH. Install it at claude.ai/code"
**Y** el exit code es 0

**REQ-PKG01/03 — skills desde GitHub**
**Dado** que el usuario instaló sdd-tui via `uv tool install sdd-tui`
**Cuando** ejecuta `sdd-setup`
**Entonces** el CLI hace un shallow clone de `github.com/jorgeferrando/sdd-tui` a un directorio temporal,
copia los skills al destino, y limpia el temporal

## Interfaces / Contratos

### `sdd-setup` flags

| Flag | Tipo | Descripción |
|------|------|-------------|
| `--global` | bool | Instalar en `~/.claude/skills/` sin preguntar |
| `--local` | bool | Instalar en `.claude/skills/` sin preguntar |
| `--check` | bool | Solo reportar estado, sin modificar |
| `--skip-skills` / `-SkipSkills` | bool | Para install.sh / PS1: no invocar sdd-setup |
| `--help` | bool | Mostrar ayuda |

### Exit codes

| Código | Significado |
|--------|-------------|
| 0 | Éxito (incluyendo "claude not found" — solo aviso) |
| 1 | Error de permisos, package manager no encontrado, o error inesperado |

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Skills descargados de GitHub en el momento | Bundlear en el wheel | Skills y TUI evolucionan a ritmos distintos; actualizar skills no requiere reinstalar el paquete |
| Skills existentes → preguntar (update/skip/per-skill) | Saltar silenciosamente | El usuario puede tener customizaciones; sobreescribir silenciosamente sería destructivo |
| Claude Code → solo avisar, no bloquear | Bloquear si no está | El usuario puede instalar Claude Code después; el setup de skills es independiente |
| Formula en el mismo repo (`Formula/sdd-tui.rb`) | Repo separado `homebrew-sdd-tui` | Menos overhead; tap funciona igual (`brew tap jorgeferrando/sdd-tui`) |
| PyPI fuera de scope | Publicar ahora | Requiere cuenta + tokens + CI/CD; no resuelve skills; candidate para change futuro |

## Abierto / Pendiente

_(ninguno — todos los puntos resueltos)_
