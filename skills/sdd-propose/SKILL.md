---
name: sdd-propose
description: SDD Propose - Create proposal.md for a new change. Documents the problem, proposed solution, alternatives, and estimated impact. Usage - /sdd-propose "description" or as part of /sdd-new.
---

# SDD Propose

> Create `proposal.md` for a change. The proposal defines the problem and solution before any code is written.

## Usage

```
/sdd-propose "description"   # Create proposal from description
/sdd-propose TICKET-123      # Create proposal from ticket
```

## Prerequisites

- `openspec/` initialized (`/sdd-init`)
- Codebase exploration done (or run `sdd-explore` first)

## Step 1: Determine change name

If not already created, choose a short kebab-case name and create the directory:
```bash
mkdir -p openspec/changes/{change-name}
```

## Step 2: Create proposal.md

Create `openspec/changes/{change-name}/proposal.md`:

```markdown
# Proposal: {Title}

## Metadata
- **Change:** {change-name}
- **Ticket:** {TICKET-ID or N/A}
- **Date:** {YYYY-MM-DD}

## Problem

{What is wrong or missing. Why does this need to change.}

## Proposed Solution

{How to solve it. Keep it high-level — implementation details go in design.md.}

## Alternatives Discarded

| Alternative | Reason discarded |
|-------------|-----------------|
| {option} | {why not} |

## Impact

- **Files affected:** {estimate}
- **Domains:** {list}
- **Tests:** {what needs testing}
```

## Step 3: Present to user

Show the proposal. Ask:
- Does the problem description match the intent?
- Is the proposed solution correct?
- Any alternatives worth considering?

Apply feedback before proceeding.

## Next Step

With `proposal.md` approved → `/sdd-continue` (runs `sdd-spec`).
