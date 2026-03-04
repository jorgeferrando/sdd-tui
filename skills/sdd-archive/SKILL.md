---
name: sdd-archive
description: SDD Archive - Close the change cycle. Move the change to the archive and update canonical specs. Usage - /sdd-archive or /sdd-archive {change-name}.
---

# SDD Archive

> Close the SDD cycle. Move the change to the archive and merge specs into the canonical ones.

## Usage

```
/sdd-archive                   # Archive active change
/sdd-archive {change-name}     # Archive specific change
```

## Prerequisites

- `/sdd-verify` completed (all checks green)
- PR created

## Step 1: Verify state

Before archiving, confirm:
1. All tasks in `tasks.md` marked `[x]`
2. `/sdd-verify` passed
3. PR created

```bash
# Should return 0
grep -c "\[ \]" openspec/changes/{change-name}/tasks.md
```

## Step 2: Update canonical specs

The change specs (`openspec/changes/{change}/specs/`) contain **deltas**.
Now merge them into the canonical specs (`openspec/specs/`).

For each `openspec/changes/{change}/specs/{domain}/spec.md`:
1. Read the current canonical spec at `openspec/specs/{domain}/spec.md`
2. Read the change delta
3. Merge: update the canonical with new behaviors, rules, decisions
4. Update the canonical metadata (version, date)

If no canonical spec exists for the domain, create it:
```bash
mkdir -p openspec/specs/{domain}
cp openspec/changes/{change}/specs/{domain}/spec.md openspec/specs/{domain}/spec.md
```

## Step 3: Move to archive

```bash
DATE=$(date +%Y-%m-%d)
CHANGE={change-name}
mv "openspec/changes/${CHANGE}" "openspec/changes/archive/${DATE}-${CHANGE}"
```

## Step 4: Verify post-archive structure

```bash
ls openspec/changes/          # change should be gone from active
ls openspec/changes/archive/  # change should appear here
ls openspec/specs/            # canonical specs updated
```

## Step 5: Summary

```
ARCHIVE COMPLETE: {change-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archived at:
  openspec/changes/archive/{date}-{change-name}/

Canonical specs updated:
  openspec/specs/{domain}/spec.md ✓

Active changes remaining: N
```

## Bugs found after archive

If a bug is discovered after archiving:

1. Document it in the archived `tasks.md` under `## Bugs post-archive`
2. Implement the fix and commit
3. Mark `[x]` with the commit message

```markdown
## Bugs post-archive

- [x] **BUG01** `path/file` — short symptom description
  - Found: {context}
  - Fix: {description}
  - Commit: `{commit message}`
```

## Notes

- `openspec/` is local by default — never committed (unless the project opts in)
- The archive is historical context for future changes in the same domain
