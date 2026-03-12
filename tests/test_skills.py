from pathlib import Path

from sdd_tui.core.skills import _CONTEXT_AWARE, SkillInfo, load_skills


def _make_skill(tmp_path: Path, name: str, description: str = "A description") -> Path:
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Body"
    )
    return skill_dir


def test_load_skills_returns_empty_when_dir_missing(tmp_path: Path) -> None:
    assert load_skills(tmp_path / "nonexistent") == []


def test_load_skills_skips_entry_without_skill_md(tmp_path: Path) -> None:
    (tmp_path / "no-skill-md").mkdir()
    assert load_skills(tmp_path) == []


def test_load_skills_skips_invalid_front_matter(tmp_path: Path) -> None:
    skill_dir = tmp_path / "bad-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# No front matter here")
    assert load_skills(tmp_path) == []


def test_load_skills_skips_missing_description_field(tmp_path: Path) -> None:
    skill_dir = tmp_path / "incomplete"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: incomplete\n---\n")
    assert load_skills(tmp_path) == []


def test_load_skills_skips_missing_name_field(tmp_path: Path) -> None:
    skill_dir = tmp_path / "no-name"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\ndescription: some description\n---\n")
    assert load_skills(tmp_path) == []


def test_load_skills_returns_skill_info(tmp_path: Path) -> None:
    _make_skill(tmp_path, "build", "Vertical BUILD - implementation skill")
    result = load_skills(tmp_path)
    assert len(result) == 1
    assert result[0] == SkillInfo(name="build", description="Vertical BUILD - implementation skill")


def test_load_skills_sdd_first_order(tmp_path: Path) -> None:
    _make_skill(tmp_path, "build")
    _make_skill(tmp_path, "sdd-apply")
    _make_skill(tmp_path, "sdd-new")
    _make_skill(tmp_path, "docker")
    result = load_skills(tmp_path)
    names = [s.name for s in result]
    assert names == ["sdd-apply", "sdd-new", "build", "docker"]


def test_load_skills_multiple_sdd_sorted_alphabetically(tmp_path: Path) -> None:
    _make_skill(tmp_path, "sdd-verify")
    _make_skill(tmp_path, "sdd-apply")
    _make_skill(tmp_path, "sdd-new")
    result = load_skills(tmp_path)
    names = [s.name for s in result]
    assert names == ["sdd-apply", "sdd-new", "sdd-verify"]


def test_load_skills_non_sdd_sorted_alphabetically(tmp_path: Path) -> None:
    _make_skill(tmp_path, "ship")
    _make_skill(tmp_path, "build")
    _make_skill(tmp_path, "docker")
    result = load_skills(tmp_path)
    names = [s.name for s in result]
    assert names == ["build", "docker", "ship"]


def test_context_aware_set_contains_expected_skills() -> None:
    expected = {
        "sdd-apply",
        "sdd-archive",
        "sdd-audit",
        "sdd-continue",
        "sdd-design",
        "sdd-spec",
        "sdd-steer",
        "sdd-tasks",
        "sdd-verify",
    }
    assert expected == _CONTEXT_AWARE


def test_context_aware_excludes_non_change_skills() -> None:
    excluded = {"sdd-new", "sdd-explore", "sdd-ff", "sdd-init", "sdd-propose"}
    for skill in excluded:
        assert skill not in _CONTEXT_AWARE
