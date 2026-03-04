---
name: sdd-verify
description: SDD Verify - Final validation before PR. Run tests, quality checks, and self-review checklist. Usage - /sdd-verify or /sdd-verify {change-name}.
---

# SDD Verify

> Final validation before creating the PR. Tests + quality checks + self-review.

## Usage

```
/sdd-verify                # Verify active change
/sdd-verify {change-name}  # Verify specific change
```

## Prerequisites

- `/sdd-apply` completed (all tasks in tasks.md marked `[x]`)

## Step 1: Identify changed files

```bash
git diff --name-only main..HEAD    # or dev..HEAD depending on your base branch
```

## Step 2: Run tests

Run the project's full test suite:
```bash
# Use whatever your project uses:
pytest
npm test
go test ./...
./gradlew test
```

All tests must pass before proceeding.

## Step 3: Quality checks

Run linters and formatters on changed files:
```bash
# Examples:
ruff check src/
eslint src/
golangci-lint run
```

Fix any issues, re-run, and commit the fix atomically.

## Step 4: Self-review checklist

Review the changed code against these criteria:

### 1. Tests exist for new code
- [ ] New functions/methods have tests
- [ ] Edge cases are covered
- [ ] Error paths are tested

### 2. Input validated before processing
- [ ] Required fields checked
- [ ] Types/formats validated at system boundaries
- [ ] No raw user input passed to internal logic unvalidated

### 3. Methods are small and focused
- [ ] No method > 50 lines
- [ ] Nesting depth < 3 levels
- [ ] One responsibility per method

### 4. No hardcoded values
- [ ] Magic numbers extracted to constants
- [ ] Status/type strings use enums or constants
- [ ] No environment-specific values in source code

### 5. No code duplication
- [ ] Similar logic extracted to shared methods
- [ ] Consistent patterns with the existing codebase

### 6. Type hints / type safety
- [ ] All method parameters typed
- [ ] All return types declared
- [ ] Nullable types explicit

### 7. Null / None checks
- [ ] Results checked before use
- [ ] Optional parameters handled
- [ ] Exceptions raised for unexpected nulls

### 8. Spec compliance
- [ ] All spec cases covered
- [ ] Input/output contracts match
- [ ] Business rules implemented
- [ ] Error messages match spec

## Step 5: Smoke test (for UI/TUI projects)

If the project has a UI, run it manually and verify the changed behavior end-to-end.

If a bug is found during smoke test:
1. Document it as `BUGxx` in `tasks.md` before fixing
2. Fix and commit atomically
3. Re-run smoke test until it passes

## Step 6: Final report

```
VERIFY REPORT: {change-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests:    N/N PASS
Quality:  PASS
Self-review: ✓
Spec compliance: ✓

Status: READY FOR PR
```

## Next Step

All checks green → `/sdd-archive` to close the change + create PR.
