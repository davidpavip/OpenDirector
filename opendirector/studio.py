from __future__ import annotations

from opendirector.core.artifact import Artifact
from opendirector.core.task import Task
from opendirector.kernel.kernel import Kernel
from opendirector.kernel.registry import Executor
from opendirector.core.movie import Movie
from opendirector.core.intent import Intent
from opendirector.creative import CreativeContext, CreativeEngine, CreativeProgram
from opendirector.crew import Crew
from opendirector.providers import ProviderRegistry
from opendirector.knowledge import KnowledgeBase
from opendirector.creative import (
    CreativeContext,
    CreativeEngine,
    CreativeProgram,
)
from opendirector.planning import (
    PlanningContext,
    PlanningProgram,
)
from opendirector.professions import Profession, ProfessionRegistry


class Studio:
    """Primary user-facing API for OpenDirector."""

    def __init__(self, name: str):
        if not name.strip():
            raise ValueError("Studio name cannot be empty")
        self.movies: list[Movie] = []
        self.name = name
        self.kernel = Kernel()
        self.movies: list[Movie] = []
        self.creative_engine = CreativeEngine()
        self.crew = Crew()
        self.providers = ProviderRegistry()
        self.knowledge = KnowledgeBase()
        self.professions = ProfessionRegistry()

    async def run(
        self,
        program: CreativeProgram,
        context: CreativeContext,
    ) -> CreativeContext:

        return await self.creative_engine.run(
            program,
            context,
        )

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

    def create_movie(
        self,
        title: str,
        description: str = "",
        intent: Intent | None = None,
    ) -> Movie:
        movie = Movie(title=title, description=description, intent=intent)
        self.movies.append(movie)
        return movie

    ##    async def plan(
    ##        self,
    ##        program: PlanningProgram,
    ##        context: PlanningContext,
    ##    ) -> PlanningContext:
    ##        return await self.planning_engine.run(program, context)

    async def plan(
        self,
        program: PlanningProgram,
        context: PlanningContext,
    ) -> PlanningContext:
        creative_context = CreativeContext(
            planning=context,
        )

        result = await self.run(
            program,
            creative_context,
        )

        if result.planning is None:
            raise RuntimeError("Planning program completed without PlanningContext")

        result.planning.metadata["planning_program"] = program.name

        result.planning.metadata["completed_planning_operators"] = list(
            result.metadata.get(
                "completed_operators",
                [],
            )
        )
        return result.planning

    def register_profession(
        self,
        profession: Profession,
    ) -> Profession:
        return self.professions.register(profession)
