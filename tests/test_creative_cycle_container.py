import asyncio

import pytest

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeOperator,
    CreativeProgram,
    MaxIterationsCondition,
    MetadataEqualsCondition,
)


class RecordOperator(CreativeOperator):
    def __init__(self, name: str) -> None:
        self.name = name

    async def execute(self, context: CreativeContext) -> CreativeContext:
        context.metadata.setdefault("execution_order", []).append(self.name)
        return context


class CountOperator(CreativeOperator):
    name = "count"

    async def execute(self, context: CreativeContext) -> CreativeContext:
        context.metadata["count"] = context.metadata.get("count", 0) + 1
        return context


def test_cycle_requires_name():
    with pytest.raises(ValueError, match="cannot be empty"):
        CreativeCycle(name="")


def test_cycle_runs_once_by_default():
    studio = Studio("Gilbert Studio")

    cycle = CreativeCycle(
        name="Opening Scene Cycle",
        operators=[
            RecordOperator("create"),
            RecordOperator("review"),
            RecordOperator("select"),
        ],
    )

    program = CreativeProgram(
        name="Opening Scene Program",
        cycles=[cycle],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    assert result.metadata["execution_order"] == [
        "create",
        "review",
        "select",
    ]
    assert result.metadata["completed_cycles"] == [
        "Opening Scene Cycle",
    ]
    assert result.metadata["completed_operators"] == [
        "create",
        "review",
        "select",
    ]

    report = result.metadata["cycle_reports"][0]

    assert report["cycle_name"] == "Opening Scene Cycle"
    assert report["iteration_count"] == 1
    assert report["stop_reason"] == "maximum iterations reached: 1"


def test_cycle_repeats_until_max_iterations():
    studio = Studio("Gilbert Studio")

    cycle = CreativeCycle(
        name="Three Iterations",
        operators=[CountOperator()],
        stopping_condition=MaxIterationsCondition(3),
    )

    program = CreativeProgram(
        name="Iteration Program",
        cycles=[cycle],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    assert result.metadata["count"] == 3
    assert result.metadata["completed_operators"] == [
        "count",
        "count",
        "count",
    ]

    report = result.metadata["cycle_reports"][0]

    assert report["iteration_count"] == 3
    assert len(report["iterations"]) == 3
    assert report["stop_reason"] == "maximum iterations reached: 3"


def test_cycle_stops_when_metadata_condition_is_satisfied():
    studio = Studio("Gilbert Studio")

    cycle = CreativeCycle(
        name="Count Until Three",
        operators=[CountOperator()],
        stopping_condition=MetadataEqualsCondition(
            key="count",
            expected=3,
        ),
        safety_limit=10,
    )

    program = CreativeProgram(
        name="Conditional Program",
        cycles=[cycle],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    assert result.metadata["count"] == 3

    report = result.metadata["cycle_reports"][0]

    assert report["iteration_count"] == 3
    assert "metadata condition satisfied" in report["stop_reason"]


def test_cycle_safety_limit_prevents_infinite_loop():
    studio = Studio("Gilbert Studio")

    cycle = CreativeCycle(
        name="Never Satisfied",
        operators=[CountOperator()],
        stopping_condition=MetadataEqualsCondition(
            key="finished",
            expected=True,
        ),
        safety_limit=4,
    )

    program = CreativeProgram(
        name="Safety Program",
        cycles=[cycle],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    assert result.metadata["count"] == 4

    report = result.metadata["cycle_reports"][0]

    assert report["iteration_count"] == 4
    assert report["stop_reason"] == "cycle safety limit reached: 4"


def test_program_rejects_cycles_and_direct_operators_together():
    with pytest.raises(ValueError, match="both cycles and direct operators"):
        CreativeProgram(
            name="Invalid Program",
            cycles=[CreativeCycle(name="Cycle")],
            operators=[RecordOperator("create")],
        )
