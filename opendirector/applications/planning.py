from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from opendirector import Studio
from opendirector.applications.blueprint_renderer import (
    BlueprintMarkdownRenderer,
)
from opendirector.applications.planning_program import (
    build_planning_program,
)
from opendirector.applications.production_io import (
    ProductionIO,
    ProductionPaths,
)
from opendirector.creative import CreativeContext
from opendirector.crew import Editor
from opendirector.planning import (
    AssignmentMode,
    ProductionBlueprint,
    RoleAssignment,
)
from opendirector.providers import MockLanguageProvider
from opendirector.applications.little_robot_planning import (
    build_little_robot_planning,
)
from opendirector.applications.planning_renderer import (
    PlanningMarkdownRenderer,
)


class PlanningApplication:
    """Plan a production from normalized Markdown.

    The application owns orchestration and file handling. The Creative
    Engine owns execution. The Evolution Engine owns blueprint evolution.
    """

    def __init__(
        self,
        studio: Studio | None = None,
        production_io: ProductionIO | None = None,
        renderer: BlueprintMarkdownRenderer | None = None,
        planning_renderer: PlanningMarkdownRenderer | None = None,
    ) -> None:
        self.studio = studio or self._build_default_studio()
        self.production_io = production_io or ProductionIO()
        self.renderer = renderer or BlueprintMarkdownRenderer()
        self.planning_renderer = planning_renderer or PlanningMarkdownRenderer()

    ##    def __init__(
    ##        self,
    ##        studio: Studio | None = None,
    ##        production_io: ProductionIO | None = None,
    ##        renderer: BlueprintMarkdownRenderer | None = None,
    ##    ) -> None:
    ##        self.studio = studio or self._build_default_studio()
    ##        self.production_io = production_io or ProductionIO()
    ##        self.renderer = renderer or BlueprintMarkdownRenderer()

    async def run(
        self,
        production_dir: Path,
        approved_by: str = "Gilbert",
    ) -> Path:
        paths = ProductionPaths.from_root(production_dir)
        source = self.production_io.load_source(paths)

        template = ProductionBlueprint(source=source)

        program = build_planning_program(
            studio=self.studio,
            template=template,
        )

        result = await self.studio.run(
            program,
            CreativeContext(),
        )

        draft = result.metadata.get("selected_blueprint")

        if not isinstance(draft, ProductionBlueprint):
            raise RuntimeError("Planning completed without a selected blueprint")

        draft = replace(
            draft,
            assignments=self._build_assignments(draft),
        )

        planning_document = build_little_robot_planning(draft)
        planning_markdown = self.planning_renderer.render(planning_document)

        self.production_io.save_planning(
            paths=paths,
            markdown=planning_markdown,
        )

        approved = draft.approve(approved_by)
        markdown = self.renderer.render(approved)

        blueprint_path, _ = self.production_io.save_blueprint(
            paths=paths,
            markdown=markdown,
            version=approved.version,
        )

        return blueprint_path

    def _build_default_studio(self) -> Studio:
        studio = Studio("OpenDirector Studio")

        provider = studio.providers.register(MockLanguageProvider())
        studio.crew.add(Editor(provider))

        return studio

    def _build_assignments(
        self,
        blueprint: ProductionBlueprint,
    ) -> tuple[RoleAssignment, ...]:
        modes = {
            "Director": (
                AssignmentMode.HUMAN,
                "Gilbert",
            ),
            "Screenwriter": (
                AssignmentMode.AI_ASSISTANT,
                "OpenDirector",
            ),
            "Cinematographer": (
                AssignmentMode.AI_ASSISTANT,
                "OpenDirector",
            ),
            "Editor": (
                AssignmentMode.AI_ASSISTANT,
                "OpenDirector",
            ),
            "Animator": (
                AssignmentMode.AI_DELEGATE,
                "OpenDirector",
            ),
            "Composer": (
                AssignmentMode.AI_DELEGATE,
                "OpenDirector",
            ),
            "Sound Designer": (
                AssignmentMode.AI_DELEGATE,
                "OpenDirector",
            ),
        }

        assignments: list[RoleAssignment] = []

        for profession in blueprint.professions:
            mode, performer = modes.get(
                profession.name,
                (
                    AssignmentMode.AI_ASSISTANT,
                    "OpenDirector",
                ),
            )

            assignments.append(
                RoleAssignment(
                    profession_name=profession.name,
                    mode=mode,
                    performer=performer,
                )
            )

        return tuple(assignments)
