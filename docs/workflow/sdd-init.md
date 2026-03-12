# sdd-init

**Bootstrap `openspec/` with guided onboarding.** Run this once at the start of a project to set up the directory structure and generate the steering files that feed the rest of the workflow.

```
/sdd-init
```

Safe to re-run — if steering already exists, it shows the current state instead of overwriting.

---

## What it does

1. Checks that the SDD skills are installed
2. Scans the project automatically (reads `package.json`, `pyproject.toml`, etc. to pre-fill answers)
3. Runs a guided Q&A about your project — confirms or corrects what was auto-detected
4. Generates **steering files** in `openspec/steering/`

---

## Example session

Running `/sdd-init` on a Python project looks like this:

```
Scanning project...
  ✓ pyproject.toml detected — Python project
  ✓ pytest found in dev dependencies
  ✓ ruff found in dev dependencies
  ✓ src/ layout detected

Let me confirm a few things:

[1/4] Tech stack detected: Python 3.11 + FastAPI + pytest. Correct?
> yes

[2/4] What does this project do? (one sentence)
> REST API for managing project tasks and deadlines

[3/4] Who are the main users?
> internal developer teams

[4/4] Any naming conventions not obvious from the code?
> We always prefix internal helpers with underscore, and never use
> abbreviations in variable names.

Generating steering files...

INIT COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
openspec/steering/product.md     ✓
openspec/steering/tech.md        ✓
openspec/steering/structure.md   ✓
openspec/steering/conventions.md ✓
openspec/steering/project-rules.md ✓

Next: /sdd-new "your first feature"
```

The scan reads real project files before asking questions, so most answers are pre-filled. For a typical project you'll only need to confirm or add a detail or two.

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
