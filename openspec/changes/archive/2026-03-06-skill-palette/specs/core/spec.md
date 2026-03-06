# Spec: Core — Skills reader

## Metadata
- **Dominio:** core
- **Change:** skill-palette
- **Fecha:** 2026-03-06
- **Versión:** 0.1
- **Estado:** approved

## Contexto

El TUI necesita listar los skills disponibles en `~/.claude/skills/` para
mostrarlos en la `SkillPaletteScreen`. El lector es agnóstico a la TUI —
devuelve una lista de `SkillInfo` que la pantalla consume.

---

## Requisitos (EARS)

- **REQ-01** `[Event]` When `load_skills(skills_dir)` es llamado, the reader SHALL escanear todos los subdirectorios de `skills_dir` y retornar `list[SkillInfo]` ordenada.
- **REQ-02** `[Event]` When se procesa un subdirectorio, the reader SHALL leer el front matter YAML de `{subdir}/SKILL.md` y extraer `name` y `description`.
- **REQ-03** `[Unwanted]` If `skills_dir` no existe, the reader SHALL retornar lista vacía `[]` sin lanzar excepción.
- **REQ-04** `[Unwanted]` If un subdirectorio no tiene `SKILL.md`, the reader SHALL ignorarlo silenciosamente.
- **REQ-05** `[Unwanted]` If `SKILL.md` existe pero no tiene front matter YAML válido o le faltan los campos `name`/`description`, the reader SHALL ignorar ese skill silenciosamente.
- **REQ-06** `[Ubiquitous]` The reader SHALL retornar los skills SDD primero (nombre con prefijo `sdd-`), ordenados entre sí alfabéticamente, seguidos del resto también ordenados alfabéticamente.
- **REQ-07** `[Ubiquitous]` The `SkillInfo` SHALL contener exactamente: `name: str`, `description: str`.

## Modelo de Datos

```python
@dataclass
class SkillInfo:
    name: str           # ej: "sdd-apply"
    description: str    # ej: "SDD Apply - Implementación del cambio..."
```

## Interfaz pública

```python
def load_skills(skills_dir: Path) -> list[SkillInfo]:
    """Escanea skills_dir y retorna lista de SkillInfo ordenada."""
```

Uso estándar desde TUI:
```python
from pathlib import Path
skills = load_skills(Path.home() / ".claude" / "skills")
```

## Escenarios de verificación

**REQ-01 + REQ-06** — orden SDD-first
**Dado** un `skills_dir` con: `build/`, `sdd-apply/`, `sdd-new/`, `docker/`
**Cuando** se llama `load_skills(skills_dir)`
**Entonces** el orden retornado es: `sdd-apply`, `sdd-new`, `build`, `docker`

**REQ-03** — directorio inexistente
**Dado** un path que no existe
**Cuando** se llama `load_skills(path)`
**Entonces** se retorna `[]` sin excepción

**REQ-05** — SKILL.md sin front matter
**Dado** un skill con `SKILL.md` que no tiene bloque `---` YAML
**Cuando** se llama `load_skills`
**Entonces** ese skill no aparece en el resultado

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Front matter YAML como fuente de verdad | Parsear nombre del directorio | Los skills ya tienen front matter estándar — reutilizar en lugar de inventar convención nueva |
| Retornar `[]` si el dir no existe | Lanzar `SkillsDirNotFoundError` | La ausencia de `~/.claude/skills/` es un estado válido en instalaciones nuevas |
| SDD-first por prefijo `sdd-` | Config explícita de orden | El prefijo ya distingue los skills SDD — sin configuración extra |

## Abierto / Pendiente

Ninguno.
