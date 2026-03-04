from __future__ import annotations

import re
from pathlib import Path

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import PhaseState, Pipeline, Task


class TaskParser:
    _TASK_RE = re.compile(r"^- \[(x| )\] \*{0,2}([A-Z]+\d+)\*{0,2} (.+)$")
    _AMENDMENT_RE = re.compile(r"^── amendment: (.+) ──$")
    _COMMIT_HINT_RE = re.compile(r"^\s{2,}-\s+Commit:\s+`?(.+?)`?\s*$")

    def parse(self, tasks_md: Path) -> list[Task]:
        tasks: list[Task] = []
        current_amendment: str | None = None
        last_task: Task | None = None

        for line in tasks_md.read_text().splitlines():
            stripped = line.strip()

            if amendment_match := self._AMENDMENT_RE.match(stripped):
                current_amendment = amendment_match.group(1).strip()
                last_task = None
                continue

            if task_match := self._TASK_RE.match(stripped):
                task = Task(
                    id=task_match.group(2),
                    description=task_match.group(3).strip(),
                    done=task_match.group(1) == "x",
                    amendment=current_amendment,
                )
                tasks.append(task)
                last_task = task
                continue

            if last_task is not None:
                if hint_match := self._COMMIT_HINT_RE.match(line):
                    last_task.commit_hint = hint_match.group(1).strip()
                    last_task = None

        return tasks


class PipelineInferer:
    def __init__(self) -> None:
        self._parser = TaskParser()

    def infer(self, change_path: Path, git_reader: GitReader) -> Pipeline:
        propose = self._check_file(change_path / "proposal.md")
        spec = self._check_glob(change_path / "specs", "*/spec.md")
        design = self._check_file(change_path / "design.md")

        tasks_md = change_path / "tasks.md"
        tasks_exists = tasks_md.exists()
        tasks = PhaseState.DONE if tasks_exists else PhaseState.PENDING

        apply = PhaseState.PENDING
        if tasks_exists:
            parsed = self._parser.parse(tasks_md)
            apply = PhaseState.PENDING if any(not t.done for t in parsed) else PhaseState.DONE

        verify = PhaseState.PENDING
        if apply == PhaseState.DONE:
            clean = git_reader.is_clean(change_path)
            verify = PhaseState.DONE if clean is True else PhaseState.PENDING

        return Pipeline(
            propose=propose,
            spec=spec,
            design=design,
            tasks=tasks,
            apply=apply,
            verify=verify,
        )

    def _check_file(self, path: Path) -> PhaseState:
        return PhaseState.DONE if path.exists() else PhaseState.PENDING

    def _check_glob(self, base: Path, pattern: str) -> PhaseState:
        if not base.exists():
            return PhaseState.PENDING
        return PhaseState.DONE if any(base.glob(pattern)) else PhaseState.PENDING
