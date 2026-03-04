---
name: sdd-init
description: SDD Init - Bootstrap openspec/ in the current project. Creates the directory structure and excludes openspec/ from git via .git/info/exclude. Entry point for the SDD workflow. Usage - /sdd-init.
---

# SDD Init

> Bootstrap `openspec/` in the current project. Run once before starting the SDD workflow.

## Usage

```
/sdd-init
```

## What it does

1. Creates the `openspec/` directory structure
2. Excludes `openspec/` from git (via `.git/info/exclude`) so it stays local
3. Confirms the setup is ready

## Directory structure created

```
openspec/
├── specs/          ← canonical specs (domain knowledge)
└── changes/
    └── archive/    ← completed changes
```

## Step 1: Create structure

```bash
mkdir -p openspec/specs
mkdir -p openspec/changes/archive
```

## Step 2: Exclude from git

```bash
echo "openspec/" >> .git/info/exclude
```

Verify it's excluded:
```bash
git check-ignore -v openspec/
```

## Step 3: Confirm

```
SDD INIT COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━
openspec/specs/       ✓
openspec/changes/     ✓
.git/info/exclude     ✓ (openspec/ excluded)

Next: /sdd-new "description" to start your first change
```

## Notes

- `openspec/` is intentionally local — it contains work-in-progress documentation
- If your project commits `openspec/` (like sdd-tui itself), skip the exclude step
- Run once per project; safe to re-run if the structure already exists
