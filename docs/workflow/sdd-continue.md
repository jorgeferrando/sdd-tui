# sdd-continue

**Detect the next pending phase and run it automatically.** The "what's next?" command — you don't have to remember where you left off.

```
/sdd-continue                  # Active change (if only one exists)
/sdd-continue {change-name}    # Specific change
```

---

## How it works

`/sdd-continue` inspects the change directory and finds the first incomplete phase:

| Phase | Complete when |
|-------|---------------|
| propose | `proposal.md` exists |
| spec | `specs/*/spec.md` exists |
| design | `design.md` exists |
| tasks | `tasks.md` exists |
| apply | No `[ ]` remaining in `tasks.md` |
| verify | Apply done + clean git working tree |

It then announces the detected phase and runs the corresponding skill:

```
Detected phase: DESIGN
Change: csv-export
Running sdd-design...
```

---

## Mid-apply resume

If `tasks.md` has some tasks completed and some pending, `/sdd-continue` passes the next task ID to `/sdd-apply` automatically — no need to specify it manually.

---

## Multiple active changes

If more than one change exists in `openspec/changes/` (excluding `archive/`), the skill asks which one to continue. One active change at a time is recommended.

---

## All phases done

If every phase is complete, `/sdd-continue` tells you the change is ready to archive:

```
All phases complete for: csv-export
Next: /sdd-archive
```

---

## When to use it vs direct commands

Use `/sdd-continue` when you return to a change after a break and don't remember which phase you were in. Use the direct commands (`/sdd-apply`, `/sdd-verify`) when you know exactly where you are.
