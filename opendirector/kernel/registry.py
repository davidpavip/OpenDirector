from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from opendirector.core.task import Task


@dataclass(frozen=True)
class Capability:
    task_type: str
    produces: list[str] = field(default_factory=list)


class Executor(Protocol):
    name: str
    capabilities: list[Capability]

    def can_execute(self, task: Task) -> bool: ...

    def execute(self, task: Task): ...


class Registry:
    def __init__(self) -> None:
        self._executors: list[Executor] = []

    def register(self, executor: Executor) -> None:
        self._executors.append(executor)

    def find(self, task: Task) -> list[Executor]:
        return [executor for executor in self._executors if executor.can_execute(task)]

    def all(self) -> list[Executor]:
        return list(self._executors)
