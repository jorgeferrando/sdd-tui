---
name: sdd-apply
description: SDD Apply - Implement the change following tasks.md. One task = one file = one atomic commit. Usage - /sdd-apply or /sdd-apply {change-name} or /sdd-apply T03.
---

# SDD Apply

> Implement the code following `tasks.md`. One task = one file = one atomic commit.

## Usage

```
/sdd-apply                 # Implement active change
/sdd-apply {change-name}   # Implement specific change
/sdd-apply T03             # Continue from a specific task
```

## Prerequisites

- `tasks.md` approved with task list
- Correct git branch created

## Step 1: Load current state

Read `openspec/changes/{change}/tasks.md`. Identify:
- Completed tasks (marked `[x]`)
- Next pending task
- Dependencies between tasks

If `T03` is provided: start from that task.

## Step 2: Verify git state

```bash
git status          # should be clean
git branch --show-current
```

## Step 3: Implement task by task

For each pending task:

### a) Announce

```
=== Task T02/T05: {Task description} ===
File: {path/to/file}
```

### b) Implement

Write code following existing project patterns. Read similar code first.

### c) Quality check

Run the project's test/lint commands on the changed file:
```bash
# Examples — use whatever your project uses:
pytest {path/to/test}
npm test
go test ./...
```

Fix any issues before committing. Do not proceed with failing quality checks.

### d) Atomic commit

```bash
git add {specific file}
git commit -m "$(cat <<'EOF'
[{change-name}] {Description in English, imperative mood}

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Commit message rules:**
- Max 70 characters on the first line
- Imperative mood: "Add", "Fix", "Update" (not "Added", "Fixes")
- Only the file(s) for this task (atomic)

### e) Update tasks.md

Mark task as completed:
```
- [x] **T02** ...
```

### f) Confirm before continuing

```
T02 completed ✓
Commits: 2/5
Continue with T03?
```

## Step 4: Changes requested during apply

If the user asks for a change not in `tasks.md`:

**BEFORE implementing:**

1. Add it to `tasks.md` as `BUGxx` or `IMPxx`:
   ```markdown
   ## Bugs found during apply

   - [ ] **BUG01** `path/file` — short symptom description
     - Fix: {description}
     - Commit: `[{change-name}] Fix {description}`
   ```
2. Implement it
3. Commit atomically
4. Mark as `[x]`

**Never implement an unregistered change.** The `tasks.md` is the project timeline.

## Step 5: Unexpected situations

**Do NOT make unilateral decisions.** If something not covered by tasks.md appears:

```
During T03 I found {situation}.
The tasks don't cover this case. How should I proceed?
1. {Option A}
2. {Option B}
3. Stop and update design/tasks
```

## Step 6: Summary when done

```
APPLY COMPLETE: {change-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tasks completed: N/N
Commits: N
Files created: [list]
Files modified: [list]

Next: /sdd-verify
```

## Next Step

With implementation complete → `/sdd-verify` for tests and quality gates.
