from opendirector.core.artifact import Artifact, ArtifactType
from opendirector.core.task import Task, TaskStatus


def test_artifact_to_dict():
    artifact = Artifact(
        artifact_type=ArtifactType.VIDEO,
        title="Shot 001 video",
        uri="assets/videos/shot_001.mp4",
        created_by="ltx_renderer",
    )

    data = artifact.to_dict()

    assert data["artifact_type"] == "video"
    assert data["title"] == "Shot 001 video"
    assert data["uri"] == "assets/videos/shot_001.mp4"


def test_task_lifecycle():
    task = Task(
        task_type="render.video",
        title="Render Shot 001",
        payload={"candidate_id": "abc"},
    )

    assert task.status == TaskStatus.NEW

    task.start()
    assert task.status == TaskStatus.RUNNING

    task.complete()
    assert task.status == TaskStatus.COMPLETED


def test_task_failure():
    task = Task(task_type="review.candidate", title="Review Candidate")
    task.fail("missing video")

    assert task.status == TaskStatus.FAILED
    assert task.error == "missing video"
