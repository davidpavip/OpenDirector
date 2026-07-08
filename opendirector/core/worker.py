from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from opendirector.core.artifact import Artifact
from opendirector.core.task import Task


@dataclass
class WorkerCapability:
    task_type: str
    produces: list[str] = field(default_factory=list)


class Worker(ABC):
    name: str
    role: str
    capabilities: list[WorkerCapability]

    @abstractmethod
    def can_execute(self, task: Task) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(self, task: Task) -> list[Artifact]:
        raise NotImplementedError
