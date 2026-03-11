# sdd-apply

**Implement the change task by task.** Each task becomes exactly one commit.

```
/sdd-apply                   # Implement the active change
/sdd-apply {change-name}     # Implement a specific change
/sdd-apply T03               # Resume from a specific task
```

---

## The discipline: one task = one file = one commit

`sdd-apply` enforces atomic commits. For each task in `tasks.md`:

1. Implements the file
2. Runs quality checks (linter, formatter)
3. Commits with the message from the task

```
T01 ✓  [csv-export] Add ExportFormat enum to models
T02 ✓  [csv-export] Add CSV serializer class
T03 ✓  [csv-export] Wire export endpoint to serializer
T04 ✓  [csv-export] Add unit tests for CSV serializer
```

Each commit is independently reviewable and revertible.

---

## Prerequisites

Before running `/sdd-apply`:

- `tasks.md` exists and is approved
- `openspec/steering/conventions.md` exists (run `/sdd-init` first if missing)
- The correct git branch is active

The skill reads `conventions.md` silently at the start to apply your project's rules throughout the implementation.

---

## Resuming a partial apply

If you stopped mid-way, run `/sdd-apply T03` to resume from task T03. The skill reads the `[x]` marks in `tasks.md` and skips already-completed tasks automatically.

---

## Changes requested mid-apply

If you ask for a change, fix, or improvement that isn't in `tasks.md`, the skill **registers it first** before touching any code:

```markdown
## Bugs post-T02

- [ ] BUG01  src/serializer.py — error message doesn't mention the flag name
  - Commit: [csv-export] Fix error message to include flag name
```

Then it implements and commits it. No change is made without a record in `tasks.md`. This keeps the timeline complete.

---

## Unexpected situations

If something in the codebase differs from the design, the skill stops and asks — it doesn't make unilateral architectural decisions. The options are:

1. Proceed with an adjustment (documented in `design.md`)
2. Update the design and tasks before continuing
3. Pause and revisit

---

## Commands

| Command | Effect |
|---------|--------|
| `continue` | Proceed to the next task without confirmation |
| `pause` | Stop after the current task |
| `skip` | Mark the current task as skipped, proceed |
| `status` | Show progress summary |

---

## Next step

→ [`/sdd-verify`](sdd-verify.md) when all tasks are marked `[x]`
