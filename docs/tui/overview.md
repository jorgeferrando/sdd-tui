# TUI Overview

sdd-tui is a terminal UI that visualizes the state of your `openspec/` in real time. It's a companion to the SDD skills — not a replacement.

```bash
# Run from any directory containing openspec/
sdd-tui

# Or with an explicit path
sdd-tui /path/to/openspec
```

---

## What it does

sdd-tui gives you a navigable view of everything in `openspec/` without switching between files manually:

- **Changes list** — see all active and archived changes at a glance, with their pipeline phase and progress
- **Change detail** — inspect proposal, spec, design, tasks, and diffs for any change
- **Spec health** — track which changes have complete specs (requirements, artifacts, test coverage)
- **Decisions timeline** — browse all architectural decisions across all changes
- **Spec evolution** — diff what changed in a domain across multiple changes
- **Git log** — see commits, working tree status, and branch info
- **Progress dashboard** — overall project progress across all changes
- **Velocity metrics** — throughput and cycle time per change

---

## Skills vs TUI

| Task | Skills (Claude Code) | sdd-tui |
|------|---------------------|---------|
| Write proposal | ✓ `/sdd-new` | — |
| Implement code | ✓ `/sdd-apply` | — |
| Read a spec | — | ✓ `s` in change detail |
| Check pipeline status | — | ✓ EpicsView |
| Browse diffs | — | ✓ `d` in change detail |
| See all decisions | — | ✓ `X` in EpicsView |
| Copy next SDD command | — | ✓ `Space` in change detail |

The skills *create* the content. The TUI *reads and navigates* it.

---

## Multi-project support

sdd-tui can monitor multiple projects simultaneously from a single instance. Configure them in `openspec/config.yaml`:

```yaml
projects:
  - name: frontend
    path: /path/to/frontend/openspec
  - name: backend
    path: /path/to/backend/openspec
```

EpicsView shows all projects with visual separators, and all views work across project boundaries.

---

## Requirements

- Python 3.11+
- Any modern terminal with Unicode support
- `git` in PATH
- `gh` CLI (optional — for PR/CI status panels)

---

## Navigation model

sdd-tui uses a **stack-based navigation**: each screen is pushed onto a stack, and `Esc` pops back to the previous screen. There's no global back button — just `Esc` from anywhere.

Press `?` on any screen to open the full keybindings reference for that context.

→ [Full keybindings reference](keybindings.md)
→ [All screens described](views.md)
