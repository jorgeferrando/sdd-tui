# sdd-verify

**Final validation before creating the PR.** Runs tests, quality checks, and a self-review checklist.

```
/sdd-verify                # Verify the active change
/sdd-verify {change-name}  # Verify a specific change
```

---

## What it checks

### 1. Tests

Runs the full test suite using whatever your project uses:

```bash
pytest          # Python
npm test        # Node.js
go test ./...   # Go
./gradlew test  # JVM
```

All tests must pass before proceeding.

### 2. Quality checks

Runs linters and formatters on the changed files:

```bash
ruff check src/          # Python
eslint src/              # TypeScript/JavaScript
golangci-lint run        # Go
```

If checks fail, the skill fixes and commits atomically — the fix becomes part of the change history.

### 3. Self-review checklist

A structured review of the implementation against the spec:

- All `tasks.md` tasks marked `[x]`?
- Every requirement in `specs/*/spec.md` covered by at least one test?
- No debug code, no commented-out code?
- Error paths tested?
- Commit messages follow the project convention?
- No references to internal tooling, company names, or unrelated systems?

---

## Example output

When everything passes:

```
VERIFY REPORT: csv-export
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests:         42/42 PASS
Quality:       ruff PASS (0 errors)
Self-review:   10/10 ✓
Spec:          all requirements covered

Status: READY FOR PR
```

When issues are found:

```
VERIFY REPORT: csv-export — ISSUES FOUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests:         41/42 FAIL
  FAIL: test_csv_export_empty_table — AssertionError line 34

Self-review:
  PENDING: Error path not tested (empty dataset)
  PENDING: REQ-03 not covered by any test

Fixing issues before continuing...
```

The skill fixes and re-runs until the report is clean.

---

## Prerequisite

All tasks in `tasks.md` must be marked `[x]` before running verify. If the apply is partial, complete it first.

---

## After verify

Once all checks pass, the change is ready to merge. Create the PR and then run:

→ [`/sdd-archive`](sdd-archive.md)
