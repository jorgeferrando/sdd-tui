# Proposal: Distribución de SDD skills para Claude Code

## Metadata
- **Change:** docs-skills-install
- **Jira:** N/A
- **Fecha:** 2026-03-03

## Problema

Las skills SDD (`/sdd-init`, `/sdd-apply`, etc.) son necesarias para usar sdd-tui
pero están solo en la máquina del autor. Tienen además referencias a proyectos
Parclick (PHP, Docker, scripts internos) que no son relevantes para otros usuarios.
Un nuevo usuario que instale sdd-tui no tiene forma de obtener las skills.

## Solución Propuesta

1. Incluir versiones **genéricas** de las 12 skills SDD en el repo bajo `skills/sdd-*/SKILL.md`
2. Script `scripts/install-skills.sh` con elección: global (`~/.claude/skills/`) o project-local (`.claude/skills/`)
3. Actualizar `README.md` con la sección de instalación de skills

Las versiones genéricas eliminan:
- Referencias a Parclick, Docker, PHP, proyectos específicos
- `parclick-system` y `session-init`
- Scripts internos (`~/.claude/scripts/`)

Y sustituyen por instrucciones genéricas adaptables a cualquier proyecto.

## Impacto

- **Archivos a crear:** 12 skills + 1 script = 13
- **Archivos a modificar:** 1 (`README.md`)
- **Total:** 14 archivos
- **Dominio:** docs
