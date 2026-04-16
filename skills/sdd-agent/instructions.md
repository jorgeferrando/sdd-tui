---
name: sdd-agent
description: SDD Agent - Autonomous orchestrator that executes the full SDD cycle for a given task. Interacts via chat (Slack, web, or terminal) when it needs input. Usage - /sdd-agent "task description" or triggered by external systems.
requires: ["openspec/config.yaml"]
produces: ["openspec/changes/{change}/proposal.md", "openspec/changes/{change}/specs/*/spec.md", "openspec/changes/{change}/design.md", "openspec/changes/{change}/tasks.md"]
---

# SDD Agent

> Autonomous orchestrator that runs the full SDD cycle for a task. Works without supervision when it can, asks via chat when it can't.

## Usage

```
/sdd-agent "add rate limiting to the public API"
/sdd-agent --issue 42          # From GitHub issue #42
/sdd-agent --ticket PROJ-123   # From Jira ticket
```

## Prerequisites

- `openspec/` initialized (if not, runs `sdd-init --quick` automatically)
- Git repo with clean working tree

## Confidence model

Before each phase, assess confidence:

| Level | Criteria | Action |
|-------|----------|--------|
| **HIGH** | Scope < 5 files, existing pattern to follow, clear requirements | Proceed silently |
| **MEDIUM** | Scope 5-10 files, some ambiguity but reasonable defaults exist | Proceed, flag in PR description as "needs review" |
| **LOW** | Scope > 10 files, ambiguous requirements, no similar pattern, conflicting conventions | **Stop and ask** via chat |

Always classify before proceeding. When in doubt, ask — a junior that asks is better than one that guesses wrong.

## Step 1: Parse input

Read the task from:
- Direct description (string argument)
- GitHub issue (if `--issue N`): read title + body + comments via `gh issue view N`
- Jira ticket (if `--ticket ID`): read from Jira API

Extract:
- **Goal:** what needs to be built/fixed
- **Constraints:** any mentioned limitations, deadlines, or dependencies
- **Acceptance criteria:** explicit conditions if provided, otherwise derive from the goal

If the input is too vague to determine scope (e.g., "improve performance"), ask:
```
The task is broad. To proceed, I need to know:
- Which part of the system? (e.g., API response time, database queries, frontend load)
- What is the target? (e.g., < 200ms response, 50% reduction)
```

## Step 2: Bootstrap (if needed)

```bash
ls openspec/steering/conventions.md
```

If missing, run `sdd-init --quick` to bootstrap openspec/ with sensible defaults. Do not ask — a junior sets up their workspace without being told.

## Step 3: Explore with recall

Run the `sdd-explore` workflow:
1. Search archived specs and past decisions (recall)
2. Scan the codebase for similar patterns
3. Identify affected files and domains
4. Write findings to `openspec/changes/{change-name}/notes.md`

**Confidence check:** If recall finds a previous spec in the same domain that was explicitly scoped differently, flag it:
```
I found a previous spec for this domain that explicitly excluded {X}.
Your task seems to include {X}. Should I proceed including it, or respect the previous boundary?
```

## Step 4: Propose

Run the `sdd-propose` workflow:
1. Analyze the task against all proposal sections
2. For sections marked **missing**: ask via chat (group questions, max 3 at a time)
3. For sections marked **inferable**: use best judgment, mark as "inferred" in the proposal
4. Generate `proposal.md`

**Confidence check:** Show the proposal summary in chat:
```
Proposal ready for: {change-name}
Scope: {N} files, {domains}
Key decisions:
  - {decision 1}
  - {decision 2}

Should I continue to spec, or do you want to adjust anything?
```

Wait for response. If approved (or no response in the configured timeout), continue.

## Step 5: Spec

Run the `sdd-spec` workflow:
1. Read proposal, identify domain
2. Check for canonical spec (delta if exists)
3. For edge cases that affect business logic: ask via chat
4. For technical edge cases with clear conventions: decide and document

**Confidence check:** Only ask about business logic. Technical decisions follow conventions.

## Step 6: Design + Tasks

Run `sdd-design` as agent (non-interactive), then `sdd-tasks`:
1. Design reads proposal + spec + codebase, produces design.md
2. Tasks breaks design into atomic tasks with dependencies

**Confidence check:** If scope analysis shows > 10 files:
```
This change affects {N} files. That's larger than typical for autonomous work.
Options:
1. Proceed (I'll handle it in {N} tasks)
2. Split into smaller changes (I'll propose how to split)
3. Stop here — you take over from design.md
```

## Step 7: Apply

Run `sdd-apply --auto`:
1. Load steering (conventions, project-rules, tech)
2. For each task, spawn a subagent
3. Each subagent: implement, test, commit atomically
4. Report progress in chat after each task

```
Progress: T03/T05 ✓ Add rate limit middleware
  Commit: a1b2c3d
  Tests: 8/8 pass
```

**If a task fails (test failure, unexpected situation):**
1. Retry once with a different approach
2. If still failing: ask via chat with context
```
T04 failing: test_rate_limit_exceeded expects 429 but getting 200.
The middleware is not being applied to the route. I see two possible causes:
1. Route registration order — middleware runs after the handler
2. Missing middleware import in routes/index.js
Which should I investigate first, or should I try both?
```

## Step 8: Verify

Run `sdd-verify`:
1. Full test suite
2. Linter (if configured)
3. Self-review checklist
4. Convention audit
5. If the project has a dev server: start it, run smoke tests against acceptance criteria

**Do not create the PR in this step** — the orchestrator creates it with the full context.

## Step 9: Create PR

Create the pull request with structured description:

```bash
git push -u origin {branch-name}
gh pr create --title "{title}" --body "{body}"
```

PR body template:
```markdown
## Task
{Original task description or issue link}

## What this PR does
{1-3 sentences from proposal.md}

## Spec
{Key behaviors from spec.md — Given/When/Then summary}

## Design decisions
{Decision table from design.md}

## Changes
{File list from tasks.md with one-line descriptions}

## Acceptance criteria
{From proposal.md}

---
Generated by SDD Agent | [View full artifacts](openspec/changes/{change}/)
```

Report in chat:
```
✅ PR created: {repo}#{number}
  {title}
  {N} commits, {N} files changed
  Tests: all passing
  
  Waiting for review.
```

## Step 10: PR review loop

After creating the PR, monitor for review comments:

```bash
gh pr view {number} --json reviews,comments
```

When a review comment arrives:
1. Read the comment
2. If it's a change request: implement the fix, commit, push, reply to the comment
3. If it's a question: answer based on the spec/design context
4. If it requires a decision outside scope: ask via chat

```
Review comment on PR #{number} from @reviewer:
  "Why did you use middleware instead of a decorator pattern?"

My response (from design.md):
  "The middleware pattern was chosen because the existing codebase uses
   middleware for all cross-cutting concerns (auth, logging). Following
   the established pattern per conventions.md."

Should I reply with this, or do you want to adjust?
```

After addressing all comments, report:
```
PR #{number}: addressed {N} review comments, pushed {N} new commits.
Waiting for re-review.
```

Repeat until the PR is approved or the user stops the agent.

## Escalation protocol

**Always ask when:**
- Business logic is ambiguous (not technical — business)
- Scope changes beyond what was proposed
- Tests fail after 2 attempts
- Review comment requests architectural change
- Confidence is LOW on any phase

**Never ask when:**
- Technical decisions covered by conventions.md
- Code style choices covered by project-rules.md
- Test structure follows existing patterns
- Error handling follows established patterns

**How to ask:**
- Be specific, not vague ("Should X return 404 or 204?" not "What should X do?")
- Offer options with trade-offs
- Include context from the codebase
- Max 3 questions at a time

## Notes

- The chat channel (Slack, web, terminal) is injected by the runtime — this skill is channel-agnostic
- `AskUserQuestion` is the mechanism for all chat interactions
- If running headless (no chat), treat all MEDIUM confidence as HIGH and skip questions
- The PR review loop runs until approval, explicit stop, or configured timeout
