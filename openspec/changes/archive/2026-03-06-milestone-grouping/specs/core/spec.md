# Spec: Core — Milestone Reader

## Metadata
- **Dominio:** core
- **Change:** milestone-grouping
- **Fecha:** 2026-03-06
- **Versión:** 1.5
- **Estado:** draft

## Contexto

Nuevo módulo `core/milestones.py` que lee `openspec/milestones.yaml` y retorna
agrupaciones lógicas de changes. Sin dependencias externas — parsing manual
consistente con el patrón establecido en `core/config.py`.

## ADDED

### Modelo de Datos

```python
@dataclass
class Milestone:
    name: str            # ej: "v1.0 — Bootstrap"
    changes: list[str]   # nombres de changes asignados (en orden declarado)
```

### `load_milestones(openspec_path: Path) -> list[Milestone]`

**Dado** un path al directorio `openspec/`
**Cuando** se llama a `load_milestones(openspec_path)`
**Entonces** se retorna la lista de `Milestone` definidos en `openspec/milestones.yaml`,
en el orden en que aparecen en el archivo

### Formato milestones.yaml

```yaml
milestones:
  - name: "v1.0 — Bootstrap"
    changes:
      - bootstrap
      - view-2-change-detail
  - name: "v1.1 — UX"
    changes:
      - ux-feedback
      - ux-navigation
```

### Requisitos (EARS)

- **REQ-ML-01** `[Event]` When `load_milestones(openspec_path)` is called and `milestones.yaml` exists, the system SHALL return a `list[Milestone]` parsed from the file, in declaration order.
- **REQ-ML-02** `[Unwanted]` If `milestones.yaml` does not exist, the system SHALL return `[]` without raising.
- **REQ-ML-03** `[Unwanted]` If `milestones.yaml` is malformed or unparseable, the system SHALL return `[]` without raising.
- **REQ-ML-04** `[Unwanted]` If a milestone block has no `changes:` list, the system SHALL include the milestone with `changes=[]`.
- **REQ-ML-05** `[Ubiquitous]` The parser SHALL NOT require PyYAML — parsing SHALL be implemented with stdlib only (regex + string ops).

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Archivo no existe | `milestones.yaml` ausente | `[]` |
| Archivo vacío | Sin contenido | `[]` |
| Milestone sin changes | `changes:` ausente o vacía | `Milestone(name=..., changes=[])` |
| Nombres con guiones | `view-2-change-detail` | Preservado exactamente |
| Encoding inválido | Caracteres especiales | `errors="replace"`, nunca `UnicodeDecodeError` |

### Reglas de negocio

- **RB-ML-01:** Parser de estado: detecta `milestones:` → luego `- name:` → luego `  - change-name` dentro del bloque de changes.
- **RB-ML-02:** `load_milestones` no lanza excepciones — todos los errores retornan `[]`.
- **RB-ML-03:** El orden de milestones en la lista de retorno es el mismo que en el YAML.
- **RB-ML-04:** Los nombres de changes en `Milestone.changes` son exactamente los strings del YAML (sin trim extra).
