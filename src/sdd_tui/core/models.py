from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class PhaseState(Enum):
    DONE = "done"
    PENDING = "pending"


@dataclass
class Pipeline:
    propose: PhaseState = PhaseState.PENDING
    spec: PhaseState = PhaseState.PENDING
    design: PhaseState = PhaseState.PENDING
    tasks: PhaseState = PhaseState.PENDING
    apply: PhaseState = PhaseState.PENDING
    verify: PhaseState = PhaseState.PENDING


@dataclass
class Task:
    id: str
    description: str
    done: bool
    amendment: str | None = None


@dataclass
class Change:
    name: str
    path: Path
    pipeline: Pipeline = field(default_factory=Pipeline)


class OpenspecNotFoundError(Exception):
    pass
