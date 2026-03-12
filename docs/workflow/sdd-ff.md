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

---

## Real example

```
/sdd-ff "add CSV export to the report dashboard"
```

**Phase 1 — Explore:**
```
Reading openspec/specs/reports/spec.md...
Reading src/reports/views.py, src/reports/models.py...
No existing export mechanism found. Will create from scratch.
```

**Phase 2 — Proposal:** (created in ~30 seconds)
```markdown
# Proposal: csv-export

## Description
Add a "Download CSV" button to the report dashboard that exports
the currently displayed rows.

## Motivation
Users screenshot tables to paste into spreadsheets.

## Alternatives considered
- Excel (.xlsx): requires openpyxl, heavier
- PDF: not machine-readable

## Estimated impact
~5 files, 1 domain (reports)
```

**Phase 3 — Spec:**
```markdown
REQ-01 [Event] When the user clicks "Download CSV", the system SHALL
       generate a CSV file containing all currently visible rows.

REQ-02 [Ubiquitous] Column headers in the CSV SHALL match the table headers.

REQ-03 [Unwanted] If the table is empty, the system SHALL export a header-only
       CSV and notify the user.
```

**Phase 4 — Design:**
> One decision point: "Should the CSV be generated server-side or client-side?"
> → Paused and asked. Answer: server-side.

**Phase 5 — Tasks:**
```
- [ ] T01  src/reports/serializers.py  — CsvExporter class
- [ ] T02  src/reports/views.py        — add export endpoint
- [ ] T03  src/reports/templates/      — add Download CSV button
- [ ] T04  tests/test_csv_export.py    — unit tests for CsvExporter
```

**Summary:**
```
FF COMPLETE: csv-export
━━━━━━━━━━━━━━━━━━━━━━━━━━━
proposal.md  ✓
spec.md      ✓  (reports — 3 REQs)
design.md    ✓  (4 files)
tasks.md     ✓  (4 tasks)

Next: /sdd-apply
```

Total time from command to tasks-ready: ~3 minutes.

---

## Next step

→ [`/sdd-apply`](sdd-apply.md) to implement task by task.
