# Providers

sdd-tui integrates with external services (GitHub, issue trackers) through a provider abstraction. This allows the TUI to work without any external services configured, and to support different platforms without changing core code.

---

## Configuration

Providers are configured via the **Git Workflow Setup wizard**, accessible from EpicsView with the `S` key.

The wizard generates `openspec/config.yaml` with a `git_workflow` section:

```yaml
project: my-app
git_workflow:
  git_host: github
  issue_tracker: github
  default_branch: main
  repo: owner/repo-name
```

---

## GitHub Provider

When `git_host: github` and `issue_tracker: github`, sdd-tui uses the `gh` CLI to fetch:

| Feature | Data shown |
|---------|-----------|
| PR status | Open/merged/closed, review state, URL |
| CI status | Last workflow run result (pass/fail/running) |
| Releases | Latest tag, publish date |
| Issues | Open issues list (via Todos screen) |

**Requirement:** `gh` must be installed and authenticated (`gh auth login`).

If `gh` is not found or a command fails, the TUI degrades gracefully — the affected panel shows a loading indicator or empty state, never an error crash.

---

## Null Provider

When no provider is configured, sdd-tui uses the **Null provider**: all external calls return empty results silently. The TUI works fully for local `openspec/` browsing — pipeline, spec health, decisions, diffs — without any network access.

This is the default for projects that:
- Don't use GitHub
- Use a private Git host without `gh` CLI support
- Prefer to keep the TUI fully offline

---

## Multi-project setup

sdd-tui can monitor multiple projects simultaneously. Configure them in `openspec/config.yaml`:

```yaml
projects:
  - name: frontend
    path: /path/to/frontend/openspec
    git_workflow:
      git_host: github
      repo: owner/frontend

  - name: backend
    path: /path/to/backend/openspec
    git_workflow:
      git_host: github
      repo: owner/backend

  - name: infra
    path: /path/to/infra/openspec
    # no git_workflow → uses Null provider for this project
```

EpicsView shows changes from all projects, with visual separators between them.

---

## Running the setup wizard

```bash
sdd-tui
# Press S from EpicsView to open the Git Workflow Setup wizard
```

The wizard walks through 5 steps:

1. Choose git host (GitHub / None)
2. Choose issue tracker (GitHub / None)
3. Enter repository name (`owner/repo`)
4. Enter default branch (`main` / `dev` / other)
5. Confirm and write `config.yaml`
