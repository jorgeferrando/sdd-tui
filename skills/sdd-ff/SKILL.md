---
name: sdd-ff
description: SDD Fast-Forward - Run propose + spec + design + tasks without pauses. For when the scope is clear and you want to generate all documentation in one pass. Usage - /sdd-ff "description" or /sdd-ff TICKET-123.
---

# SDD Fast-Forward

> Generate complete change documentation in one pass: propose → spec → design → tasks. No pauses between phases.

## Usage

```
/sdd-ff "description"   # Fast-forward from a description
/sdd-ff TICKET-123      # Fast-forward from a ticket
```

Use when the scope is clear and no approval is needed between phases.
For complex or uncertain changes, use `/sdd-new` + `/sdd-continue` with pauses.

## Prerequisites

- `openspec/` initialized (`/sdd-init`)

## Sequence (no pauses)

### 1 — Explore

Quick codebase exploration:
- Existing similar patterns
- Files that will be affected
- Related canonical specs in `openspec/specs/`

### 2 — Propose

Create `openspec/changes/{change-name}/proposal.md`:
- Problem description
- Proposed solution and discarded alternatives
- Estimated impact (files, domains, tests)

### 3 — Spec

Create `openspec/changes/{change-name}/specs/{domain}/spec.md`:
- Expected behavior (given/when/then)
- Alternative cases and edge cases
- Business rules

### 4 — Design

Create `openspec/changes/{change-name}/design.md`:
- Technical architecture and files to create/modify
- Implementation detail per file
- Design decisions with alternatives

### 5 — Tasks

Create `openspec/changes/{change-name}/tasks.md`:
- Ordered list of atomic tasks
- Commit hint per task
- Dependencies between tasks

## When done

Show summary and confirm:

```
FF COMPLETE: {change-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
proposal.md  ✓
spec.md      ✓  ({domain})
design.md    ✓  ({N} files)
tasks.md     ✓  ({N} tasks)

Next: /sdd-apply to implement
```

If during the ff an ambiguity requires a user decision → pause, ask with `AskUserQuestion`, then continue.

## Next Step

With complete documentation → `/sdd-apply` to implement task by task.
