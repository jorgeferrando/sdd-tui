# Design: Distribución de SDD skills

## Metadata
- **Change:** docs-skills-install
- **Fecha:** 2026-03-03
- **Estado:** approved

## Resumen Técnico

Se añaden versiones genéricas de las 12 skills SDD al repo en `skills/sdd-*/SKILL.md`.
Un script `scripts/install-skills.sh` copia el directorio `skills/` al destino
elegido por el usuario (`~/.claude/skills/` o `.claude/skills/`).
El script soporta modo interactivo y flags `--global`/`--local` para uso con `curl | bash`.

## Estructura de archivos

```
skills/
├── sdd-init/SKILL.md
├── sdd-new/SKILL.md
├── sdd-explore/SKILL.md
├── sdd-propose/SKILL.md
├── sdd-spec/SKILL.md
├── sdd-design/SKILL.md
├── sdd-tasks/SKILL.md
├── sdd-apply/SKILL.md
├── sdd-verify/SKILL.md
├── sdd-archive/SKILL.md
├── sdd-continue/SKILL.md
└── sdd-ff/SKILL.md

scripts/
└── install-skills.sh
```

## Archivos a Crear/Modificar

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `skills/sdd-init/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-new/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-explore/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-propose/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-spec/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-design/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-tasks/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-apply/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-verify/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-archive/SKILL.md` | nuevo | Versión genérica |
| `skills/sdd-continue/SKILL.md` | nuevo | Ya genérica (mínima limpieza) |
| `skills/sdd-ff/SKILL.md` | nuevo | Ya genérica (mínima limpieza) |
| `scripts/install-skills.sh` | nuevo | Script de instalación |
| `README.md` | modificar | Añadir sección de skills |

## Scope

- **Total archivos:** 14
- **Resultado:** Evaluar (pero mayoría son copias adaptadas, no código nuevo)

## `scripts/install-skills.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../skills" && pwd)"

# Determine destination
if [[ "${1:-}" == "--global" ]]; then
    DEST="$HOME/.claude/skills"
elif [[ "${1:-}" == "--local" ]]; then
    DEST="$(pwd)/.claude/skills"
else
    echo "Install SDD skills for Claude Code"
    echo ""
    echo "  [1] Global (~/.claude/skills/) — available in all projects"
    echo "  [2] Project-local (.claude/skills/) — current project only"
    echo ""
    read -rp "Choice [1/2]: " choice
    case "$choice" in
        1) DEST="$HOME/.claude/skills" ;;
        2) DEST="$(pwd)/.claude/skills" ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

mkdir -p "$DEST"
installed=0
skipped=0

for skill_dir in "$SKILLS_DIR"/sdd-*/; do
    skill_name="$(basename "$skill_dir")"
    target="$DEST/$skill_name"
    if [[ -d "$target" ]]; then
        echo "  skip  $skill_name (already exists — delete to reinstall)"
        ((skipped++))
    else
        cp -r "$skill_dir" "$target"
        echo "  ✓     $skill_name"
        ((installed++))
    fi
done

echo ""
echo "Installed: $installed  Skipped: $skipped"
echo "Destination: $DEST"
```

## Qué se limpia en las skills genéricas

| Eliminado | Sustituido por |
|-----------|---------------|
| `parclick-system cargado` | — (eliminado) |
| Tablas de proyectos next/admin/front | Instrucción genérica |
| `~/.claude/scripts/next-*.sh` | "Run your project's test command" |
| Docker checks | — (eliminado) |
| `DI-XXX` como formato obligatorio | ID de ticket opcional |
| Arquitectura PHP/Angular/NestJS | Descripción genérica de capas |

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `cp -r` sin overwrite | Actualizar siempre | Evita borrar customizaciones del usuario |
| `--global`/`--local` flags | Solo interactivo | Permite uso con `curl \| bash` sin TTY |
| Skills en `skills/` (no en `.claude/skills/`) | `.claude/skills/` directamente | Separar fuente de distribución del destino de instalación |
| 12 skills en commits separados | Un commit para todas | Atomicidad — cada skill es un artefacto independiente |
