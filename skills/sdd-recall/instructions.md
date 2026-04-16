---
name: sdd-recall
description: SDD Recall - Search archived specs and past decisions for context relevant to the current problem. Usage - /sdd-recall "query" or /sdd-recall {domain}.
requires: ["openspec/specs/"]
produces: []
---

# SDD Recall

> Search archived specs, canonical specs, and past design decisions for context relevant to a new change.

## Usage

```
/sdd-recall "authentication middleware"   # Search by topic
/sdd-recall api                           # Search by domain
/sdd-recall                               # Show all domains with summaries
```

## Prerequisites

- `openspec/` initialized (`/sdd-init`)
- At least one archived change or canonical spec exists

## Step 1: Build search corpus

Scan these locations (in order of relevance):

1. **`openspec/INDEX.md`** — if it exists, use it as the primary lookup. Match the query against domain names, summaries, entities, and keywords.
2. **`openspec/specs/*/spec.md`** — canonical specs (current truth)
3. **`openspec/changes/archive/*/`** — archived changes (historical decisions)
   - `proposal.md` — problem context and alternatives
   - `design.md` — technical decisions and rationale
   - `specs/*/spec.md` — delta specs with business rules

If none of these exist, inform the user:
```
No specs or archived changes found.
Run /sdd-init and complete at least one change cycle to build project memory.
```

## Step 2: Search and rank

Match the query against:
- Domain names and spec titles
- Problem descriptions in proposals
- Decision tables in designs (the "Alternative discarded" columns are especially valuable)
- Business rules (BR-xx entries)
- Entity and keyword fields in INDEX.md

Rank results by relevance. Prefer:
1. Exact domain match
2. Canonical spec match (current truth > archived delta)
3. Design decisions that explain *why* something was built a certain way
4. Proposals that describe similar problems

## Step 3: Present results

Show a concise summary grouped by source:

```
RECALL: "authentication middleware"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Canonical specs:
  openspec/specs/auth/spec.md
    - BR-01: Sessions expire after 24h of inactivity
    - BR-02: Refresh tokens are single-use

Archived decisions:
  openspec/changes/archive/2026-03-10-add-auth/design.md
    - Chose JWT over session cookies — stateless, no server-side storage
    - Discarded OAuth2 for v1 — too complex for current scope

  openspec/changes/archive/2026-03-10-add-auth/proposal.md
    - Original problem: needed auth for public API endpoints
    - Out of scope: admin roles (deferred to separate change)

Related domains:
  openspec/specs/api/spec.md — references auth middleware in request flow
```

## Step 4: Suggest how to use the context

Based on what was found, suggest how this context applies to the current work:

```
Suggestions:
  - The auth domain already has conventions for token handling — follow them
  - The original design explicitly deferred admin roles — if your change
    needs them, start a new spec rather than modifying the archived one
  - The API spec references auth middleware at the routing layer —
    check if your change affects that integration point
```

## Notes

- This is a **read-only** skill — it never modifies files
- Results are informational — the user decides what to apply
- If the query is broad and returns too many matches, ask the user to narrow it
- For domains with large specs, show only the relevant sections, not the full file

## Next Step

With relevant context found → use it to inform `/sdd-new`, `/sdd-propose`, or `/sdd-design`.
