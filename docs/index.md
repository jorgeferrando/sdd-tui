# sdd-tui

**sdd-tui** is a terminal UI for managing the [Spec-Driven Development (SDD)](https://github.com/jorgeferrando/sdd-tui) workflow without leaving your editor. It visualizes the pipeline state of every change, lets you browse specs, diffs, and documentation with a few keystrokes, and integrates with Git and GitHub so you always know what to work on next. It pairs with the `/sdd-*` Claude Code skills for a fully AI-assisted development loop.

---

## Quick Start

**macOS (Homebrew)**

```bash
brew tap jorgeferrando/sdd-tui
brew install sdd-tui
sdd-setup --global
```

**Linux / Windows**

```bash
# Linux
curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/Install-SddTui.ps1 | iex
```

**First run**

```bash
cd your-project
sdd-tui          # Opens the TUI — press ? for keybindings
```

Initialize SDD in an existing project:

```
/sdd-init        # Inside Claude Code — bootstraps openspec/ and loads steering
```
