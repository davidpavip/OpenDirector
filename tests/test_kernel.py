from opendirector.core.artifact import Artifact, ArtifactType
from opendirector.core.task import Task, TaskStatus
from opendirector.kernel import Kernel, Capability


class FakeVideoExecutor:
    name = "fake_video_executor"
    capabilities = [Capability(task_type="render.video", produces=["video"])]

    def can_execute(self, task: Task) -> bool:
        return task.task_type == "render.video"

    def execute(self, task: Task):
        return [
            Artifact(
                artifact_type=ArtifactType.VIDEO,
                title="Fake rendered video",
                uri="assets/videos/fake.mp4",
                created_by=self.name,
            )
        ]


def test_kernel_runs_task_with_registered_executor():
    kernel = Kernel()
    kernel.register(FakeVideoExecutor())

    task = Task(task_type="render.video", title="Render test video")

    artifacts = kernel.submit(task)

    assert task.status == TaskStatus.COMPLETED
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type == ArtifactType.VIDEO


def test_kernel_fails_task_without_executor():
    kernel = Kernel()
    task = Task(task_type="render.video", title="Render test video")

    artifacts = kernel.submit(task)

    assert artifacts == []
    assert task.status == TaskStatus.FAILED
    assert "No executor found" in task.error
