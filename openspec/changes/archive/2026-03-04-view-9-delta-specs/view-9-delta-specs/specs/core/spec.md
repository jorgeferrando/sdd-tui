# Spec: Core — Spec Parser (delta format + decisions extractor)

## Metadata
- **Dominio:** core
- **Change:** view-9-delta-specs
- **Jira:** N/A
- **Fecha:** 2026-03-04
- **Versión:** 1.0
- **Estado:** draft

## Contexto

`view-9-delta-specs` necesita dos capacidades nuevas en core:

1. **Parser de delta spec**: detectar secciones `## ADDED`, `## MODIFIED`, `## REMOVED`
   en archivos `specs/{dominio}/spec.md` de un change, para que View 9 coloree el diff.

2. **Extractor de decisiones**: extraer la tabla "Decisiones Tomadas" de `design.md`
   en cada change archivado, para que la Decisions Timeline las agregue.

Ambos son módulos Python puros (`core/spec_parser.py`), sin dependencias de TUI.

## Comportamiento Actual

No existe. `core/spec_parser.py` es módulo nuevo.

## ADDED Requirements

### Delta spec parser

- **REQ-01** `[Event]` When `parse_delta(spec_path)` is called, the system SHALL return a `DeltaSpec` with sections `added`, `modified`, `removed`, each containing the lines of text under their respective `## ADDED / ## MODIFIED / ## REMOVED` heading.

- **REQ-02** `[Unwanted]` If none of the three headings are present in the file, the system SHALL return `DeltaSpec(added=[], modified=[], removed=[], fallback=True)` where `fallback=True` signals plain-text rendering.

- **REQ-03** `[Ubiquitous]` The parser SHALL be case-insensitive for section headings (`## added`, `## ADDED` both match).

- **REQ-04** `[Ubiquitous]` Lines between a recognized heading and the next recognized heading (or end of file) SHALL be assigned to that section, preserving blank lines within the section.

### Decisions extractor

- **REQ-05** `[Event]` When `extract_decisions(design_path, change_name)` is called, the system SHALL return a `ChangeDecisions` with the `change_name` and a list of `Decision` rows extracted from the `## Decisiones Tomadas` markdown table.

- **REQ-06** `[Unwanted]` If `design.md` does not exist or has no `## Decisiones Tomadas` table, the system SHALL return `ChangeDecisions(change_name=change_name, decisions=[])`.

- **REQ-07** `[Ubiquitous]` The extractor SHALL parse each row of the markdown table as a `Decision(decision, alternative, reason)` triple, skipping the header and separator rows.

- **REQ-08** `[Event]` When `collect_archived_decisions(archive_dir)` is called, the system SHALL iterate all subdirectories of `archive_dir`, extract decisions from each `design.md`, and return a list of `ChangeDecisions` ordered by archive date ascending (parsed from the directory name prefix `YYYY-MM-DD-`).

- **REQ-09** `[Unwanted]` If a directory name does not start with `YYYY-MM-DD-`, the system SHALL skip it silently (no exception).

### Escenarios de verificación

**REQ-01/02** — Delta parser con marcadores

**Dado** un spec con contenido:
```
## ADDED Requirements
- **REQ-01** `[Event]` When X...

## MODIFIED Requirements
- **REQ-02** — Before: "old" After: "new"
```
**Cuando** se llama `parse_delta(path)`
**Entonces** `delta.added = ["- **REQ-01** ..."]`, `delta.modified = ["- **REQ-02** ..."]`, `delta.fallback = False`

**REQ-02** — Fallback sin marcadores

**Dado** un spec con contenido libre (sin `## ADDED/MODIFIED/REMOVED`)
**Cuando** se llama `parse_delta(path)`
**Entonces** `delta.fallback = True`, `added/modified/removed` vacíos

**REQ-08** — Orden de decisiones

**Dado** archive con `2026-02-01-view-2/` y `2026-03-04-view-8/`
**Cuando** se llama `collect_archived_decisions(archive_dir)`
**Entonces** retorna view-2 primero, view-8 segundo

## Interfaces / Contratos

```python
@dataclass
class DeltaSpec:
    added: list[str]      # líneas bajo ## ADDED
    modified: list[str]   # líneas bajo ## MODIFIED
    removed: list[str]    # líneas bajo ## REMOVED
    fallback: bool        # True si no hay marcadores → mostrar texto plano

@dataclass
class Decision:
    decision: str
    alternative: str
    reason: str

@dataclass
class ChangeDecisions:
    change_name: str       # nombre sin prefijo de fecha (ej: "view-8-spec-health")
    archive_date: date     # fecha del prefijo del directorio
    decisions: list[Decision]

def parse_delta(spec_path: Path) -> DeltaSpec: ...
def extract_decisions(design_path: Path, change_name: str) -> ChangeDecisions: ...
def collect_archived_decisions(archive_dir: Path) -> list[ChangeDecisions]: ...
```

## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| `fallback=True` en lugar de excepción | Excepción si sin marcadores | Los delta specs legacy (sin marcadores) deben funcionar sin error |
| Orden por prefijo YYYY-MM-DD en nombre de directorio | git log por change name | El prefijo de archive ya ES la fecha canónica; no requiere git |
| `change_name` sin prefijo de fecha en `ChangeDecisions` | Nombre completo del directorio | El nombre semántico es más legible en la timeline |
| Regex para tabla markdown `\| .+ \| .+ \| .+ \|` | Parser MD completo | Suficiente para extraer filas sin AST |

## Abierto / Pendiente

Ninguno.
