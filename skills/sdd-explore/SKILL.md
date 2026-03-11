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
- **Specs** — check `openspec/INDEX.md` first (if it exists) to identify relevant domains,
  then load only those spec files from `openspec/specs/`

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

OpenSpec Index (if present):
  - openspec/INDEX.md → identified domains: {domain1}, {domain2}
  - Loaded specs: openspec/specs/{domain}/spec.md

Key constraints:
  - {anything that affects the design}
```

## OpenSpec Index Lookup

If `openspec/INDEX.md` exists, read it **before** loading any individual spec file:
1. Match the change description / ticket keywords against the `**Keywords:**` field of each entry
2. Load only the 1-3 most relevant domain spec files
3. If no clear match, load the most likely domain + `core`
4. If `openspec/INDEX.md` does not exist, scan `openspec/specs/` directly (fallback)

## Notes

- This is a read-only phase — no code changes
- Keep exploration focused; stop when you have enough context to propose
