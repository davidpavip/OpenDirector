from __future__ import annotations

from dataclasses import replace

from opendirector.planning.context import PlanningContext
from opendirector.planning.models import (
    Profession,
    RoleAssignment,
    StoryRole,
)
from opendirector.planning.operator import PlanningOperator


class DefineIntentOperator(PlanningOperator):
    name = "define_intent"

    def __init__(self, intent_summary: str) -> None:
        if not intent_summary.strip():
            raise ValueError("Intent summary cannot be empty")
        self.intent_summary = intent_summary

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        context.blueprint = replace(
            context.blueprint,
            intent_summary=self.intent_summary,
        )
        return context


class DesignStoryOperator(PlanningOperator):
    name = "design_story"

    def __init__(self, story_summary: str) -> None:
        if not story_summary.strip():
            raise ValueError("Story summary cannot be empty")
        self.story_summary = story_summary

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        context.blueprint = replace(
            context.blueprint,
            story_summary=self.story_summary,
        )
        return context


class DefineStoryRolesOperator(PlanningOperator):
    name = "define_story_roles"

    def __init__(self, roles: list[StoryRole]) -> None:
        self.roles = tuple(roles)

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        context.blueprint = replace(
            context.blueprint,
            story_roles=self.roles,
        )
        return context


class DefineProfessionsOperator(PlanningOperator):
    name = "define_professions"

    def __init__(self, professions: list[Profession]) -> None:
        self.professions = tuple(professions)

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        context.blueprint = replace(
            context.blueprint,
            professions=self.professions,
        )
        return context


class AssignProfessionsOperator(PlanningOperator):
    name = "assign_professions"

    def __init__(self, assignments: list[RoleAssignment]) -> None:
        self.assignments = tuple(assignments)

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        available_professions = {
            profession.name for profession in context.blueprint.professions
        }

        unknown = [
            assignment.profession_name
            for assignment in self.assignments
            if assignment.profession_name not in available_professions
        ]

        if unknown:
            raise ValueError(
                "Assignments reference undefined professions: " + ", ".join(unknown)
            )

        context.blueprint = replace(
            context.blueprint,
            assignments=self.assignments,
        )
        return context


class ApproveBlueprintOperator(PlanningOperator):
    name = "approve_blueprint"

    def __init__(self, approved_by: str) -> None:
        self.approved_by = approved_by

    async def execute(
        self,
        context: PlanningContext,
    ) -> PlanningContext:
        assert context.blueprint is not None

        context.blueprint = context.blueprint.approve(approved_by=self.approved_by)
        context.record("blueprint_approved", True)
        context.record("blueprint_version", context.blueprint.version)

        return context
