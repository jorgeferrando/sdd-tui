# Design: Release Workflow

## Metadata
- **Change:** release-workflow
- **Jira:** N/A
- **Proyecto:** sdd-tui
- **Fecha:** 2026-03-11
- **Estado:** draft

## Resumen Técnico

El change añade una capa de configuración optativa (`ReleaseWorkflowConfig`) que extiende
el modelo existente de `GitWorkflowConfig` siguiendo el mismo patrón: dataclass en
`core/providers/protocol.py`, parser/writer en `core/reader.py`, wizard steps en
`tui/setup.py`, y check en `App.on_mount`.

Los scripts (`changelog.py`, `release.sh`) son independientes del paquete Python —
no se importan desde la TUI. `changelog.py` usa solo stdlib Python. `release.sh` solo
requiere bash, git, uv, gh, curl.

## Arquitectura

```
config.yaml
  └── release_workflow: section
        ↓
  core/providers/protocol.py
    ReleaseWorkflowConfig (dataclass)
        ↓
  core/reader.py
    load_release_config(openspec_path) → ReleaseWorkflowConfig
    _parse_release_workflow(text) → ReleaseWorkflowConfig
    _write_release_config(openspec_path, cfg)
        ↓
  tui/setup.py
    GitWorkflowSetupScreen
      _RELEASE_QUESTIONS (3 nuevos pasos, condicionales)
      _save_and_dismiss() → también llama _write_release_config
        ↓
  tui/app.py
    on_mount()
      load_release_config(openspec_path)
      si cfg ausente → self.notify("Release workflow not configured...")

scripts/changelog.py (standalone, stdlib)
  git rev-parse --show-toplevel  → repo root
  load openspec/config.yaml      → release_workflow.enabled
  git tag --sort=-version:refname → tag boundaries (si enabled=true)
  openspec/versions/*.yaml        → marker boundaries (si enabled=false o no tags)
  openspec/changes/archive/*/proposal.md → change descriptions
  → CHANGELOG.md (overwrite)
  --mark-version X.Y.Z → openspec/versions/X.Y.Z.yaml
  --version X.Y.Z      → stdout solo esa sección

scripts/release.sh (bash)
  lee openspec/config.yaml via grep/awk
  orquesta: validate → pytest → git clean → bump → changelog → tag → gh release → formula
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `scripts/changelog.py` | Script Python | Genera CHANGELOG.md desde openspec/archive + version boundaries |
| `scripts/release.sh` | Script Bash | Orquesta el proceso completo de release |
| `openspec/versions/.gitkeep` | Marker | Mantiene el directorio vacío en git |
| `tests/test_changelog.py` | Tests | Cobertura de changelog.py (descripción, boundaries, mark-version, --version) |
| `tests/test_release_config.py` | Tests | Cobertura de load_release_config y _write_release_config |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `src/sdd_tui/core/providers/protocol.py` | Añadir `ReleaseWorkflowConfig` dataclass | Contrato de config de release |
| `src/sdd_tui/core/reader.py` | Añadir `load_release_config`, `_parse_release_workflow`, `_write_release_config` | Mismo patrón que git_workflow |
| `src/sdd_tui/tui/setup.py` | Añadir `_RELEASE_QUESTIONS` + lógica condicional + extender `_save_and_dismiss` | REQ-WZ06-09 |
| `src/sdd_tui/tui/app.py` | `on_mount`: check release_workflow ausente → notify | REQ-OB01-03 |
| `tests/test_tui_setup.py` | Añadir casos: release yes/no, wizard completo con release steps | Cobertura wizard extendido |

## Scope

- **Total archivos:** 10
- **Resultado:** Ideal ✓

## Dependencias Técnicas

- No depende de PRs externos
- `scripts/changelog.py` usa solo stdlib Python — sin dependencias adicionales
- `scripts/release.sh` requiere en runtime: `git`, `uv`, `gh`, `curl`, `python3`
- `openspec/versions/` se crea al primer `--mark-version` si no existe

## Patrones Aplicados

- **GitWorkflowConfig pattern**: `ReleaseWorkflowConfig` sigue exactamente el mismo
  patrón — dataclass con defaults, parser de YAML manual (sin dependencia a PyYAML),
  writer que reemplaza la sección en config.yaml. Ver `_parse_git_workflow` / `_write_git_workflow_config` en `core/reader.py`.

- **Wizard condicional**: Los pasos 7-8 del wizard (versioning, formula) solo se muestran
  si el usuario eligió `yes` en el paso 6. Se implementa en `_record_answer` saltando
  pasos según `self._answers["releases_enabled"]`.

- **on_mount check pattern**: Mismo patrón que el check de deps en `on_mount` —
  condición → `self.notify(...)`. No es bloqueante. Flag `_release_notified` evita
  repetición por screen changes.

## Detalle de Implementación

### `ReleaseWorkflowConfig` (protocol.py)

```python
@dataclass
class ReleaseWorkflowConfig:
    enabled: bool = False
    versioning: str = "semver"          # "semver" | "calver" | "none"
    changelog_source: str = "openspec"  # "openspec" | "manual" | "none"
    homebrew_formula: str | None = None
```

### `load_release_config` (reader.py)

```python
def load_release_config(openspec_path: Path) -> tuple[ReleaseWorkflowConfig, bool]:
    """Returns (config, is_configured).
    is_configured=False when release_workflow: section is absent from config.yaml."""
```

Retorna una tupla para que `on_mount` distinga "ausente" (notificar) de
`enabled=False` (no notificar). No puede inferirse solo desde el dataclass porque
los defaults son los mismos que "ausente".

### Wizard — pasos de release (setup.py)

```python
_RELEASE_QUESTIONS = [
    {
        "key": "releases_enabled",
        "title": "Does this project publish releases?",
        "options": [("yes", "Yes — tags, GitHub Releases"), ("no", "No — track versions in openspec/ only")],
    },
    {
        "key": "versioning",
        "title": "Which versioning scheme?",
        "options": [("semver", "Semantic versioning (1.2.3)"), ("calver", "Calendar versioning (2026.03.11)"), ("none", "No versioning")],
        "skip_if": lambda answers: answers.get("releases_enabled") == "no",
    },
    {
        "key": "homebrew_formula",
        "title": "Homebrew formula path? (relative to repo root)",
        "options": [("Formula/{project}.rb", "Formula/{project}.rb  (default)"), ("none", "No Homebrew formula")],
        "skip_if": lambda answers: answers.get("releases_enabled") == "no",
    },
]
```

Los `_QUESTIONS` existentes + `_RELEASE_QUESTIONS` se concatenan. `_record_answer`
evalúa `skip_if` antes de mostrar el siguiente paso.

### `_save_and_dismiss` extendido (setup.py)

```python
def _save_and_dismiss(self) -> None:
    cfg = GitWorkflowConfig(...)        # pasos 1-5
    _write_git_workflow_config(...)
    rel_cfg = ReleaseWorkflowConfig(
        enabled=self._answers.get("releases_enabled") == "yes",
        versioning=self._answers.get("versioning", "semver"),
        homebrew_formula=... or None,
    )
    _write_release_config(self._openspec_path, rel_cfg)
    self.app.notify("Workflow configured ✓")
    self.app.pop_screen()
```

### `on_mount` check (app.py)

```python
_rel_cfg, _rel_configured = load_release_config(self._openspec_path)
if not _rel_configured:
    self.notify("Release workflow not configured — press S to set up", timeout=8)
```

Nota: `load_release_config` puede fallar silenciosamente (igual que `load_git_workflow_config`)
y retornar `(ReleaseWorkflowConfig(), False)`. `enabled=False` con `is_configured=True`
significa que el usuario eligió "no".

### `changelog.py` — estructura interna

```python
def find_repo_root() -> Path        # git rev-parse --show-toplevel
def load_release_config(root) -> ReleaseWorkflowConfig
def collect_archived_changes(archive_dir) -> list[ChangeEntry]
  # ChangeEntry: name, date, description
def collect_version_boundaries(root, cfg) -> list[VersionBoundary]
  # Combina git tags + openspec/versions/*.yaml según cfg.enabled
def assign_changes_to_versions(changes, boundaries) -> dict[str, list[ChangeEntry]]
def render_changelog(assignments, repo_url) -> str
def extract_section(changelog_text, version) -> str   # para --version flag
def mark_version(root, version)                        # para --mark-version flag
```

### `release.sh` — lectura de config

El script lee `openspec/config.yaml` con `grep`/`awk` básico para extraer
`changelog_source` y `homebrew_formula` sin depender de Python ni PyYAML.
Ejemplo:
```bash
CHANGELOG_SOURCE=$(awk '/^release_workflow:/{f=1} f && /changelog_source:/{print $2; exit}' openspec/config.yaml)
```

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_load_release_config_absent` | Unit | Retorna `(defaults, False)` cuando no hay sección |
| `test_load_release_config_enabled` | Unit | Parsea `enabled: true` correctamente |
| `test_load_release_config_disabled` | Unit | Parsea `enabled: false` → `is_configured=True` |
| `test_write_release_config_new` | Unit | Escribe sección nueva en config.yaml |
| `test_write_release_config_replace` | Unit | Reemplaza sección existente |
| `test_collect_archived_changes` | Unit | Extrae date, name, description de archive/ |
| `test_collect_version_boundaries_from_markers` | Unit | Lee openspec/versions/*.yaml |
| `test_assign_changes_no_boundaries` | Unit | Todos bajo [Unreleased] |
| `test_assign_changes_with_boundary` | Unit | Changes divididos por fecha de marker |
| `test_mark_version_creates_yaml` | Unit | Crea openspec/versions/0.2.0.yaml |
| `test_extract_section` | Unit | Extrae sección correcta para --version |
| `test_wizard_release_yes_flow` | TUI async | Wizard completo con releases=yes llega a versioning+formula |
| `test_wizard_release_no_flow` | TUI async | Wizard con releases=no salta versioning y formula |
| `test_wizard_saves_release_config` | TUI async | _save_and_dismiss escribe release_workflow: en config.yaml |
| `test_on_mount_notifies_unconfigured` | TUI async | Notificación aparece si release_workflow ausente |
| `test_on_mount_no_notify_if_disabled` | TUI async | Sin notificación si enabled=false |

## Notas de Implementación

- `changelog.py` es Python puro (stdlib: `pathlib`, `subprocess`, `datetime`, `re`,
  `argparse`) — sin imports del paquete `sdd_tui`. Funciona con cualquier Python 3.11+.
- El check `is_configured` se resuelve buscando la línea `release_workflow:` en config.yaml
  antes de parsear valores — simple y consistente con el parser manual existente.
- `openspec/versions/` se crea automáticamente en `--mark-version` si no existe
  (igual que `openspec_path.mkdir(parents=True, exist_ok=True)` en `_write_git_workflow_config`).
- `release.sh` usa `set -euo pipefail` — cualquier comando fallido aborta el script.
- SHA256 del tarball via `curl -sL <url> | sha256sum` — una sola línea, sin descargar
  el fichero a disco.
