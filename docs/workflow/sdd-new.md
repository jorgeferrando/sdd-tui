# sdd-new

**Start a new change.** Explores the codebase and creates the proposal.

```
/sdd-new "description"   # Start from a description
/sdd-new TICKET-123      # Start from a ticket ID
```

---

## What it does

`/sdd-new` combines two steps in one command:

1. **Explore** — reads the relevant parts of the codebase to understand context: existing patterns, files that will be affected, related canonical specs in `openspec/specs/`
2. **Propose** — creates `openspec/changes/{change-name}/proposal.md` with the problem, proposed solution, discarded alternatives, and estimated impact

---

## Output

```
openspec/changes/my-feature/
└── proposal.md
```

**Example proposal:**

```markdown
# Proposal: csv-export

## Description
Add CSV export to the report dashboard.

## Motivation
Users currently screenshot the table. They need a machine-readable format
for further processing in spreadsheets.

## Alternatives considered
- PDF export: heavier, no machine-readable value
- Excel (.xlsx): requires an additional dependency

## Success criteria
- [ ] Export button appears in the report header
- [ ] Downloaded file contains all visible rows
- [ ] Column headers match table headers
```

---

## Naming

The change name is derived automatically from the description in kebab-case:

| Input | Change name |
|-------|-------------|
| `"add CSV export"` | `csv-export` |
| `TICKET-42` | `ticket-42-csv-export` |

The name is used as the directory and as the prefix for all commits: `[csv-export] Add export button`.

---

## When to use `/sdd-ff` instead

If the scope is already clear and you don't need to review intermediate artifacts, use [`/sdd-ff`](sdd-ff.md) to generate proposal + spec + design + tasks in a single pass.

---

## Next step

After reviewing the proposal → [`/sdd-continue`](sdd-continue.md) to move to the spec phase.
