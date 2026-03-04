# sdd-tui

TUI para gestionar el flujo [SDD (Spec-Driven Development)](https://github.com/jorgeferrando/sdd-tui)
desde la terminal. Visualiza el estado del pipeline de cada change y permite
navegar entre vistas, diffs y documentación sin salir del editor.

## Install

```bash
# Con uv (recomendado — entorno aislado)
uv tool install git+https://github.com/jorgeferrando/sdd-tui

# Con pipx
pipx install git+https://github.com/jorgeferrando/sdd-tui

# Con pip
pip install git+https://github.com/jorgeferrando/sdd-tui
```

## Skills (Claude Code)

sdd-tui works together with a set of Claude Code skills (`/sdd-init`, `/sdd-apply`, etc.) that drive the SDD workflow. Install them before using the tool.

### From the repository (recommended)

```bash
# Clone and run the installer
git clone https://github.com/jorgeferrando/sdd-tui
cd sdd-tui
./scripts/install-skills.sh
```

The installer will ask:
- **Global** (`~/.claude/skills/`) — available in all your projects
- **Project-local** (`.claude/skills/`) — only in the current project

### Without cloning

```bash
# Global install
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install-skills.sh | bash -s -- --global

# Project-local install
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install-skills.sh | bash -s -- --local
```

After installing, restart Claude Code. The `/sdd-*` skills will be available.

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

### View 1 — Lista de changes

| Tecla | Acción |
|-------|--------|
| `Enter` | Abrir detalle del change |
| `a` | Mostrar/ocultar archivados |
| `r` | Refrescar |
| `q` | Salir |

### View 2 — Detalle del change

| Tecla | Acción |
|-------|--------|
| `Space` | Copiar comando SDD al portapapeles |
| `p` | Ver proposal |
| `d` | Ver design |
| `s` | Ver spec(s) |
| `t` | Ver tasks |
| `r` | Refrescar en sitio |
| `Esc` | Volver |

## Stack

- [Textual](https://textual.textualize.io/) — TUI framework
- [uv](https://docs.astral.sh/uv/) — gestión de entornos y dependencias
- Git (subprocess)
