from __future__ import annotations

from pathlib import Path

from sdd_tui.core.models import Change, PhaseState, Pipeline, Task
from sdd_tui.core.progress import ProgressReport, compute_progress


def _make_change(
    name: str = "my-change",
    pipeline: Pipeline | None = None,
    tasks: list[Task] | None = None,
) -> Change:
    return Change(
        name=name,
        path=Path("/tmp/fake"),
        pipeline=pipeline or Pipeline(),
        tasks=tasks or [],
    )


def _pipeline_up_to(phase: str) -> Pipeline:
    """Return a Pipeline with all phases up to `phase` set to DONE."""
    phases = ["propose", "spec", "design", "tasks", "apply", "verify"]
    kwargs: dict[str, PhaseState] = {}
    reached = False
    for p in phases:
        if reached:
            kwargs[p] = PhaseState.PENDING
        else:
            kwargs[p] = PhaseState.DONE
            if p == phase:
                reached = True
    return Pipeline(**kwargs)


def _make_tasks(done: int, total: int) -> list[Task]:
    tasks = []
    for i in range(total):
        tasks.append(Task(id=f"T{i+1:02d}", description="desc", done=(i < done)))
    return tasks


# --- compute_progress: empty list ---


def test_empty_list_returns_zero_percent() -> None:
    report = compute_progress([])
    assert report.percent == 0


def test_empty_list_returns_zero_totals() -> None:
    report = compute_progress([])
    assert report.total_done == 0
    assert report.total_tasks == 0


def test_empty_list_returns_empty_changes() -> None:
    report = compute_progress([])
    assert report.changes == []


# --- no tasks, no divide by zero ---


def test_no_tasks_no_divide_by_zero() -> None:
    changes = [_make_change("a"), _make_change("b")]
    report = compute_progress(changes)
    assert report.percent == 0
    assert report.total_tasks == 0


def test_no_tasks_change_appears_with_zero_zero() -> None:
    change = _make_change("a")
    report = compute_progress([change])
    assert len(report.changes) == 1
    assert report.changes[0].tasks_done == 0
    assert report.changes[0].tasks_total == 0


# --- partial and full progress ---


def test_all_done_returns_100_percent() -> None:
    change = _make_change(tasks=_make_tasks(done=4, total=4))
    report = compute_progress([change])
    assert report.percent == 100


def test_partial_progress() -> None:
    change = _make_change(tasks=_make_tasks(done=3, total=5))
    report = compute_progress([change])
    assert report.percent == 60


def test_multiple_changes_aggregate() -> None:
    c1 = _make_change("a", tasks=_make_tasks(done=2, total=4))
    c2 = _make_change("b", tasks=_make_tasks(done=1, total=3))
    report = compute_progress([c1, c2])
    assert report.total_done == 3
    assert report.total_tasks == 7
    assert report.percent == round(3 / 7 * 100)


# --- furthest_phase ---


def test_furthest_phase_none_when_no_phase_done() -> None:
    change = _make_change(pipeline=Pipeline())
    report = compute_progress([change])
    assert report.changes[0].furthest_phase is None


def test_furthest_phase_spec() -> None:
    change = _make_change(pipeline=_pipeline_up_to("spec"))
    report = compute_progress([change])
    assert report.changes[0].furthest_phase == "spec"


def test_furthest_phase_apply() -> None:
    change = _make_change(pipeline=_pipeline_up_to("apply"))
    report = compute_progress([change])
    assert report.changes[0].furthest_phase == "apply"


def test_furthest_phase_all_done_is_verify() -> None:
    change = _make_change(pipeline=_pipeline_up_to("verify"))
    report = compute_progress([change])
    assert report.changes[0].furthest_phase == "verify"


# --- pipeline_distribution ---


def test_pipeline_distribution_zero_when_no_phases_done() -> None:
    change = _make_change(pipeline=Pipeline())
    report = compute_progress([change])
    for phase in ["propose", "spec", "design", "tasks", "apply", "verify"]:
        assert report.pipeline_distribution[phase] == 0


def test_pipeline_distribution_single_change() -> None:
    change = _make_change(pipeline=_pipeline_up_to("design"))
    report = compute_progress([change])
    assert report.pipeline_distribution["design"] == 1
    assert report.pipeline_distribution["tasks"] == 0


def test_pipeline_distribution_all_phases() -> None:
    phases = ["propose", "spec", "design", "tasks", "apply", "verify"]
    changes = [_make_change(name=p, pipeline=_pipeline_up_to(p)) for p in phases]
    report = compute_progress(changes)
    for phase in phases:
        assert report.pipeline_distribution[phase] == 1


def test_pipeline_distribution_multiple_in_same_phase() -> None:
    c1 = _make_change("a", pipeline=_pipeline_up_to("spec"))
    c2 = _make_change("b", pipeline=_pipeline_up_to("spec"))
    report = compute_progress([c1, c2])
    assert report.pipeline_distribution["spec"] == 2


# --- ProgressReport type ---


def test_compute_progress_returns_progress_report() -> None:
    assert isinstance(compute_progress([]), ProgressReport)


def test_change_progress_has_name() -> None:
    change = _make_change("foo")
    report = compute_progress([change])
    assert report.changes[0].name == "foo"
