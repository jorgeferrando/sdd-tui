# Install

SDD has two components to install: the **sdd-tui** terminal app and the **SDD skills** for Claude Code. `sdd-setup` handles both.

---

## macOS

=== "Homebrew (recommended)"

    ```bash
    brew tap jorgeferrando/sdd-tui
    brew install sdd-tui
    sdd-setup
    ```

=== "uv"

    ```bash
    uv tool install git+https://github.com/jorgeferrando/sdd-tui
    sdd-setup
    ```

---

## Linux

=== "One-liner"

    Detects `uv`, `pipx`, or `pip` automatically:

    ```bash
    curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install.sh | bash
    ```

=== "uv"

    ```bash
    uv tool install git+https://github.com/jorgeferrando/sdd-tui
    sdd-setup
    ```

---

## Windows

=== "PowerShell 5.1+"

    ```powershell
    irm https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/Install-SddTui.ps1 | iex
    ```

=== "uv"

    ```powershell
    uv tool install git+https://github.com/jorgeferrando/sdd-tui
    sdd-setup
    ```

---

## What `sdd-setup` does

`sdd-setup` downloads the SDD skills from GitHub and installs them into Claude Code's skills directory.

```bash
sdd-setup            # install globally (default)
sdd-setup --global   # install into ~/.claude/skills/  (all projects)
sdd-setup --local    # install into .claude/skills/    (current project only)
sdd-setup --check    # show installed version and skill state
```

Skills are independent of the TUI version — you can update them at any time by running `sdd-setup` again.

After installing, **restart Claude Code**. The `/sdd-*` commands will be available in any project.

---

## Prerequisites

**sdd-tui** requires:

- Python 3.11+
- A terminal with [Unicode support](https://textual.textualize.io/FAQ/#how-do-i-fix-incorrectly-rendered-characters) (any modern terminal works)
- `git` accessible in `PATH`

**SDD skills** require:

- [Claude Code](https://claude.ai/code) installed and authenticated
- A project with a `openspec/` directory (created by `/sdd-init`)

---

## Serve the docs locally

If you want to browse this site locally:

```bash
pip install "sdd-tui[docs]"
mkdocs serve
```

---

## Next step

→ [Walk through your first change](first-change.md)
