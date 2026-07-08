from __future__ import annotations

from opendirector.core.task import Task
from opendirector.core.artifact import Artifact
from opendirector.kernel.registry import Registry, Executor


class Kernel:
    def __init__(self) -> None:
        self.registry = Registry()
        self.tasks: list[Task] = []
        self.artifacts: list[Artifact] = []

    def register(self, executor: Executor) -> None:
        self.registry.register(executor)

    def submit(self, task: Task) -> list[Artifact]:
        self.tasks.append(task)

        executors = self.registry.find(task)

        if not executors:
            task.fail(f"No executor found for task type: {task.task_type}")
            return []

        executor = executors[0]

        task.start()

        try:
            artifacts = executor.execute(task)
            task.complete()
            self.artifacts.extend(artifacts)
            return artifacts
        except Exception as exc:
            task.fail(str(exc))
            return []
