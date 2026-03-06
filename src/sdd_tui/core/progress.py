from __future__ import annotations

from dataclasses import dataclass, field

from sdd_tui.core.models import Change, PhaseState

_PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]


@dataclass
class ChangeProgress:
    name: str
    tasks_done: int
    tasks_total: int
    furthest_phase: str | None


@dataclass
class ProgressReport:
    changes: list[ChangeProgress] = field(default_factory=list)
    total_done: int = 0
    total_tasks: int = 0
    percent: int = 0
    pipeline_distribution: dict[str, int] = field(
        default_factory=lambda: {p: 0 for p in _PHASES}
    )


def compute_progress(changes: list[Change]) -> ProgressReport:
    """Aggregate progress across all changes. Pure function — no I/O."""
    if not changes:
        return ProgressReport()

    change_progresses: list[ChangeProgress] = []
    total_done = 0
    total_tasks = 0
    distribution: dict[str, int] = {p: 0 for p in _PHASES}

    for change in changes:
        done = sum(1 for t in change.tasks if t.done)
        total = len(change.tasks)
        furthest = _furthest_phase(change)

        change_progresses.append(
            ChangeProgress(
                name=change.name,
                tasks_done=done,
                tasks_total=total,
                furthest_phase=furthest,
            )
        )
        total_done += done
        total_tasks += total

        if furthest is not None:
            distribution[furthest] += 1

    percent = round(total_done / total_tasks * 100) if total_tasks > 0 else 0

    return ProgressReport(
        changes=change_progresses,
        total_done=total_done,
        total_tasks=total_tasks,
        percent=percent,
        pipeline_distribution=distribution,
    )


def _furthest_phase(change: Change) -> str | None:
    """Return the last DONE phase in pipeline order, or None if none are done."""
    furthest = None
    for phase in _PHASES:
        if getattr(change.pipeline, phase) == PhaseState.DONE:
            furthest = phase
    return furthest
