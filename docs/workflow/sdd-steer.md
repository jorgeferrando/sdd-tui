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
