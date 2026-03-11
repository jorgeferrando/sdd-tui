from pathlib import Path

from sdd_tui.core.providers.protocol import ReleaseWorkflowConfig
from sdd_tui.core.reader import _write_release_config, load_release_config

# --- load_release_config ---


def test_load_release_config_absent_when_no_config_file(tmp_path: Path) -> None:
    cfg, is_configured = load_release_config(tmp_path)
    assert not is_configured
    assert cfg == ReleaseWorkflowConfig()


def test_load_release_config_absent_when_no_section(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text("project: my-project\n")
    cfg, is_configured = load_release_config(tmp_path)
    assert not is_configured
    assert cfg == ReleaseWorkflowConfig()


def test_load_release_config_enabled_true(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text(
        "project: my-project\n"
        "release_workflow:\n"
        "  enabled: true\n"
        "  versioning: semver\n"
        "  changelog_source: openspec\n"
        "  homebrew_formula: Formula/my-project.rb\n"
    )
    cfg, is_configured = load_release_config(tmp_path)
    assert is_configured
    assert cfg.enabled is True
    assert cfg.versioning == "semver"
    assert cfg.changelog_source == "openspec"
    assert cfg.homebrew_formula == "Formula/my-project.rb"


def test_load_release_config_enabled_false_is_configured(tmp_path: Path) -> None:
    """enabled=False with section present → is_configured=True (user opted out)."""
    (tmp_path / "config.yaml").write_text(
        "release_workflow:\n"
        "  enabled: false\n"
        "  versioning: semver\n"
        "  changelog_source: openspec\n"
        "  homebrew_formula: null\n"
    )
    cfg, is_configured = load_release_config(tmp_path)
    assert is_configured
    assert cfg.enabled is False
    assert cfg.homebrew_formula is None


def test_load_release_config_homebrew_none_variants(tmp_path: Path) -> None:
    for null_val in ("null", "none", "~"):
        (tmp_path / "config.yaml").write_text(
            f"release_workflow:\n"
            f"  enabled: false\n"
            f"  versioning: semver\n"
            f"  changelog_source: openspec\n"
            f"  homebrew_formula: {null_val}\n"
        )
        cfg, _ = load_release_config(tmp_path)
        assert cfg.homebrew_formula is None, f"Expected None for {null_val!r}"


def test_load_release_config_section_stops_at_next_top_level_key(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_text(
        "release_workflow:\n"
        "  enabled: true\n"
        "  versioning: calver\n"
        "  changelog_source: manual\n"
        "  homebrew_formula: null\n"
        "git_workflow:\n"
        "  git_host: github\n"
    )
    cfg, is_configured = load_release_config(tmp_path)
    assert is_configured
    assert cfg.versioning == "calver"
    assert cfg.changelog_source == "manual"


def test_load_release_config_returns_defaults_on_corrupt_file(tmp_path: Path) -> None:
    (tmp_path / "config.yaml").write_bytes(b"\xff\xfe")
    cfg, is_configured = load_release_config(tmp_path)
    assert not is_configured
    assert cfg == ReleaseWorkflowConfig()


# --- _write_release_config ---


def test_write_release_config_creates_new_file(tmp_path: Path) -> None:
    cfg = ReleaseWorkflowConfig(
        enabled=True,
        versioning="semver",
        changelog_source="openspec",
        homebrew_formula="Formula/my.rb",
    )
    _write_release_config(tmp_path, cfg)
    text = (tmp_path / "config.yaml").read_text()
    assert "release_workflow:" in text
    assert "enabled: true" in text
    assert "homebrew_formula: Formula/my.rb" in text


def test_write_release_config_appends_to_existing(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("project: sdd-tui\n")
    _write_release_config(tmp_path, ReleaseWorkflowConfig(enabled=False))
    text = config_file.read_text()
    assert "project: sdd-tui" in text
    assert "release_workflow:" in text
    assert "enabled: false" in text


def test_write_release_config_replaces_existing_section(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "project: sdd-tui\n"
        "release_workflow:\n"
        "  enabled: false\n"
        "  versioning: semver\n"
        "  changelog_source: openspec\n"
        "  homebrew_formula: null\n"
        "git_workflow:\n"
        "  git_host: none\n"
    )
    _write_release_config(tmp_path, ReleaseWorkflowConfig(enabled=True, versioning="calver"))
    text = config_file.read_text()
    assert text.count("release_workflow:") == 1
    assert "enabled: true" in text
    assert "versioning: calver" in text
    assert "git_workflow:" in text  # preserved


def test_write_release_config_null_homebrew(tmp_path: Path) -> None:
    _write_release_config(tmp_path, ReleaseWorkflowConfig(homebrew_formula=None))
    text = (tmp_path / "config.yaml").read_text()
    assert "homebrew_formula: null" in text


def test_write_then_load_roundtrip(tmp_path: Path) -> None:
    original = ReleaseWorkflowConfig(
        enabled=True,
        versioning="calver",
        changelog_source="manual",
        homebrew_formula="Formula/sdd-tui.rb",
    )
    _write_release_config(tmp_path, original)
    loaded, is_configured = load_release_config(tmp_path)
    assert is_configured
    assert loaded == original
