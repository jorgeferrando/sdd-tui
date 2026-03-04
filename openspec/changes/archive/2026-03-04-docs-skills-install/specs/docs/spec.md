# Spec: Distribución de SDD skills

## Metadata
- **Dominio:** docs
- **Change:** docs-skills-install
- **Fecha:** 2026-03-03
- **Estado:** approved

## Comportamiento del script de instalación

**Dado** un usuario que ha clonado el repo o descargado el script
**Cuando** ejecuta `./scripts/install-skills.sh`
**Entonces:**
- Se le pregunta dónde instalar: global o project-local
- Las skills se copian al destino elegido
- Se muestra confirmación de qué se instaló

### Opciones de instalación

| Opción | Destino | Cuándo usar |
|--------|---------|-------------|
| Global | `~/.claude/skills/` | Usar SDD en todos los proyectos |
| Project-local | `.claude/skills/` | Usar SDD solo en el proyecto actual |

### Instalación desde GitHub (sin clonar)

```bash
# Global
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install-skills.sh | bash -s -- --global

# Project-local
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install-skills.sh | bash -s -- --local
```

### Skills incluidas

Las 12 skills SDD: `sdd-init`, `sdd-new`, `sdd-explore`, `sdd-propose`, `sdd-spec`,
`sdd-design`, `sdd-tasks`, `sdd-apply`, `sdd-verify`, `sdd-archive`, `sdd-continue`, `sdd-ff`

## Reglas

- **RB-S1:** Las skills en el repo no deben contener referencias a Parclick, Docker interno, o scripts de `~/.claude/scripts/`.
- **RB-S2:** El script funciona tanto con `bash script.sh` como con `curl | bash`.
- **RB-S3:** El script no sobreescribe sin avisar si ya existen skills con el mismo nombre.
- **RB-S4:** `--global` y `--local` como flags; sin flags → modo interactivo.
- **RB-S5:** El README documenta ambas formas de instalar (script local + curl).
