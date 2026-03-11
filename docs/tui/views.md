# Views

sdd-tui is organized around screens. Each screen focuses on one aspect of your `openspec/`.

---

## EpicsView — Changes list

The main screen. Shows all active changes (and optionally archived ones) with their pipeline state.

```
┌─ sdd-tui ──────────────────────────────────────────────────────────┐
│ NAME                   PHASE     STATUS      SIZE  HINT             │
│ ──────────────────────────────────────────────────────────────────  │
│ auth-refresh-token     apply     ●  3/5       M    Run T04          │
│ user-profile-ui        verify    ✓  done       S    Push to CI      │
│ payment-webhook        propose   ○  new        ?    Write spec      │
└────────────────────────────────────────────────────────────────────┘
```

**Columns:**

| Column | Meaning |
|--------|---------|
| `NAME` | Change name |
| `PHASE` | Current SDD phase (propose → spec → design → tasks → apply → verify) |
| `STATUS` | `●` in progress, `✓` done, `○` not started |
| `SIZE` | Complexity: XS / S / M / L / XL (based on spec lines + task count) |
| `HINT` | Suggested next action |

Press `a` to toggle archived changes. Press `/` to filter by name.

---

## ChangeDetailScreen — Change detail

Opened with `Enter` from EpicsView. Shows the pipeline panel and task list for a specific change.

```
┌─ auth-refresh-token ───────────────────────────────────────────────┐
│ PIPELINE                          TASKS                             │
│ ─────────                         ──────                            │
│ propose  ✓                        [x] T01  src/auth/token.py       │
│ spec     ✓                        [x] T02  src/auth/refresh.py     │
│ design   ✓                        [ ] T03  tests/test_refresh.py   │
│ tasks    ✓                        [ ] T04  tests/test_token.py     │
│ apply    ● 2/4                                                      │
│ verify   ○                        NEXT  /sdd-apply T03             │
│ PR       ○  (loading...)                                            │
└────────────────────────────────────────────────────────────────────┘
```

Use `p` / `d` / `s` / `t` to open the corresponding document. Press `Space` to copy the next SDD command to clipboard.

---

## SpecHealthScreen — Spec health dashboard

Opened with `H` from EpicsView. Shows spec quality metrics for all changes.

```
┌─ Spec Health ──────────────────────────────────────────────────────┐
│ CHANGE              REQ   EARS%   TASKS   ARTIFACTS   HINT         │
│ ─────────────────────────────────────────────────────────────────  │
│ auth-refresh-token   8    100%      4        ✓        Run verify   │
│ user-profile-ui      3     67%      2        ✗        Add tests    │
│ payment-webhook      0      —       0        ✗        Write spec   │
└────────────────────────────────────────────────────────────────────┘
```

**Columns:**

| Column | Meaning |
|--------|---------|
| `REQ` | Number of EARS requirements in spec |
| `EARS%` | Percentage of requirements with proper EARS syntax |
| `TASKS` | Number of tasks in tasks.md |
| `ARTIFACTS` | Whether design.md, spec, and proposal all exist |
| `HINT` | Highest priority repair action |

Press `Enter` to open the change detail for any row.

---

## DecisionsTimeline — All decisions

Opened with `X` from EpicsView. Shows every architectural decision across all changes, in chronological order.

Decisions are extracted from the `## Decisiones Tomadas` tables in each change's spec files. Each decision shows its status: `locked` (final), `open` (under discussion), or `deferred` (postponed).

---

## SpecEvolutionScreen — Spec diff viewer

Opened with `E` from ChangeDetailScreen. Shows the delta spec for the current change alongside the canonical spec, so you can see exactly what this change adds or modifies.

Press `D` to toggle between the delta view and the canonical spec view.

---

## ProgressDashboard — Overall progress

Opened with `P` from EpicsView. Shows aggregate progress across all changes:

- Changes by phase distribution
- Furthest phase reached per change
- Total tasks completed vs pending

Press `e` to export the report as Markdown.

---

## VelocityScreen — Metrics

Opened with `V` from EpicsView. Shows throughput metrics: how many changes were completed per week, average cycle time (propose → archive), and changes currently in progress.

---

## GitLogScreen — Git history

Opened with `G` from EpicsView. Shows recent commits for the project, including commit hash, author, relative date, and message. Also shows working tree status (modified files) at the top.

---

## ReleasesScreen — GitHub releases

Opened with `l` from EpicsView. Lists GitHub releases for the repo (requires `gh` CLI). Shows tag, name, and publish date.

---

## TodosScreen — Todo files

Opened with `T` from EpicsView. Shows all files from `openspec/todos/` in a single scrollable view. Each file is a section with its checkboxes rendered.

---

## HelpScreen — Keybindings reference

Opened with `?` from any screen. Shows the keybindings available in the current context.
