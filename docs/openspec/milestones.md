# Milestones & Todos

Two optional mechanisms for organizing work beyond individual changes.

---

## Milestones

`openspec/milestones.yaml` groups changes under named milestones. sdd-tui's EpicsView uses this to display changes grouped by milestone instead of a flat list.

### Format

```yaml
milestones:
  - name: v1.0 — Core CLI
    changes:
      - add-task-command
      - list-tasks-command
      - delete-task-command

  - name: v1.1 — Priorities
    changes:
      - priority-flag
      - priority-filter

  - name: v2.0 — Projects
    changes:
      - projects-domain
      - assign-task-to-project
```

### Behavior in sdd-tui

- Changes are displayed grouped under their milestone in EpicsView
- Changes not assigned to any milestone appear under an `── unassigned ──` separator at the bottom
- Empty milestones are hidden
- Changes can only belong to one milestone

### When to use it

Milestones are optional. Use them when:

- You're planning a versioned release and want to track which changes belong to it
- A set of changes has a logical grouping that isn't obvious from the change names
- You're presenting progress to stakeholders and want a cleaner view

---

## Todos

`openspec/todos/` is a directory of free-form Markdown todo files. sdd-tui displays them in a dedicated **Todos screen** (`T` from EpicsView).

### Format

Any Markdown file with standard checkbox syntax:

```markdown
# Auth refactor — outstanding items

- [ ] Migrate session storage from cookie to JWT
- [ ] Add refresh token rotation
- [x] Document the new auth flow in openspec/specs/auth/spec.md
```

### When to use it

Todos are for things that don't yet have a formal change but shouldn't be lost:

- Follow-up work identified during a change review
- Technical debt items discovered mid-implementation
- Ideas for future changes that need more research

!!! tip
    When a todo item grows into a real change, move it: delete the todo entry and run `/sdd-new` for that item. The todo becomes the starting context for the proposal.

### Multiple files

You can have multiple todo files organized by topic:

```
openspec/todos/
├── auth.md
├── performance.md
└── api-cleanup.md
```

sdd-tui displays all of them in a single scrollable view, with each file as a section.
