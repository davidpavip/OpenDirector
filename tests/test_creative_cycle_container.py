import asyncio

import pytest

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeCycle,
    CreativeOperator,
    CreativeProgram,
)


class RecordOperator(CreativeOperator):
    def __init__(self, name: str) -> None:
        self.name = name

    async def execute(self, context: CreativeContext) -> CreativeContext:
        context.metadata.setdefault("execution_order", []).append(self.name)
        return context


def test_cycle_requires_name():
    with pytest.raises(ValueError, match="cannot be empty"):
        CreativeCycle(name="")


def test_program_runs_cycle_operators_in_order():
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

    result = asyncio.run(
        studio.run(
            program,
            CreativeContext(),
        )
    )

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
    assert result.metadata["cycle_reports"] == [
        {
            "cycle_name": "Opening Scene Cycle",
            "completed_operators": [
                "create",
                "review",
                "select",
            ],
        }
    ]


def test_program_runs_multiple_cycles_in_order():
    studio = Studio("Gilbert Studio")

    program = CreativeProgram(
        name="Two Cycle Program",
        cycles=[
            CreativeCycle(
                name="Exploration",
                operators=[
                    RecordOperator("create"),
                    RecordOperator("review"),
                ],
            ),
            CreativeCycle(
                name="Decision",
                operators=[
                    RecordOperator("select"),
                ],
            ),
        ],
    )

    result = asyncio.run(studio.run(program, CreativeContext()))

    assert result.metadata["execution_order"] == [
        "create",
        "review",
        "select",
    ]
    assert result.metadata["completed_cycles"] == [
        "Exploration",
        "Decision",
    ]


def test_program_rejects_cycles_and_direct_operators_together():
    with pytest.raises(ValueError, match="both cycles and direct operators"):
        CreativeProgram(
            name="Invalid Program",
            cycles=[CreativeCycle(name="Cycle")],
            operators=[RecordOperator("create")],
        )
