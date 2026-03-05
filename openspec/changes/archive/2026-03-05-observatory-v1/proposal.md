# Proposal: observatory-v1 — Multi-project Support

## Metadata
- **Change:** observatory-v1
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema / Motivación

`sdd-tui` inspecciona un proyecto a la vez: siempre `Path.cwd()`.
Un desarrollador con varios repositorios SDD necesita abrir una instancia
separada por proyecto. No hay visión cruzada.

**Nota:** Este change es la primera de tres features separadas:
1. `observatory-v1` — Multi-project (este change)
2. `pr-status` — GitHub PR status en Pipeline sidebar
3. `velocity-metrics` — Métricas de throughput y lead time

## Solución Propuesta

### Config en `~/.sdd-tui/config.yaml` (global, opcional)

```yaml
projects:
  - path: ~/sites/sdd-tui
  - path: ~/PhpstormProjects/next
  - path: ~/PhpstormProjects/front
```

Si no existe → comportamiento legacy (single-project desde `cwd`).

### View 1 multi-proyecto

EpicsView agrupa changes de todos los proyectos con separadores:

```
─── sdd-tui ────────────────────────────────────────
  observatory-v1        ✓ · · · ·  [spec]
─── next ───────────────────────────────────────────
  di-464-parking        ✓ ✓ ✓ ✓ ·  [apply T03]
  di-471-rates          ✓ ✓ · · ·  [design]
─── front ──────────────────────────────────────────
  (no active changes)
```

Cada change mantiene una referencia a su proyecto origen.
`Enter` → ChangeDetailScreen funciona igual que antes.

### Navegación

- La app navega con `push_screen` / `pop_screen` igual que siempre.
- El proyecto de un change se pasa al construir `ChangeDetailScreen` — sin routing nuevo.
- `r` recarga todos los proyectos.

## Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|---------------|
| Dashboard separado (ProjectDashboard screen) | Duplica UI; la tabla de changes ya es el dashboard |
| Config por proyecto en `openspec/config.yaml` | Contamina el repo con paths locales del usuario |
| `~/.config/sdd-tui/config.yaml` (XDG) | `~/.sdd-tui/config.yaml` es más simple y discoverable |

## Impacto Estimado

| Archivo | Cambio |
|---------|--------|
| `core/config.py` | Nuevo: loader + validator de `~/.sdd-tui/config.yaml` |
| `core/reader.py` | `load_changes(path)` acepta path explícito; `load_all_changes(config)` agrega todos |
| `tui/epics.py` | Separadores por proyecto; `Change` lleva referencia al proyecto |
| `tui/app.py` | Carga config al arrancar; pasa lista de proyectos a EpicsView |
| `tests/test_config.py` | Nuevo: tests unitarios del config loader |
| `tests/test_tui_epics.py` | Casos multi-project |

Estimación: ~6-8 archivos modificados/nuevos.

## Criterios de Exito

- [ ] Sin `~/.sdd-tui/config.yaml`, el comportamiento es idéntico al actual
- [ ] Con config, View 1 muestra changes de todos los proyectos agrupados con separadores
- [ ] `Enter` sobre cualquier change (de cualquier proyecto) abre ChangeDetailScreen correctamente
- [ ] `r` recarga todos los proyectos
- [ ] Tests >= 120 (actualmente 111)
