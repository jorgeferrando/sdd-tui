# Proposal: todos-panel

## Descripción

Añadir una pantalla `TodosScreen` a la TUI que muestre los archivos de `openspec/todos/`.
El directorio `openspec/todos/` contendrá archivos Markdown con ítems de tipo `- [ ] texto` / `- [x] texto`.
La pantalla agrupa los ítems por archivo, muestra el progreso de cada sección y permite distinguir pendientes de completados.

## Motivación

El roadmap GSD-inspirado identificó `openspec/todos/` como el siguiente panel natural tras milestone-grouping.
Actualmente no hay forma de gestionar notas abiertas, deuda técnica, ideas o ítems sueltos que no encajan
en un change activo ni en un spec canónico. Un panel de todos da visibilidad a ese espacio informal
sin requerir estructura formal.

## Alternativas consideradas

1. **Un solo `openspec/todos.md`** — más simple, pero sin posibilidad de agrupar por categoría ni de tener múltiples listas temáticas.
2. **Integración con tasks.md de changes activos** — acoplamiento incorrecto; los todos son transversales y no pertenecen a un change específico.
3. **No implementar** — se pierde el último ítem del roadmap GSD acordado.

## Impacto

| Área | Cambio |
|------|--------|
| `core/todos.py` | Nuevo módulo: `TodoItem`, `TodoFile`, `load_todos()` |
| `tui/todos.py` | Nueva pantalla: `TodosScreen` |
| `tui/epics.py` | Añadir binding `T` → `TodosScreen` |
| `tests/` | Unit tests de `load_todos` + integración TUI |
| `openspec/todos/` | Directorio ejemplo con un archivo de muestra |

Archivos nuevos: 2 (`core/todos.py`, `tui/todos.py`).
Archivos modificados: 1 (`tui/epics.py`).
Total: 3 archivos de código + tests.

## Formato de archivos todos

Cada archivo en `openspec/todos/*.md` sigue el formato estándar de checkboxes Markdown:

```markdown
# Título de la lista

- [ ] Ítem pendiente
- [x] Ítem completado
- [ ] Otro ítem pendiente
```

El título (línea `# ...`) se usa como nombre del grupo en la pantalla.
Si no hay `# título`, se usa el nombre del archivo sin extensión.

## Criterios de éxito

- `load_todos(openspec_path)` retorna `[]` si `openspec/todos/` no existe (degradación silenciosa).
- `TodosScreen` agrupa ítems por archivo, mostrando `[N/M]` completados por grupo.
- Los ítems completados aparecen tachados o en estilo `dim`.
- Binding `T` en `EpicsView` abre `TodosScreen`.
- Tests unitarios de `_build_content()` y `load_todos()` + al menos un test de navegación TUI.
- Sin regresiones en los 336 tests existentes.
