from __future__ import annotations

from pathlib import Path

from sdd_tui.core.metrics import INACTIVE_THRESHOLD_DAYS, ChangeMetrics, parse_metrics


def _make_spec(change_dir: Path, domain: str, content: str) -> None:
    spec_dir = change_dir / "specs" / domain
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(content)


# --- REQ counting ---

def test_req_count_from_spec_files(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(change_dir, "core", (
        "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
        "- **REQ-02** `[Unwanted]` If A, the B SHALL C\n"
    ))
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 2


def test_ears_count_typed_reqs(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(change_dir, "core", (
        "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
        "- **REQ-02** `[Unwanted]` If A, the B SHALL C\n"
        "- **REQ-03** `[State]` While D, the E SHALL F\n"
        "- **REQ-04** `[Optional]` Where feature, the G SHALL H\n"
        "- **REQ-05** `[Ubiquitous]` The I SHALL J\n"
    ))
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 5
    assert metrics.ears_count == 5


def test_non_ears_tags_not_counted(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    _make_spec(change_dir, "core", (
        "- **REQ-01** `[Event]` When X, the Y SHALL Z\n"
        "- **REQ-02** [SomeOther] description\n"
    ))
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 2
    assert metrics.ears_count == 1


def test_no_specs_returns_zero(tmp_path: Path) -> None:
    change_dir = tmp_path / "my-change"
    change_dir.mkdir()
    metrics = parse_metrics(change_dir, tmp_path)
    assert metrics.req_count == 0
    assert metrics.ears_count == 0


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
