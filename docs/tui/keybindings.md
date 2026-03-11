# Keybindings

Press `?` on any screen to open the in-app keybindings reference.

---

## Global (all screens)

| Key | Action |
|-----|--------|
| `?` | Open keybindings help screen |

---

## EpicsView — Changes list

| Key | Action |
|-----|--------|
| `Enter` | Open change detail |
| `a` | Toggle show/hide archived changes |
| `r` | Refresh |
| `s` | Open `steering.md` viewer |
| `/` | Search / filter changes by name |
| `H` | Open Spec Health dashboard |
| `X` | Open Decisions Timeline |
| `P` | Open Progress Dashboard |
| `V` | Open Velocity Metrics |
| `l` | Open Releases screen |
| `K` | Open Skill Palette |
| `S` | Open Git Workflow Setup wizard |
| `G` | Open Git Log screen |
| `T` | Open Todos screen |
| `q` | Quit |

---

## ChangeDetailScreen — Change detail

| Key | Action |
|-----|--------|
| `p` | View `proposal.md` |
| `d` | View `design.md` |
| `s` | View spec(s) |
| `t` | View `tasks.md` |
| `q` | View `requirements.md` |
| `Space` | Copy next SDD command to clipboard |
| `E` | Open Spec Evolution viewer |
| `r` | Refresh in place |
| `K` | Open Skill Palette (change context) |
| `Esc` | Back to changes list |

---

## SpecHealthScreen — Spec health dashboard

| Key | Action |
|-----|--------|
| `Enter` | Open change detail for selected row |
| `Esc` | Back to changes list |

---

## SpecEvolutionScreen / DecisionsTimeline

| Key | Action |
|-----|--------|
| `D` | Toggle delta view / canonical view |
| `j` / `k` | Scroll down / up |
| `Esc` | Back |

---

## Document viewers (proposal, design, spec, tasks)

| Key | Action |
|-----|--------|
| `j` / `k` | Scroll down / up |
| `q` / `Esc` | Close viewer |

---

## Search / filter (EpicsView)

| Key | Action |
|-----|--------|
| `/` | Open search input |
| `Esc` | Clear filter and close input |
| Any text | Filter changes by name (live) |

Matching changes are highlighted in **bold cyan**. The filter persists while the input is open.

---

## Tips

- Most screens support `j`/`k` for Vim-style scrolling
- `Esc` always goes back — there's no separate "back" button
- `Space` in ChangeDetail copies the exact command you need to run next in Claude Code (e.g. `/sdd-apply T03`)
