# Proposal: release-workflow

## Metadata
- **Change:** release-workflow
- **Jira:** N/A (proyecto standalone)
- **Fecha:** 2026-03-11
- **Estado:** draft

## Descripción

Definir y automatizar el proceso de releases de `sdd-tui`: versionado semántico,
script de release, creación de GitHub Releases, actualización de Homebrew formula,
y proceso de hotfix.

## Motivación

El proyecto lleva 40+ changes implementados y sigue en `v0.1.0` sin ningún tag git
publicado. La Homebrew formula tiene SHA256 como placeholder. No existe ningún proceso
definido para:

- Cuándo y cómo bumpar la versión
- Cómo crear un tag y un GitHub Release
- Cómo actualizar la Homebrew formula después de un release
- Qué hacer en un hotfix vs una release normal

Consecuencia: usuarios que instalaron via Homebrew no pueden. Usuarios que instalan
via `uv tool install git+https://...` siempre obtienen `main` sin saber qué versión
tienen. La `ReleasesScreen` de la TUI siempre muestra "No releases found".

## Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|----------------|
| CI/CD automatizado (GitHub Actions) | Overhead elevado para proyecto personal sin equipo |
| Publicación en PyPI | Requiere cuenta + tokens + mantenimiento adicional; fuera de scope actual |
| Release manual sin script | Error-prone: SHA256, formula URL, tag — demasiados pasos manuales |

## Solución Propuesta

**Un script `scripts/release.sh`** que guíe el proceso completo de release:

1. Valida precondiciones (tests pasan, working tree limpio, versión bumpeada)
2. Crea el tag `vX.Y.Z` y lo pushea
3. Crea el GitHub Release via `gh release create` con release notes auto-generadas
4. Actualiza `Formula/sdd-tui.rb` con la nueva URL y SHA256 real
5. Commitea y pushea la formula actualizada

**Versionado semántico simplificado:**
- `PATCH` (0.1.x): bugfixes, mejoras menores, ajustes de UI
- `MINOR` (0.x.0): features nuevas (pantallas, bindings, providers)
- `MAJOR` (x.0.0): cambios breaking en openspec/ o incompatibilidad de config

**Proceso de hotfix:**
- Hotfix = bugfix urgente → bump PATCH → mismo flujo que release normal
- No hay ramas separadas de hotfix (proyecto con rama `main` única)

**Release notes y CHANGELOG generados desde `openspec/`:**

`openspec/changes/archive/` es la fuente canónica de lo que se ha implementado.
Cada change archivado tiene fecha (en el nombre del directorio) y descripción
(en `proposal.md` → `## Descripción`). El script generará:

1. **Release notes del GitHub Release** — changes archivados desde el último tag,
   agrupados por fecha, con la primera línea de `## Descripción` de cada proposal.
2. **`CHANGELOG.md` acumulativo** — historial completo de releases en el repo,
   regenerado/actualizado en cada release con el mismo contenido.

Formato de ejemplo:
```
## v0.2.0 — 2026-03-11

- provider-abstraction: GitHost/IssueTracker protocols + setup wizard (S)
- todos-panel: openspec/todos/ panel (T binding)
- milestone-grouping: grouping by openspec/milestones.yaml
...
```

**Versionado semántico simplificado:**
- `PATCH` (0.1.x): bugfixes, mejoras menores, ajustes de UI
- `MINOR` (0.x.0): features nuevas (pantallas, bindings, providers)
- `MAJOR` (x.0.0): cambios breaking en openspec/ o incompatibilidad de config

**Proceso de hotfix:**
- Hotfix = bugfix urgente → bump PATCH → mismo flujo que release normal
- No hay ramas separadas de hotfix (proyecto con rama `main` única)

## Impacto

| Área | Cambio |
|------|--------|
| `scripts/release.sh` | Nuevo script |
| `scripts/changelog.py` | Script Python que genera el changelog desde openspec/ |
| `CHANGELOG.md` | Nuevo archivo en el repo, generado y commitado en cada release |
| `Formula/sdd-tui.rb` | SHA256 real en cada release (actualizado por el script) |
| `openspec/specs/distribution/spec.md` | Sección de release process añadida |
| Tests | Sin nuevos tests (scripts, no lógica Python del paquete) |

## Criterios de Éxito

- [ ] `scripts/release.sh 0.2.0` ejecuta sin errores en un working tree limpio
- [ ] El tag `v0.2.0` aparece en `git tag`
- [ ] `gh release view v0.2.0` muestra las notas con todos los changes desde el inicio
- [ ] `Formula/sdd-tui.rb` tiene la URL y SHA256 del tarball real
- [ ] `CHANGELOG.md` existe en el repo con el historial completo
- [ ] `ReleasesScreen` en la TUI muestra el nuevo release

## Scope

**Incluido:**
- `scripts/release.sh`
- `scripts/changelog.py`
- `CHANGELOG.md` (generado y commitado)
- Actualización de `Formula/sdd-tui.rb` (URL + SHA256)
- Spec de release process en `openspec/specs/distribution/spec.md`
- Primera release real: `v0.2.0`

**Excluido:**
- GitHub Actions / CI automatizado
- PyPI
- Versionado automático desde commits (conventional commits, etc.)
