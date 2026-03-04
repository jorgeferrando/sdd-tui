---
name: sdd-continue
description: SDD Continue - Detect the next pending phase and execute it. Equivalent to "what's next?". Usage - /sdd-continue or /sdd-continue {change-name}.
---

# SDD Continue

> Automatically detect the next pending phase and execute the corresponding skill.

## Usage

```
/sdd-continue                  # Active change (only one in openspec/changes/)
/sdd-continue {change-name}    # Specific change
```

## Step 1: Identify the active change

```bash
ls openspec/changes/
```

- If `{change-name}` was provided: use that directory
- If exactly one change exists (excluding `archive/`): use that one
- If multiple: ask the user which one with `AskUserQuestion`

## Step 2: Detect pending phase

Read `openspec/changes/{change-name}/` and determine the first incomplete phase:

| Phase | DONE condition |
|-------|----------------|
| `propose` | `proposal.md` exists |
| `spec` | `specs/*/spec.md` — at least one file exists |
| `design` | `design.md` exists |
| `tasks` | `tasks.md` exists |
| `apply` | `tasks.md` has no `[ ]` remaining |
| `verify` | apply DONE + clean working tree (`git status --porcelain` empty) |

The **first NOT DONE phase** is the one to execute.

### Special cases

- `apply` in progress: if some `[x]` and some `[ ]` → continue apply from first `[ ]`
- `verify` pending only because of dirty git: inform user before running verify
- All phases DONE: inform → ready for `/sdd-archive`

## Step 3: Execute the skill

| Detected phase | Skill to run |
|---------------|--------------|
| `propose` | `sdd-propose` |
| `spec` | `sdd-spec` |
| `design` | `sdd-design` |
| `tasks` | `sdd-tasks` |
| `apply` | `sdd-apply` (with next task ID if partial) |
| `verify` | `sdd-verify` |
| all DONE | Inform → `/sdd-archive` |

Always announce what phase is being executed:

```
Detected phase: DESIGN
Change: {change-name}
Running sdd-design...
```

## Notes

- Never skip phases — if `design.md` is missing, don't run `sdd-tasks` even if proposal and spec exist
- If `tasks.md` has partial completions, pass the next task ID to `sdd-apply` (e.g. `T03`, `BUG01`)
