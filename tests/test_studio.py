import pytest

from opendirector import Studio
from opendirector.core.artifact import Artifact, ArtifactType
from opendirector.core.task import Task, TaskStatus
from opendirector.kernel import Capability


class FakeExecutor:
    name = "fake_executor"
    capabilities = [Capability(task_type="demo.task", produces=["report"])]

    def can_execute(self, task: Task) -> bool:
        return task.task_type == "demo.task"

    def execute(self, task: Task):
        return [
            Artifact(
                artifact_type=ArtifactType.REPORT,
                title="Demo report",
                data={"ok": True},
                created_by=self.name,
            )
        ]


def test_studio_requires_name():
    with pytest.raises(ValueError):
        Studio("")


def test_studio_register_and_submit():
    studio = Studio("Gilbert Studio")
    studio.register(FakeExecutor())

    task = Task(task_type="demo.task", title="Run demo task")
    artifacts = studio.submit(task)

    assert task.status == TaskStatus.COMPLETED
    assert len(artifacts) == 1
    assert artifacts[0].title == "Demo report"
    assert studio.artifacts == artifacts
