# Scope Control

The most common SDD mistake is making a change too large. Large changes are hard to review, risky to merge, and slow to archive. Scope control is the discipline of keeping changes small and independently valuable.

---

## The 20-file rule

| File count | Action |
|------------|--------|
| < 10 files | Ideal — proceed |
| 10–20 files | Evaluate — split if there's a logical seam |
| > 20 files | Mandatory split |

This rule applies to *code files*. Documentation-only changes (Markdown, config) are more lenient since the review risk is lower.

---

## How to split a change

A good split produces two changes that each have **independent business value** — not "part 1" and "part 2".

**Bad split** (no independent value):

```
payment-integration-part1  ← models + repository
payment-integration-part2  ← handler + controller
```

Part 1 is useless without part 2. If part 1 merges and part 2 is delayed, the codebase is broken.

**Good split** (independent value):

```
payment-read-only    ← display payment status in UI (no mutation)
payment-create       ← create payment via form (adds mutation)
```

Either change can ship independently and provide value.

---

## Common seams for splitting

| Seam | Example |
|------|---------|
| Read vs write | List/show before create/update/delete |
| Domain vs UI | Backend endpoint before frontend integration |
| Core vs edge cases | Happy path before error handling |
| Migration vs feature | Schema change before the feature that uses it |
| Config vs behavior | Feature flag before the flagged feature |

---

## Detecting scope creep during apply

If `/sdd-apply` touches more files than `tasks.md` planned, stop. Options:

1. **The extra file is necessary** → add a `MEJxx` task in `tasks.md` before touching it
2. **The extra file is a new change** → pause, archive current progress, start a new change for it
3. **The design was wrong** → update `design.md` and `tasks.md` before continuing

Never implement something that isn't in `tasks.md`. The task list is the contract.

---

## Why small changes compound

- Each archived change updates the canonical spec — future changes inherit accurate context
- Small commits are independently revertible
- Reviewers can give focused feedback
- Velocity metrics become meaningful (you can see actual throughput, not just big batch releases)
