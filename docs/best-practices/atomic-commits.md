# Atomic Commits

One task = one file = one commit. This is the core discipline of `/sdd-apply`.

---

## What "atomic" means

An atomic commit:

- Touches exactly **one file**
- Represents exactly **one task** from `tasks.md`
- Has a commit message that references the change: `[change-name] Description`
- Is **independently revertible** — `git reset HEAD~1` undoes exactly one logical unit

---

## Why one file per commit

**Reviewability:** A reviewer can look at a single commit and understand exactly what changed and why, without context from other commits.

**Revertibility:** If task T03 introduced a bug, `git reset HEAD~3` (or interactive rebase) removes only that task. With multi-file commits, reverting one problem forces reverting everything else too.

**Traceability:** Each commit in `git log` maps 1:1 to a task in `tasks.md`. The history is the implementation timeline.

---

## Good vs bad commits

**Bad — multiple files, vague message:**
```
abc1234  Add payment feature
  src/payments/model.py
  src/payments/repository.py
  src/payments/handler.py
  tests/test_payments.py
```

**Good — one file, clear message:**
```
abc1234  [payments] Add Payment dataclass to models
  src/payments/model.py

def5678  [payments] Add PaymentRepository with SQLite backend
  src/payments/repository.py

ghi9012  [payments] Add CreatePaymentHandler
  src/payments/handler.py

jkl3456  [payments] Add unit tests for CreatePaymentHandler
  tests/test_payments.py
```

---

## Staging with care

`/sdd-apply` stages files explicitly (`git add {specific-file}`) — never `git add .` or `git add -A`. This prevents accidentally committing unrelated changes, debug artifacts, or local config files.

---

## Commit message format

```
[change-name] Verb noun in imperative mood
```

Examples:

```
[csv-export] Add ExportFormat enum to models
[csv-export] Implement CSV serializer
[csv-export] Wire export endpoint to serializer
[csv-export] Add unit tests for CSV serializer
```

The `[change-name]` prefix makes it trivial to `git log --grep='\[csv-export\]'` and see only the commits for that change.

---

## Handling exceptions

Sometimes a task genuinely touches two files (e.g., adding a function and updating its import in `__init__.py`). In this case:

1. Note it in the task: `T03  src/models.py + src/__init__.py — add Payment + re-export`
2. Stage both files in the same commit
3. Keep this rare — if it happens often, the task decomposition is too coarse
