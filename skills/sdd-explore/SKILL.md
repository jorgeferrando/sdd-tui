---
name: sdd-explore
description: SDD Explore - Read-only codebase exploration to understand context before proposing changes. Used as part of /sdd-new or /sdd-continue. Usage - /sdd-explore "what to look for".
---

# SDD Explore

> Read-only exploration of the codebase to understand context before proposing changes.

## Usage

```
/sdd-explore "what to look for"
/sdd-explore                     # General exploration for the active change
```

## What to look for

- **Similar patterns** — existing implementations of the same type of change
- **Affected files** — what will need to change and why
- **Domain models** — data structures, interfaces, contracts involved
- **Tests** — how existing tests are structured for similar code
- **Specs** — check `openspec/specs/` for canonical domain specs

## Output

A concise summary of findings:

```
EXPLORE COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Relevant files:
  - src/...   (reason)
  - src/...   (reason)

Existing patterns:
  - Pattern X used in Y — can follow the same approach

Canonical specs:
  - openspec/specs/{domain}/spec.md — covers Z behavior

Key constraints:
  - {anything that affects the design}
```

## Notes

- This is a read-only phase — no code changes
- Keep exploration focused; stop when you have enough context to propose
