# Your First Change

This tutorial walks you through a complete SDD cycle from start to finish. We'll use **taskflow** — a fictional CLI task manager — as the example project.

By the end you'll have:

- An initialized `openspec/` directory
- A complete change documented and archived
- A working mental model of the SDD cycle

---

## 1. Bootstrap the project

Open Claude Code in your project root and run:

```
/sdd-init
```

The skill will ask a few questions about your project (tech stack, team size, deployment model) and generate the `openspec/` directory with steering artifacts:

```
openspec/
├── config.yaml
├── specs/           ← canonical specs (empty at start)
├── changes/         ← active changes
└── steering/
    ├── product.md   ← what the product does and why
    ├── tech.md      ← tech stack and conventions
    └── structure.md ← codebase layout
```

!!! tip
    `openspec/` should be committed to your repo. It's the living documentation of your project — not a temporary artifact.

---

## 2. Start a new change

You need to add a `--priority` flag to the `taskflow add` command. Run:

```
/sdd-new "add priority flag to task add command"
```

Claude Code will:

1. **Explore** the codebase — find the `add` command, understand the data model
2. **Propose** the change — create `openspec/changes/priority-flag/proposal.md`

The proposal looks like:

```markdown
# Proposal: priority-flag

## Description
Add an optional `--priority` flag (low/medium/high) to `taskflow add`.

## Motivation
Users have no way to distinguish urgent tasks from routine ones.

## Success criteria
- [ ] `taskflow add "fix bug" --priority high` works
- [ ] Priority is shown in `taskflow list`
- [ ] Defaults to `medium` when omitted
```

Review the proposal. When you're happy, continue:

```
/sdd-continue
```

---

## 3. Write the spec

`/sdd-continue` detects that `spec` is the next pending phase and runs `/sdd-spec` automatically.

The spec captures *what* the system does, not *how*:

```markdown
## Requirements (EARS)

- REQ-01 [Event] When the user runs `taskflow add` with `--priority`,
  the CLI SHALL store the priority value alongside the task.

- REQ-02 [Ubiquitous] The system SHALL accept priority values:
  low, medium, high (case-insensitive).

- REQ-03 [Unwanted] If an invalid priority value is provided,
  the CLI SHALL exit with code 1 and print the valid options.

- REQ-04 [State] While no `--priority` flag is provided,
  the system SHALL default to `medium`.
```

Approve the spec, then:

```
/sdd-continue
```

---

## 4. Design the implementation

`/sdd-design` translates the spec into a concrete plan:

```markdown
## Files to create
| File | Purpose |
|------|---------|
| src/cli/add.py | Add --priority argument to the add command |
| src/models/task.py | Add priority field to Task dataclass |
| tests/test_add.py | Unit tests for priority validation |
```

The design also identifies the total file count and warns if you're approaching the 20-file limit.

```
/sdd-continue
```

---

## 5. Generate tasks

`/sdd-tasks` breaks the design into atomic tasks:

```markdown
- [ ] T01  src/models/task.py    — add priority field + enum
- [ ] T02  src/cli/add.py        — add --priority argument
- [ ] T03  tests/test_add.py     — priority validation tests
```

Each task = one file = one commit.

---

## 6. Implement

```
/sdd-apply
```

Claude Code implements each task, runs quality checks, and commits atomically:

```
T01 ✓  [priority-flag] Add Priority enum and field to Task model
T02 ✓  [priority-flag] Add --priority flag to add command
T03 ✓  [priority-flag] Add unit tests for priority validation
```

If you ask Claude to fix something mid-apply ("the error message should mention the flag name"), it will register it as `BUG01` in `tasks.md` before touching any code.

---

## 7. Verify

```
/sdd-verify
```

Runs your project's test suite and quality checks, then walks through a self-review checklist:

- All tests pass?
- No new warnings?
- Spec requirements covered by tests?
- No debug code left?

---

## 8. Archive

```
/sdd-archive
```

Closes the change:

1. Moves `openspec/changes/priority-flag/` → `openspec/changes/archive/YYYY-MM-DD-priority-flag/`
2. Merges the delta spec into `openspec/specs/cli/spec.md`
3. Updates `CHANGELOG.md`

The archived change is permanent history. Every requirement, decision, and task is preserved.

---

## What you now have

```
openspec/
├── specs/
│   └── cli/
│       └── spec.md     ← canonical spec updated with priority-flag behavior
└── changes/
    └── archive/
        └── 2024-03-11-priority-flag/
            ├── proposal.md
            ├── specs/cli/spec.md
            ├── design.md
            └── tasks.md
```

Next time someone asks "why does the priority flag default to medium?" — the answer is in `openspec/changes/archive/2024-03-11-priority-flag/proposal.md`.

---

## Next steps

- [Explore the full workflow →](../workflow/overview.md)
- [Learn what's in openspec/ →](../openspec/structure.md)
- [Launch sdd-tui to visualize your changes →](../tui/overview.md)
