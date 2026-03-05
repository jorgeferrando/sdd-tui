# Proposal: sdd-setup-experience

## Metadata
- **Change:** sdd-setup-experience
- **Fecha:** 2026-03-05
- **Estado:** draft

## Problema

La experiencia de instalación actual de sdd-tui requiere múltiples pasos manuales:

1. Instalar la TUI: `uv tool install git+https://github.com/jorgeferrando/sdd-tui`
2. Instalar skills por separado: `./scripts/install-skills.sh` (o via curl)
3. Reiniciar Claude Code
4. Ejecutar `/sdd-init` en el proyecto

Esto crea fricción de entrada, especialmente para usuarios nuevos que no saben qué paso va primero o por qué existen dos instalaciones separadas. Además, no existe un canal de distribución estándar (Homebrew, apt, etc.) para macOS/Linux/Windows.

## Solución Propuesta

### 1. Entrypoint `sdd-setup` (CLI unificado)

Añadir un segundo script en `pyproject.toml` que, al ejecutarse, realiza todo el onboarding post-instalación:

```
sdd-setup
  → Detecta si los skills ya están instalados
  → Ofrece instalarlos (global / local)
  → Verifica dependencias (git, gh, uv)
  → Muestra el siguiente paso: abrir Claude Code y ejecutar /sdd-init
```

No requiere clonar el repo — el paquete incluye los skills. `sdd-setup` los extrae desde dentro del paquete instalado.

### 2. Homebrew Formula (macOS + Linux via Linuxbrew)

Crear `Formula/sdd-tui.rb` en el repositorio para distribución via Homebrew:

```
brew tap jorgeferrando/sdd-tui
brew install sdd-tui
sdd-setup  ← instala skills y verifica entorno
```

La formula instala Python + la TUI via pipx embebido o el sistema Python del Homebrew.

### 3. Instaladores para Linux y Windows

- **Linux:** Script `install.sh` mejorado con detección de distro, soporte apt/yum/dnf, y empaquetado como `.deb`/`.rpm` opcional.
- **Windows:** Script PowerShell `scripts/Install-SddTui.ps1` que instala la TUI via pip/uv y copia los skills al directorio correcto. Sencillo e incluido en este change. Instrucciones para Scoop/Winget quedan fuera (requieren mantener manifests externos).

## Alternativas Consideradas

### A. Solo mejorar README
Documentación más clara sin cambiar el flujo. Descartado: el problema es estructural, no de documentación.

### B. Docker container
`docker run sdd-tui`. Descartado: la TUI necesita terminal interactiva y acceso al filesystem del proyecto; la fricción de montaje de volúmenes sería igual o mayor.

### C. Publicar en PyPI
PyPI es el repositorio oficial de paquetes Python (`pip install <nombre>`). Permitiría `pip install sdd-tui` sin URL de GitHub. Descartado en este change: requiere cuenta PyPI, tokens, y CI/CD para auto-publish — no resuelve el problema de los skills ni de los gestores de paquetes nativos. Candidate para un change futuro independiente.

## Impacto

**Archivos a crear/modificar:**
- `pyproject.toml` — añadir entrypoint `sdd-setup`
- `src/sdd_tui/setup.py` — lógica del CLI `sdd-setup`
- `Formula/sdd-tui.rb` — Homebrew formula
- `scripts/install.sh` — reemplaza/extiende `install-skills.sh` para Linux
- `scripts/Install-SddTui.ps1` — nuevo, para Windows
- `README.md` — actualizar sección Install con los nuevos canales

**Tests:**
- Tests unitarios para `setup.py` (detección de skills, paths, flags)
- Los tests TUI existentes no se ven afectados

**Sin cambios en:** lógica de la TUI, skills, openspec.

## Criterios de Éxito

- [ ] `uv tool install sdd-tui && sdd-setup` completa el onboarding sin tocar GitHub
- [ ] `brew install sdd-tui && sdd-setup` funciona en macOS
- [ ] `sdd-setup --help` documenta todos los flags disponibles
- [ ] README tiene una sección clara por plataforma (macOS, Linux, Windows)
- [ ] Tests de `sdd-setup` cubren: detección de skills, instalación global/local, flags `--global`/`--local`/`--check`
