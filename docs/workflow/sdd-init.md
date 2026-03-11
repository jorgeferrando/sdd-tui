# sdd-init

**Bootstrap `openspec/` with guided onboarding.** Run this once at the start of a project to set up the directory structure and generate the steering files that feed the rest of the workflow.

```
/sdd-init
```

Safe to re-run — if steering already exists, it shows the current state instead of overwriting.

---

## What it does

1. Checks that the SDD skills are installed
2. Creates `openspec/` directory structure
3. Runs a guided Q&A about your project (tech stack, conventions, deployment)
4. Generates **steering files** in `openspec/steering/`

---

## Output

```
openspec/
├── config.yaml
├── specs/                    ← empty — populated by future changes
├── changes/
│   └── archive/
└── steering/
    ├── product.md            ← what the product does and for whom
    ├── tech.md               ← stack, versions, toolchain
    ├── structure.md          ← codebase layout
    ├── conventions.md        ← naming, patterns, anti-patterns
    └── project-rules.md      ← rules Claude uses during sdd-apply
```

Steering files are the **persistent memory** of the project. They capture the invisible conventions that cause PR rejections — naming rules, layer boundaries, anti-patterns — so Claude applies them consistently across every change.

---

## When to re-run

Run `/sdd-init` again (or `/sdd-steer sync`) when:

- The tech stack changes significantly
- New conventions are established after a sprint
- A new contributor joins and the steering feels outdated

---

## Should I commit `openspec/`?

**Yes, always.** `openspec/` is living documentation — not a temporary artifact. It should be versioned alongside your code so the full history is preserved.

---

## Next step

→ Start your first change with [`/sdd-new`](sdd-new.md)
