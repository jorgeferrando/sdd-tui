from __future__ import annotations

from pathlib import Path

from sdd_tui.core.metrics import (
    INACTIVE_THRESHOLD_DAYS,
    ChangeMetrics,
    _count_git_files,
    _count_spec_lines,
    _count_tasks,
    _get_complexity,
    parse_metrics,
)


def _make_spec(change_dir: Path, domain: str, content: str) -> None:
    spec_dir = change_dir / "specs" / domain
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(content)


# --- REQ counting ---


def test_req_count_from_spec_files(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(
        change_dir,
        "core",
        (
            "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
            "- **REQ-02** `[Unwanted]` If A, the B SHALL C\n"
        ),
    )
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 2


def test_ears_count_typed_reqs(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(
        change_dir,
        "core",
        (
            "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
            "- **REQ-02** `[Unwanted]` If A, the B SHALL C\n"
            "- **REQ-03** `[State]` While D, the E SHALL F\n"
            "- **REQ-04** `[Optional]` Where feature, the G SHALL H\n"
            "- **REQ-05** `[Ubiquitous]` The I SHALL J\n"
        ),
    )
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 5
    assert metrics.ears_count == 5


def test_non_ears_tags_not_counted(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(
        change_dir,
        "core",
        ("- **REQ-01** `[Event]` When X, the Y SHALL Z\n- **REQ-02** [SomeOther] description\n"),
    )
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 2
    assert metrics.ears_count == 1


def test_no_specs_returns_zero(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 0
    assert metrics.ears_count == 0


def test_duplicate_req_counted_once(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    # REQ-01 appears twice: once as definition (with EARS), once as scenario header (without)
    _make_spec(
        change_dir,
        "core",
        (
            "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
            "\n"
            "**REQ-01** — Scenario name\n"
            "**Dado** ...\n"
        ),
    )
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 1
    assert metrics.ears_count == 1


def test_reqs_across_multiple_domains(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(change_dir, "core", "- **REQ-01** `[Event]` When X, the Y SHALL Z\n")
    _make_spec(change_dir, "tui", "- **REQ-02** `[State]` While D, the E SHALL F\n")
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 2
    assert metrics.ears_count == 2


# --- Artifacts ---


def test_artifacts_presence(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").touch()
    (change_dir / "design.md").touch()
    (change_dir / "tasks.md").touch()
    _make_spec(change_dir, "core", "")
    metrics = parse_metrics(change_dir, tmp_path)
    assert "proposal" in metrics.artifacts
    assert "spec" in metrics.artifacts
    assert "design" in metrics.artifacts
    assert "tasks" in metrics.artifacts
    assert "research" not in metrics.artifacts


def test_artifacts_research_optional(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "research.md").touch()
    metrics = parse_metrics(change_dir, tmp_path)
    assert "research" in metrics.artifacts


def test_artifacts_order(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").touch()
    (change_dir / "research.md").touch()
    (change_dir / "design.md").touch()
    (change_dir / "tasks.md").touch()
    _make_spec(change_dir, "core", "")
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.artifacts == ["proposal", "spec", "research", "design", "tasks"]


def test_empty_change_has_no_artifacts(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.artifacts == []


# --- Inactive days ---


def test_inactive_days_no_git(tmp_path: Path) -> None:
    """tmp_path is not a git repo → inactive_days=None."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.inactive_days is None


# --- Threshold constant ---


def test_inactive_threshold_is_seven() -> None:
    assert INACTIVE_THRESHOLD_DAYS == 7


# --- ChangeMetrics dataclass ---


def test_change_metrics_fields() -> None:
    m = ChangeMetrics(req_count=3, ears_count=2, artifacts=["proposal"], inactive_days=5)
    assert m.req_count == 3
    assert m.ears_count == 2
    assert m.artifacts == ["proposal"]
    assert m.inactive_days == 5


# --- requirements.md artifact ---


def test_requirements_artifact_detected(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "requirements.md").touch()

    metrics = parse_metrics(change_dir, tmp_path)

    assert "requirements" in metrics.artifacts


def test_requirements_artifact_absent(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()

    metrics = parse_metrics(change_dir, tmp_path)

    assert "requirements" not in metrics.artifacts


def test_requirements_artifact_order(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").touch()
    (change_dir / "research.md").touch()
    (change_dir / "requirements.md").touch()
    (change_dir / "design.md").touch()
    (change_dir / "tasks.md").touch()
    _make_spec(change_dir, "core", "")

    metrics = parse_metrics(change_dir, tmp_path)

    assert metrics.artifacts == [
        "proposal",
        "spec",
        "research",
        "requirements",
        "design",
        "tasks",
    ]


# --- REQ counting from requirements.md ---


def test_reqs_counted_from_requirements_md(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "requirements.md").write_text(
        "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
        "- **REQ-02** `[Unwanted]` If A, the B SHALL C\n"
    )

    metrics = parse_metrics(change_dir, tmp_path)

    assert metrics.req_count == 2
    assert metrics.ears_count == 2


# --- Complexity score ---


def test_complexity_score_empty_change(tmp_path: Path) -> None:
    """No tasks, no spec, not a git repo → score=0, label='XS'."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    score, label = _get_complexity(change_dir, tmp_path)
    assert score == 0
    assert label == "XS"


def test_complexity_score_tasks_only(tmp_path: Path) -> None:
    """4 tasks → score = 4*3 + 0 + 0 = 12 → 'S'."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    tasks_content = (
        "- [x] **T01** Create models\n"
        "- [x] **T02** Add reader\n"
        "- [ ] **T03** Add pipeline\n"
        "- [ ] **T04** Fix bug\n"
    )
    (change_dir / "tasks.md").write_text(tasks_content)
    score, label = _get_complexity(change_dir, tmp_path)
    assert score == 12
    assert label == "S"


def test_complexity_score_formula(tmp_path: Path) -> None:
    """3 tasks + 100 spec lines → score = 3*3 + 100//50 + 0 = 11 → 'S'."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "tasks.md").write_text(
        "- [x] **T01** desc\n- [ ] **T02** desc\n- [ ] **T03** desc\n"
    )
    spec_content = "\n".join(f"line {i}" for i in range(100))
    _make_spec(change_dir, "core", spec_content)
    score, label = _get_complexity(change_dir, tmp_path)
    assert score == 11  # 9 + 2 + 0
    assert label == "S"


def test_complexity_label_thresholds(tmp_path: Path) -> None:
    """Verify all label boundaries via direct score calculation."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    # Inject known scores by using tasks only (no git, no spec)
    # Score = task_count * 3; sizes: XS<6, S<13, M<25, L<41, XL>=41
    cases = [
        (0, "XS"),   # 0 tasks → 0
        (2, "XS"),   # 2 tasks → 6... wait: 2*3=6 → S
    ]
    # Use _count_tasks / _count_spec_lines / _count_git_files directly
    # Test boundary values for _get_complexity via tasks.md manipulation
    for task_count, expected_label in [
        (0, "XS"),   # score 0
        (1, "XS"),   # score 3
        (2, "S"),    # score 6
        (4, "S"),    # score 12
        (5, "M"),    # score 15
        (9, "L"),    # score 27
        (14, "XL"),  # score 42
    ]:
        c = tmp_path / f"change-{task_count}"
        c.mkdir()
        lines = "".join(f"- [ ] **T{i:02d}** desc\n" for i in range(task_count))
        (c / "tasks.md").write_text(lines)
        score, label = _get_complexity(c, tmp_path)
        assert label == expected_label, f"task_count={task_count} score={score} expected={expected_label} got={label}"


def test_complexity_git_files_fallback(tmp_path: Path) -> None:
    """Non-git directory → git_files=0, no exception."""
    count = _count_git_files("my-change", tmp_path)
    assert count == 0


def test_complexity_count_spec_lines(tmp_path: Path) -> None:
    """_count_spec_lines sums lines across all spec files."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(change_dir, "core", "line1\nline2\nline3\n")
    _make_spec(change_dir, "tui", "a\nb\n")
    assert _count_spec_lines(change_dir) == 5


def test_complexity_count_tasks_only_task_lines(tmp_path: Path) -> None:
    """_count_tasks ignores non-task lines."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    (change_dir / "tasks.md").write_text(
        "# Tasks\n\n- [x] **T01** desc\n- [ ] **T02** desc\n## Section\n- not a task\n"
    )
    assert _count_tasks(change_dir) == 2


def test_parse_metrics_includes_complexity(tmp_path: Path) -> None:
    """parse_metrics populates complexity_score and complexity_label."""
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    metrics = parse_metrics(change_dir, tmp_path)
    assert hasattr(metrics, "complexity_score")
    assert hasattr(metrics, "complexity_label")
    assert metrics.complexity_score == 0
    assert metrics.complexity_label == "XS"


def test_reqs_deduped_across_requirements_and_specs(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    # REQ-01 appears in both requirements.md and specs/
    (change_dir / "requirements.md").write_text("- **REQ-01** `[Event]` When X, the Y SHALL Z\n")
    _make_spec(
        change_dir,
        "core",
        (
            "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
            "- **REQ-02** `[State]` While D, the E SHALL F\n"
        ),
    )

    metrics = parse_metrics(change_dir, tmp_path)

    assert metrics.req_count == 2  # REQ-01 deduplicated, REQ-02 from spec
    assert metrics.ears_count == 2
