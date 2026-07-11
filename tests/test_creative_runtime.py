import asyncio

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeOperator,
    CreativeProgram,
)


class RecordOperator(CreativeOperator):
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    async def execute(self, context: CreativeContext) -> CreativeContext:
        context.record(self.name, self.value)
        return context


def test_creative_program_runs_in_order():
    studio = Studio("Gilbert Studio")

    program = CreativeProgram(
        name="Opening Scene Program",
        operators=[
            RecordOperator("create", "done"),
            RecordOperator("review", "done"),
            RecordOperator("select", "done"),
        ],
    )

    context = CreativeContext()
    result = asyncio.run(studio.run(program, context))

    assert result is context
    assert result.metadata["create"] == "done"
    assert result.metadata["review"] == "done"
    assert result.metadata["select"] == "done"
    assert result.metadata["completed_operators"] == [
        "create",
        "review",
        "select",
    ]


def test_empty_program_runs_successfully():
    studio = Studio("Gilbert Studio")
    program = CreativeProgram(name="Empty Program")
    context = CreativeContext()

    result = asyncio.run(studio.run(program, context))

    assert result.metadata["program_name"] == "Empty Program"
    assert result.metadata["completed_operators"] == []
