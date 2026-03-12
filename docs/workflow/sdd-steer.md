# sdd-steer

**Generate and synchronize the steering files in `openspec/steering/`.** Steering files are the persistent memory of the project — the conventions and rules that Claude applies during every `sdd-apply`.

```
/sdd-steer          # Bootstrap: generate all steering files from scratch
/sdd-steer sync     # Sync: detect drift and propose updates
```

---

## What are steering files?

Steering files capture the **invisible knowledge** about your project that lives in senior developers' heads:

- Naming conventions that the linter doesn't catch
- Layer boundaries that aren't enforced by the build
- Anti-patterns discovered after painful PRs
- Architectural decisions and why they were made

Without steering files, Claude generates technically correct code that still gets rejected in review — because it doesn't match your team's actual standards.

---

## The files

| File | Contains |
|------|---------|
| `product.md` | What the product does, for whom, and the business context |
| `tech.md` | Tech stack, versions, key libraries, toolchain |
| `structure.md` | Codebase layout, which directories contain what |
| `conventions.md` | Naming rules, patterns, anti-patterns |
| `project-rules.md` | Explicit rules Claude must follow during implementation |

---

## Bootstrap vs sync

**Bootstrap** (`/sdd-steer`): Run once after `/sdd-init`, or when starting SDD on an existing project. Explores the codebase and generates all files from scratch.

**Sync** (`/sdd-steer sync`): Run periodically when the project evolves. Detects drift between what the steering files say and what the codebase actually does, then proposes targeted updates.

---

## Example: conventions.md

Here's what a real `conventions.md` looks like for a Python FastAPI project:

```markdown
# Conventions

## Naming

- MUST: Use `snake_case` for all Python identifiers (functions, variables, modules)
- MUST NOT: Use abbreviations in variable names — `user_id` not `uid`, `request` not `req`
- MUST: Prefix internal-only helpers with underscore (`_build_query`, `_parse_date`)
- SHOULD: Name test functions `test_{what}_{scenario}` — e.g., `test_create_user_duplicate_email`

## Architecture

- MUST: Never import from `tui/` in `core/` — dependency flows one way (core → tui)
- MUST: All git subprocess calls go through `GitReader` — never call `subprocess` directly in tui/
- MUST NOT: Catch bare `Exception` — catch the specific exception type
- SHOULD: Keep functions under 30 lines; extract helpers if longer

## Testing

- MUST: Every public function in `core/` has at least one test
- MUST: Mock external I/O (git, filesystem) in unit tests — no real subprocess calls
- MUST NOT: Use `sleep()` in tests — use fixtures or `call_after_refresh`

## Commits

- MUST: Format: `[change-name] Short description in English`
- MUST: One file per commit — no multi-file commits except `__init__.py` additions
- MUST NOT: Include "WIP", "fix", or "temp" in commit messages
```

This file is what `/sdd-apply` reads silently before implementing anything. Every rule here prevents a class of PR review comment.

---

## Example: sync output

After three months of development, `/sdd-steer sync` might report:

```
Analyzing drift between steering and codebase...

DRIFT DETECTED: conventions.md

  Line 12: "MUST: Keep functions under 30 lines"
  → Found 8 functions between 30–50 lines in src/core/ added since last sync
  → Suggest updating to: "SHOULD: Keep functions under 40 lines"

  Missing rule (detected pattern):
  → All new dataclasses use @dataclass(frozen=True) — add as convention?

Proposed change (confirm to apply):
  [1] Update line-length threshold: 30 → 40 lines (SHOULD)
  [2] Add: "SHOULD: Prefer @dataclass(frozen=True) for value objects"
> 1, 2

conventions.md updated ✓
```

Sync proposes — you decide. It never auto-modifies your steering.

---

## When to update steering

- After a significant refactor changes naming or structure
- After a sprint retrospective surfaces recurring review issues
- When a new major dependency is added
- When a new architectural pattern is established

Good steering files evolve with the project. Stale steering is worse than no steering — it generates confidently wrong code.

---

## Next step

Once steering files are in place, start your first change:

→ [`/sdd-new`](sdd-new.md)
