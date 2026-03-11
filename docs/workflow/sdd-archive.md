# sdd-archive

**Close the change cycle.** Move the change to the archive and merge its specs into the canonical ones.

```
/sdd-archive                   # Archive the active change
/sdd-archive {change-name}     # Archive a specific change
```

---

## Prerequisites

- All tasks in `tasks.md` marked `[x]`
- `/sdd-verify` passed
- PR created (or commits merged to main)

---

## What it does

### 1. Verify state

Confirms that every task is complete and verify has run.

### 2. Update canonical specs

Each change has **delta specs** in `openspec/changes/{change}/specs/`. These describe only what changed. Archive merges them into the canonical specs in `openspec/specs/`:

```
Before:
  openspec/specs/reports/spec.md   ← v1.0, no CSV mention

After:
  openspec/specs/reports/spec.md   ← v2.0, CSV export requirements merged in
```

If no canonical spec exists for a domain yet, it's created from the delta.

### 3. Move to archive

```
openspec/changes/csv-export/
    → openspec/changes/archive/2024-03-11-csv-export/
```

The archive is permanent and ordered chronologically. Every proposal, design decision, and task is preserved.

### 4. Update CHANGELOG

Adds an entry to `CHANGELOG.md` for the change.

---

## The archive as project history

The archive answers questions like:

- *Why does the export default to UTF-8?* → `archive/2024-03-11-csv-export/design.md`
- *When was authentication added?* → `ls openspec/changes/archive/`
- *What requirements drove the rate limiter?* → `archive/.../specs/api/spec.md`

This is the compounding value of SDD: every future change is informed by the documented decisions of all past changes.

---

## After archive

The change is closed. Start the next one:

→ [`/sdd-new`](sdd-new.md)
