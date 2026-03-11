# Spec: Core — Todos Reader

## Metadata
- **Dominio:** core
- **Change:** todos-panel
- **Fecha:** 2026-03-11
- **Versión:** 0.1
- **Estado:** draft

## Contexto

`openspec/todos/` es un directorio libre donde el usuario puede colocar archivos Markdown
con ítems tipo `- [ ] texto` / `- [x] texto`. Es un espacio informal para notas abiertas,
deuda técnica o ideas que no encajan en un change activo. No hay estructura formal más allá
del formato de checkboxes Markdown estándar.

## Modelo de Datos

```python
@dataclass
class TodoItem:
    text: str     # texto del ítem (sin el checkbox)
    done: bool    # True si [x], False si [ ]

@dataclass
class TodoFile:
    title: str           # encabezado # del archivo, o nombre del archivo sin extensión
    items: list[TodoItem]
```

## Requisitos (EARS)

- **REQ-TD-01** `[Event]` When `load_todos(openspec_path)` is called and `openspec/todos/` exists, the system SHALL return a `list[TodoFile]` parsed from all `*.md` files in that directory, sorted alphabetically by filename.
- **REQ-TD-02** `[Unwanted]` If `openspec/todos/` does not exist, the system SHALL return `[]` without raising.
- **REQ-TD-03** `[Unwanted]` If a file cannot be read or decoded, the system SHALL skip it silently.
- **REQ-TD-04** `[Ubiquitous]` The `TodoFile.title` SHALL be the text of the first `# Heading` found in the file; if none, the filename stem.
- **REQ-TD-05** `[Ubiquitous]` Only lines matching `- [ ] text` or `- [x] text` SHALL be parsed as `TodoItem`; all other lines SHALL be ignored.
- **REQ-TD-06** `[Ubiquitous]` The parser SHALL NOT require PyYAML or any dependency beyond stdlib.
- **REQ-TD-07** `[Unwanted]` If a file contains no checkbox lines, the system SHALL include a `TodoFile` with `items=[]`.

## Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Directorio vacío | `todos/` existe pero sin `.md` | `[]` |
| Archivo sin heading | Sin línea `# ...` | `title` = filename stem |
| Archivo sin ítems | Solo texto plano | `TodoFile(title=..., items=[])` |
| Ítems mixtos | `[x]` y `[ ]` en el mismo archivo | Ambos parseados correctamente |
| Encoding inválido | Caracteres especiales | `errors="replace"`, nunca `UnicodeDecodeError` |
| Archivos no-md | `.yaml`, `.json` en `todos/` | Ignorados (solo `*.md`) |

## Interfaz pública

```python
def load_todos(openspec_path: Path) -> list[TodoFile]: ...
```

## Reglas de negocio

- **RB-TD-01:** `load_todos` no lanza excepciones — todos los errores retornan `[]` o saltan el archivo.
- **RB-TD-02:** El orden de `TodoFile` en la lista es alfabético por nombre de archivo.
- **RB-TD-03:** El orden de `TodoItem` dentro de cada `TodoFile` es el de aparición en el archivo.
- **RB-TD-04:** El regex de ítem es `^- \[([ x])\] (.+)$` (strip de línea antes de aplicar).

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|-------------|--------|
| Un directorio `openspec/todos/` con múltiples `.md` | Un único `todos.md` | Permite categorías temáticas independientes sin editar un solo archivo monolítico |
| Solo checkboxes Markdown (`- [ ]`) | Formato custom | Estándar ampliamente reconocido, editables desde cualquier editor |
| Parsing con stdlib (regex) | PyYAML | Consistente con `milestones.py` y `config.py` — sin dependencias nuevas |
| `TodoFile.items=[]` si sin ítems | Excluir el archivo | El archivo existe aunque esté vacío de ítems — visibilidad total |
