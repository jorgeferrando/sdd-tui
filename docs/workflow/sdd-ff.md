# sdd-ff

**Fast-forward.** Generate proposal + spec + design + tasks in one pass, without pausing between phases.

```
/sdd-ff "description"   # Fast-forward from a description
/sdd-ff TICKET-123      # Fast-forward from a ticket
```

---

## When to use it

Use `/sdd-ff` when:

- The scope is well understood before you start
- You don't need to review and approve each artifact individually
- You want the full documentation ready before touching any code

Use [`/sdd-new`](sdd-new.md) + [`/sdd-continue`](sdd-continue.md) instead when:

- The change is complex or uncertain
- You want to validate the proposal before writing the spec
- The design requires decisions that need user input

---

## What it produces

Four artifacts in `openspec/changes/{change-name}/`:

```
openspec/changes/csv-export/
├── proposal.md       ← problem + solution + alternatives
├── specs/
│   └── reports/
│       └── spec.md   ← behavior requirements (EARS format)
├── design.md         ← files to create/modify + technical decisions
└── tasks.md          ← ordered atomic task list
```

---

## Pauses during fast-forward

Even in fast-forward mode, if an ambiguity requires a decision, the skill pauses and asks before continuing. You won't get a silently broken design.

At the end, a summary is shown:

```
FF COMPLETE: csv-export
━━━━━━━━━━━━━━━━━━━━━━━━━━━
proposal.md  ✓
spec.md      ✓  (reports)
design.md    ✓  (6 files)
tasks.md     ✓  (6 tasks)

Next: /sdd-apply
```

---

## Next step

→ [`/sdd-apply`](sdd-apply.md) to implement task by task.
