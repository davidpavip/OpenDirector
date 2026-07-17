from __future__ import annotations

from opendirector.planning import PlanningDocument
from opendirector.production import (
    ProductionState,
    ProductionStateStore,
    ProductionWorkspace,
    SceneIndexEntry,
    SceneState,
    ShotState,
)


class WorkspaceInitializer:
    """Create runtime state from a completed PlanningDocument."""

    def __init__(
        self,
        store: ProductionStateStore | None = None,
    ) -> None:
        self.store = store or ProductionStateStore()

    def initialize(
        self,
        workspace: ProductionWorkspace,
        document: PlanningDocument,
    ) -> None:
        production_state = ProductionState(
            production_id=document.production_id,
            title=document.title,
            status="planning",
            current_scene_id=(document.scenes[0].id if document.scenes else None),
            global_constraints=list(document.understanding.constraints),
        )

        self.store.initialize(
            workspace,
            production_state,
        )

        scene_index: list[SceneIndexEntry] = []

        for order, scene in enumerate(
            document.scenes,
            start=1,
        ):
            scene_workspace = workspace.scene(scene.id)

            shot_states = {
                shot.id: ShotState(
                    shot_id=shot.id,
                    status="pending",
                )
                for shot in scene.shots
            }

            scene_state = SceneState(
                scene_id=scene.id,
                title=scene.title,
                planning_stage=scene.status,
                production_stage="not_started",
                status="draft",
                selected_idea_ids=(
                    list(scene.decision.selected_idea_ids)
                    if scene.decision is not None
                    else []
                ),
                continuity={
                    "requirements": list(scene.understanding.continuity_requirements)
                },
                open_questions=list(scene.understanding.unknowns),
                shots=shot_states,
            )

            self.store.save_scene(
                scene_workspace,
                scene_state,
            )

            scene_index.append(
                SceneIndexEntry(
                    scene_id=scene.id,
                    title=scene.title,
                    order=order,
                    status=scene.status,
                )
            )

        self.store.save_scene_index(
            workspace,
            scene_index,
        )
