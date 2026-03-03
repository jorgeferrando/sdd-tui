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
