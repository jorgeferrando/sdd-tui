# openspec/ Structure

`openspec/` is the living documentation directory for your project. It lives alongside your source code and should be committed to your repository.

---

## Full directory layout

```
openspec/
├── config.yaml                    ← project configuration for sdd-tui
│
├── specs/                         ← canonical specs (source of truth)
│   └── {domain}/
│       └── spec.md                ← behavior spec for a domain
│
├── changes/                       ← active and historical changes
│   ├── {change-name}/             ← one active change
│   │   ├── proposal.md            ← problem + solution + alternatives
│   │   ├── specs/
│   │   │   └── {domain}/
│   │   │       └── spec.md        ← delta spec (what changes in this domain)
│   │   ├── design.md              ← files to create/modify + decisions
│   │   └── tasks.md               ← ordered atomic task list
│   │
│   └── archive/                   ← completed changes (permanent)
│       └── YYYY-MM-DD-{change}/
│           └── {change-name}/     ← identical structure to active change
│
├── steering/                      ← project memory (read by sdd-apply)
│   ├── product.md                 ← what the product does and for whom
│   ├── tech.md                    ← stack, versions, toolchain
│   ├── structure.md               ← codebase layout
│   ├── conventions.md             ← naming rules, patterns, anti-patterns
│   └── project-rules.md           ← explicit rules Claude follows
│
├── milestones.yaml                ← optional: group changes by milestone
│
├── todos/                         ← optional: free-form todo files
│   └── {topic}.md
│
└── versions/                      ← optional: release version markers
    └── v{X.Y.Z}.md
```

---

## File purposes

### `config.yaml`

Configures sdd-tui for this project:

```yaml
project: my-app
openspec_path: openspec/
changes_path: openspec/changes/
archive_path: openspec/changes/archive/
specs_path: openspec/specs/
```

### `specs/{domain}/spec.md`

The **canonical spec** for a domain. This is the single source of truth for what the system does in that domain. Updated by `/sdd-archive` when a change that touches the domain is closed.

Domains map to bounded contexts, not to code directories. Examples: `auth`, `payments`, `reporting`, `api`, `cli`.

### `changes/{change-name}/proposal.md`

Created by `/sdd-new`. Answers: what is the problem, what is the proposed solution, what alternatives were considered, and what does success look like.

### `changes/{change-name}/specs/{domain}/spec.md`

A **delta spec** — it describes only what changes in this domain for this change. After archive, it merges into the canonical spec.

### `changes/{change-name}/design.md`

Created by `/sdd-design` (via `/sdd-continue`). Lists all files to create or modify, with their purpose. Includes a Mermaid diagram if ≥3 components interact.

### `changes/{change-name}/tasks.md`

Created by `/sdd-tasks`. Each task is one file, one commit. Marks progress with `[x]` / `[ ]`. Also records bugs and improvements discovered during implementation.

### `steering/`

See [Steering Files →](steering.md)

### `milestones.yaml`

Optional. Groups changes under milestones for sdd-tui's EpicsView. See [Milestones & Todos →](milestones.md)

---

## What gets committed

`openspec/` should always be committed. It's project documentation, not a build artifact.

The exception: if your project uses Claude Code in a shared environment, you may want to exclude `openspec/steering/` from the repo (steering files may contain internal conventions). Use `.gitignore` or `.git/info/exclude` for that.
