# sdd-tui

**sdd-tui** is a terminal UI for Spec-Driven Development — it gives you a live view of your `openspec/` directory: active changes, pipeline status, spec health, git diffs, PR checks, and team velocity, all from the keyboard. It pairs with a set of Claude Code skills (`/sdd-init`, `/sdd-discover`, `/sdd-apply`, etc.) that automate the spec → design → implement → archive workflow.

---

## Quick Start

**Via Homebrew (macOS/Linux):**

```bash
brew tap jorgeferrando/sdd-tui
brew install sdd-tui
```

**Via pip/pipx:**

```bash
pipx install sdd-tui
```

**First use:**

```bash
# 1. Go to any project directory
cd ~/my-project

# 2. Bootstrap openspec/ and install SDD skills into Claude Code
sdd-setup --global    # installs skills to ~/.claude/skills/

# 3. Open the TUI
sdd-tui

# 4. If the project already has code, generate initial specs
/sdd-discover         # in Claude Code — analyzes codebase and generates openspec/specs/
```
