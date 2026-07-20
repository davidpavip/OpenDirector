from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from opendirector import Studio
from opendirector.applications.blueprint_renderer import (
    BlueprintMarkdownRenderer,
)
from opendirector.applications.little_robot_planning import (
    build_little_robot_planning,
)
from opendirector.applications.planning_program import (
    build_planning_program,
)
from opendirector.applications.planning_renderer import (
    PlanningMarkdownRenderer,
)
from opendirector.applications.production_io import (
    ProductionIO,
    ProductionPaths,
)
from opendirector.applications.workspace_initializer import (
    WorkspaceInitializer,
)
from opendirector.creative import CreativeContext
from opendirector.crew import Editor
from opendirector.planning import (
    AssignmentMode,
    ProductionBlueprint,
    RoleAssignment,
)
from opendirector.providers import MockLanguageProvider

from opendirector.production import ProductionSpecificationParser, ProductionWorkspace


class PlanningApplication:
    """Plan a production from normalized Markdown.

    The application coordinates:

    - production file loading;
    - blueprint evolution;
    - scene-centered planning artifacts;
    - runtime workspace initialization;
    - human approval;
    - blueprint persistence.

    The Creative Engine owns execution.
    The Evolution Engine owns blueprint evolution.
    """

    def __init__(
        self,
        studio: Studio | None = None,
        production_io: ProductionIO | None = None,
        renderer: BlueprintMarkdownRenderer | None = None,
        planning_renderer: PlanningMarkdownRenderer | None = None,
        workspace_initializer: WorkspaceInitializer | None = None,
        specification_parser: ProductionSpecificationParser | None = None,
    ) -> None:
        self.studio = studio or self._build_default_studio()
        self.production_io = production_io or ProductionIO()
        self.renderer = renderer or BlueprintMarkdownRenderer()
        self.planning_renderer = planning_renderer or PlanningMarkdownRenderer()
        self.workspace_initializer = workspace_initializer or WorkspaceInitializer()
        self.specification_parser = (
            specification_parser or ProductionSpecificationParser()
        )

    async def run(
        self,
        production_dir: Path,
        approved_by: str = "Gilbert",
    ) -> Path:
        """Run planning and return the generated blueprint path."""

        paths = ProductionPaths.from_root(production_dir)
        source = self.production_io.load_source(paths)

        production_specification = self.specification_parser.parse(source.content)

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

        # Build and save the human-editable scene-centered notebook.
        planning_document = build_little_robot_planning(draft)

        planning_markdown = self.planning_renderer.render(planning_document)

        self.production_io.save_planning(
            paths=paths,
            markdown=planning_markdown,
        )

        # Initialize machine-readable production and scene state.
        self.workspace_initializer.initialize(
            workspace=ProductionWorkspace.from_root(production_dir),
            document=planning_document,
        )

        # Human approval remains a separate boundary.
        approved = draft.approve(approved_by)

        blueprint_markdown = self.renderer.render(
            blueprint=approved,
            production_specification=production_specification,
        )

        blueprint_path, _ = self.production_io.save_blueprint(
            paths=paths,
            markdown=blueprint_markdown,
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
