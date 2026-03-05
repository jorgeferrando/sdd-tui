# Design: sdd-setup-experience

## Metadata
- **Change:** sdd-setup-experience
- **Proyecto:** sdd-tui (Python + Textual)
- **Fecha:** 2026-03-05
- **Estado:** draft

## Resumen Técnico

Se añade un segundo CLI entry point (`sdd-setup`) al paquete Python existente. La lógica
reside en `src/sdd_tui/setup.py`, siguiendo el mismo patrón que `tui/app.py` (módulo con
`main()` registrado en `pyproject.toml`).

Los skills se descargan de GitHub en el momento de ejecutar `sdd-setup` (shallow clone de
`main`), reutilizando el mismo mecanismo que `install-skills.sh`. Esto garantiza que el usuario
siempre obtiene la versión más reciente, independientemente de qué versión del paquete TUI tenga
instalada.

Los instaladores de plataforma (Homebrew, Linux, Windows) son artefactos independientes
que orquestan: instalar TUI → invocar `sdd-setup`.

## Arquitectura

```
Usuario
  │
  ├─ brew install sdd-tui / uv tool install / install.sh / Install-SddTui.ps1
  │     └─ instala el wheel (solo TUI — skills no incluidos)
  │
  └─ sdd-setup [--global|--local|--check]
        │
        ├─ git clone --depth=1 github.com/jorgeferrando/sdd-tui → /tmp/sdd-tui-XXXX/
        │     (siempre la versión más reciente de main)
        │
        ├─ Destino: ~/.claude/skills/  (--global)
        │           .claude/skills/    (--local)
        │           interactivo        (sin flags)
        │
        ├─ shutil.copytree → destino/sdd-*/
        └─ rm -rf /tmp/sdd-tui-XXXX/
```

## Archivos a Crear

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `src/sdd_tui/setup.py` | CLI module | Lógica de `sdd-setup`: flags, detección skills, copia, check |
| `tests/test_setup.py` | Tests | Cobertura unitaria de setup.py |
| `Formula/sdd-tui.rb` | Homebrew | Formula para `brew tap jorgeferrando/sdd-tui` |
| `scripts/install.sh` | Shell | Instalador Linux: detecta pkg manager, instala TUI + skills |
| `scripts/Install-SddTui.ps1` | PowerShell | Instalador Windows: detecta pkg manager, instala TUI + skills |

## Archivos a Modificar

| Archivo | Cambio | Motivo |
|---------|--------|--------|
| `pyproject.toml` | Añadir entry point `sdd-setup` + `force-include` skills | Registrar CLI y bundlear skills en wheel |
| `README.md` | Reescribir sección Install (por plataforma) | REQ-DOC01–03 |

## Scope

- **Total archivos:** 7
- **Resultado:** Ideal (< 10)

## Dependencias Técnicas

- Sin dependencias nuevas de runtime — solo stdlib: `argparse`, `importlib.resources`,
  `importlib.metadata`, `shutil`, `sys`, `pathlib`
- `importlib.resources.files()` requiere Python 3.9+ (ya cubierto: `requires-python = ">=3.11"`)
- `hatch` como build backend ya está configurado — solo se añade `force-include`

## Detalle de Implementación

### `pyproject.toml`

```toml
[project.scripts]
sdd-tui   = "sdd_tui.tui.app:main"
sdd-setup = "sdd_tui.setup:main"         # nuevo — sin cambios en build targets

[tool.hatch.build.targets.wheel]
packages = ["src/sdd_tui"]              # sin cambios — skills no se bundlean
```

### `src/sdd_tui/setup.py` — estructura

```
main()
  → parse_args()          → argparse: --global, --local, --check
  → resolve_destination() → pregunta interactiva si no hay flag
  → run_check()           ← --check: versión paquete + source URL + skills instalados
  → fetch_skills()        → git clone --depth=1 a tempfile.mkdtemp()
      → _clone_repo()     → subprocess: git clone github.com/jorgeferrando/sdd-tui
      → itera tmp/skills/sdd-*/
      → _skill_exists()   → comprueba si ya existe en destino
      → _prompt_conflict()→ preguntar: update / skip / per-skill
      → _copy_skill()     → shutil.copytree(..., dirs_exist_ok=True)
      → cleanup tmp dir   → shutil.rmtree(tmp)
  → check_claude_in_path()→ aviso informativo si `claude` no en PATH
  → print_summary()       → installed/updated/skipped + next step
```

### `sdd-setup --check` output

```
sdd-tui version:    0.1.0
skills source:      github.com/jorgeferrando/sdd-tui (main)

installed skills (→ ~/.claude/skills/):
  ✓  sdd-apply
  ✓  sdd-init
  ✗  sdd-steer    (not installed)
  ...
```

La versión del paquete se obtiene via `importlib.metadata.version("sdd-tui")`.
Los skills no tienen versión propia — siempre se descargan desde `main`.

### `Formula/sdd-tui.rb` — estructura mínima

```ruby
class SddTui < Formula
  include Language::Python::Virtualenv

  desc "TUI for Spec-Driven Development workflow"
  homepage "https://github.com/jorgeferrando/sdd-tui"
  url "https://github.com/jorgeferrando/sdd-tui/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.11"

  resource "textual" do ... end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"sdd-tui", "--help"
    system bin/"sdd-setup", "--help"
  end
end
```

> Nota: el SHA256 se actualiza en cada release. El `resource "textual"` se genera con
> `poet` o `brew-pip-audit` — se documenta en tasks.md cómo obtenerlo.

### `scripts/install.sh` — flujo

```
1. Detectar pkg manager: uv → pipx → pip (primer disponible)
2. Si ninguno: imprimir instrucciones uv + exit 1
3. Instalar TUI: uv tool install / pipx install / pip install
4. Si --skip-skills: fin
5. Invocar: sdd-setup --global
```

### `scripts/Install-SddTui.ps1` — flujo idéntico en PowerShell 5.1+

Mismo flujo que install.sh, con `-SkipSkills` como switch parameter.

## Patrones Aplicados

- **Entry point Python estándar:** igual que `sdd-tui = "sdd_tui.tui.app:main"` — sin boilerplate extra
- **`deps.py` como referencia:** el patrón `check_cmd` + `_is_present()` se reutiliza conceptualmente para detectar `claude` en PATH
- **`install-skills.sh` como referencia:** el mecanismo de shallow clone + copy se porta a Python en `_clone_repo()` + `_copy_skill()`

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Skills descargados de GitHub | Bundlear en wheel | Skills y TUI evolucionan independientemente; actualizar skills no requiere reinstalar el paquete |
| `scripts/install.sh` nuevo (no renombrar `install-skills.sh`) | Renombrar | `install-skills.sh` permanece como método legacy documentado; no se rompen referencias existentes |
| Conflict → preguntar (update/skip/per-skill) | Saltar silenciosamente | El usuario puede tener customizaciones; sobreescribir silenciosamente sería destructivo |

## Tests Planificados

| Test | Tipo | Qué verifica |
|------|------|-------------|
| `test_resolve_destination_global` | Unit | `--global` → `~/.claude/skills/` sin prompt |
| `test_resolve_destination_local` | Unit | `--local` → `.claude/skills/` sin prompt |
| `test_install_new_skill` | Unit | Skill no existente → se copia, aparece en summary como "installed" |
| `test_install_skill_conflict_update` | Unit | Skill existente + user elige "update" → overwrite |
| `test_install_skill_conflict_skip` | Unit | Skill existente + user elige "skip" → no modificado |
| `test_check_output` | Unit | `--check` imprime versión paquete + skills bundled + estado instalados |
| `test_claude_not_in_path_warning` | Unit | `claude` ausente → aviso informativo, exit 0 |
| `test_permissions_error` | Unit | Destino sin permisos → exit 1 con mensaje claro |

## Notas de Implementación

- `git clone --depth=1` es la misma estrategia que `install-skills.sh` — usar `subprocess.run` con `check=True` y capturar stderr para mensajes de error claros
- Usar `tempfile.mkdtemp()` + `try/finally` para garantizar cleanup aunque falle el clone
- El SHA256 de la Homebrew formula se calcula con:
  `curl -L <url> | sha256sum` — documentar en tasks.md como paso manual
- `install.sh` instala primero la TUI (que incluye `sdd-setup`) y luego invoca `sdd-setup --global`; `sdd-setup` se encarga del clone de skills — sin duplicar lógica de descarga
