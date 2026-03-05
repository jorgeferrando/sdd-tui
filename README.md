# sdd-tui

TUI para gestionar el flujo [SDD (Spec-Driven Development)](https://github.com/jorgeferrando/sdd-tui)
desde la terminal. Visualiza el estado del pipeline de cada change y permite
navegar entre vistas, diffs y documentación sin salir del editor.

## Install

### macOS

```bash
# With Homebrew (recommended)
brew tap jorgeferrando/sdd-tui
brew install sdd-tui
sdd-setup          # installs SDD skills for Claude Code

# With uv
uv tool install git+https://github.com/jorgeferrando/sdd-tui
sdd-setup
```

### Linux

```bash
# One-liner (detects uv / pipx / pip automatically)
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install.sh | bash

# Or manually with uv
uv tool install git+https://github.com/jorgeferrando/sdd-tui
sdd-setup
```

### Windows (PowerShell 5.1+)

```powershell
# Download and run the installer
irm https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/Install-SddTui.ps1 | iex

# Or manually with uv
uv tool install git+https://github.com/jorgeferrando/sdd-tui
sdd-setup
```

### What `sdd-setup` does

`sdd-setup` downloads the latest SDD skills from GitHub and installs them into
Claude Code's skills directory. Skills are independent of the TUI version — you can
update them at any time by running `sdd-setup` again.

```bash
sdd-setup --global    # install into ~/.claude/skills/ (all projects)
sdd-setup --local     # install into .claude/skills/ (current project)
sdd-setup --check     # show installed version and skills state
```

After installing, restart Claude Code. The `/sdd-*` skills will be available.

### Manual skills install (legacy)

```bash
# Clone and run the installer
git clone https://github.com/jorgeferrando/sdd-tui
cd sdd-tui
./scripts/install-skills.sh
```

---

## Prerequisito

Necesita un directorio `openspec/` con la estructura SDD:

```
openspec/
├── changes/
│   └── my-change/
│       ├── proposal.md
│       ├── tasks.md
│       └── specs/
└── specs/
```

Inicializar con `/sdd-init` en [Claude Code](https://claude.ai/code).

## Usage

```bash
# Desde el directorio que contiene openspec/
sdd-tui

# Con ruta explícita
sdd-tui /ruta/al/openspec
```

## Keybindings

> Pulsa `?` en cualquier pantalla para abrir la referencia completa de keybindings.

### View 1 — Lista de changes

| Tecla | Acción |
|-------|--------|
| `Enter` | Abrir detalle del change |
| `a` | Mostrar/ocultar archivados |
| `r` | Refrescar |
| `s` | Abrir steering.md |
| `H` | Spec health dashboard |
| `X` | Decisions timeline |
| `q` | Salir |

### View 2 — Detalle del change

| Tecla | Acción |
|-------|--------|
| `p` | Ver proposal.md |
| `d` | Ver design.md |
| `s` | Ver spec(s) |
| `t` | Ver tasks.md |
| `q` | Ver requirements.md |
| `Space` | Copiar comando SDD al portapapeles |
| `E` | Spec evolution viewer |
| `r` | Refrescar en sitio |
| `Esc` | Volver a changes |

### View 8 — Spec Health

| Tecla | Acción |
|-------|--------|
| `Enter` | Abrir detalle del change |
| `Esc` | Volver a changes |

### View 9 — Spec Evolution / Decisions Timeline

| Tecla | Acción |
|-------|--------|
| `D` | Alternar vista delta / canónica |
| `j` / `k` | Scroll hacia abajo / arriba |
| `Esc` | Volver |

### Viewers (documentos, specs)

| Tecla | Acción |
|-------|--------|
| `j` / `k` | Scroll hacia abajo / arriba |
| `q` / `Esc` | Cerrar |

### Global

| Tecla | Acción |
|-------|--------|
| `?` | Pantalla de ayuda |

## Stack

- [Textual](https://textual.textualize.io/) — TUI framework
- [uv](https://docs.astral.sh/uv/) — gestión de entornos y dependencias
- Git (subprocess)
