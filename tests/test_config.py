from __future__ import annotations

from pathlib import Path

from sdd_tui.core.config import AppConfig, _parse_config, load_config


def test_load_config_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    result = load_config()
    assert result == AppConfig(projects=[])


def test_load_config_returns_projects(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config_dir = tmp_path / ".sdd-tui"
    config_dir.mkdir()
    project_a = tmp_path / "projects" / "alpha"
    project_a.mkdir(parents=True)
    project_b = tmp_path / "projects" / "beta"
    project_b.mkdir(parents=True)
    (config_dir / "config.yaml").write_text(
        f"projects:\n  - path: {project_a}\n  - path: {project_b}\n"
    )
    result = load_config()
    assert len(result.projects) == 2
    assert result.projects[0].path == project_a
    assert result.projects[1].path == project_b


def test_load_config_malformed_yaml(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config_dir = tmp_path / ".sdd-tui"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text(":::invalid:::\n")
    result = load_config()
    assert result == AppConfig(projects=[])


def test_load_config_no_projects_key(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    config_dir = tmp_path / ".sdd-tui"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text("other_key: value\n")
    result = load_config()
    assert result == AppConfig(projects=[])


def test_parse_config_expands_tilde():
    text = "projects:\n  - path: ~/myproject\n"
    result = _parse_config(text)
    assert len(result.projects) == 1
    # ~ is expanded — path is absolute and does not contain ~
    assert result.projects[0].path.is_absolute()
    assert "~" not in str(result.projects[0].path)
    assert result.projects[0].path.name == "myproject"


def test_parse_config_ignores_comments(tmp_path):
    text = "projects:\n  # this is a comment\n  - path: /tmp/x\n"
    result = _parse_config(text)
    assert len(result.projects) == 1
    assert result.projects[0].path == Path("/tmp/x").resolve()


def test_parse_config_stops_at_new_key(tmp_path):
    text = "projects:\n  - path: /tmp/x\nother:\n  - path: /tmp/y\n"
    result = _parse_config(text)
    assert len(result.projects) == 1


def test_parse_config_empty_projects_list(tmp_path):
    text = "projects:\n"
    result = _parse_config(text)
    assert result == AppConfig(projects=[])
