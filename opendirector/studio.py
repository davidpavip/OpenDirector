from __future__ import annotations

from opendirector.core.artifact import Artifact
from opendirector.core.task import Task
from opendirector.kernel.kernel import Kernel
from opendirector.kernel.registry import Executor
from opendirector.core.movie import Movie


class Studio:
    """Primary user-facing API for OpenDirector."""

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Studio name cannot be empty")
        self.movies: list[Movie] = []
        self.name = name
        self.kernel = Kernel()
        self.movies: list[Movie] = []

    @property
    def registry(self):
        return self.kernel.registry

    @property
    def tasks(self) -> list[Task]:
        return self.kernel.tasks

    @property
    def artifacts(self) -> list[Artifact]:
        return self.kernel.artifacts

    def register(self, executor: Executor) -> None:
        self.kernel.register(executor)

    def submit(self, task: Task) -> list[Artifact]:
        return self.kernel.submit(task)

    def __repr__(self) -> str:
        return f"Studio(name={self.name!r})"

    def create_movie(self, title: str, description: str = "") -> Movie:
        movie = Movie(title=title, description=description)
        self.movies.append(movie)
        return movie
