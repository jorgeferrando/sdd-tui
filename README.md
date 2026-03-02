# sdd-tui

TUI for managing the [SDD (Spec-Driven Development)](https://github.com/jorgeferrando) workflow and local integrations per epic.

> Work in progress.

## Concept

A terminal UI built with [Textual](https://textual.textualize.io/) to visualize and navigate the SDD pipeline across epics and subtasks.

## Stack

- Python + [Textual](https://textual.textualize.io/)
- Jira REST API
- Git (subprocess / pygit2)
- Local `openspec/` directory (never committed)

## Views

1. **Epics** — list of epics with local integration status
2. **Epic detail** — subtask table with SDD phase columns (propose → spec → design → tasks → apply → verify → ship → archive)
3. **Subtask detail** — task list + pipeline sidebar
4. **Task diff** — commit diff for a specific task

## Status

Early design phase. Not yet implemented.
