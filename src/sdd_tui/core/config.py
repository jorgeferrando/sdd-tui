from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectConfig:
    path: Path


@dataclass
class AppConfig:
    projects: list[ProjectConfig] = field(default_factory=list)


def load_config() -> AppConfig:
    config_path = Path.home() / ".sdd-tui" / "config.yaml"
    if not config_path.exists():
        return AppConfig()
    try:
        return _parse_config(config_path.read_text(errors="replace"))
    except Exception:
        return AppConfig()


def _parse_config(text: str) -> AppConfig:
    projects: list[ProjectConfig] = []
    in_projects = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "projects:":
            in_projects = True
            continue
        if in_projects:
            m = re.match(r"\s*-\s+path:\s+(.+)", line)
            if m:
                path_str = m.group(1).strip()
                path = Path(path_str).expanduser().resolve()
                projects.append(ProjectConfig(path=path))
            elif stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                in_projects = False
    return AppConfig(projects=projects)
