import asyncio

import pytest

from opendirector import Studio
from opendirector.creative import (
    CreativeContext,
    CreativeProgram,
)
from opendirector.professions import (
    Assignment,
    ProfessionContext,
)
from opendirector.thinking import (
    ThinkingContext,
    UnderstandOperator,
    Understanding,
)


def test_understanding_is_first_class_artifact():
    understanding = Understanding(
        intent="Plan a hopeful animated short.",
        goals=("Create emotional connection",),
        constraints=("Family-friendly",),
        confidence=0.8,
    )

    assert understanding.intent == ("Plan a hopeful animated short.")
    assert understanding.is_ready()
    assert not understanding.requires_clarification()


def test_understand_operator_creates_understanding():
    studio = Studio("Gilbert Studio")

    assignment = Assignment(
        profession="Planner",
        objective=("Create three distinct production blueprint candidates."),
        deliverable_type="BlueprintSeed[]",
        constraints=(
            "Family-friendly",
            "Maximum duration: 10 minutes",
        ),
        metadata={
            "goals": [
                "Preserve the emotional relationship",
                "Use the smallest effective cast",
            ],
            "audience": ["Family"],
        },
    )

    profession_context = ProfessionContext(
        values=(
            "Human creative ownership",
            "Do not glorify violence",
        ),
        education=("A short film should use a focused story structure",),
        experience=("Two primary roles worked well in the last production",),
        source=("# Creative Brief\n\n" "A lonely boy discovers an abandoned robot."),
        production="The Little Robot",
    )

    result = asyncio.run(
        studio.run(
            CreativeProgram(
                name="Planner Understanding",
                operators=[
                    UnderstandOperator(),
                ],
            ),
            CreativeContext(
                thinking=ThinkingContext(
                    assignment=assignment,
                    profession_context=profession_context,
                )
            ),
        )
    )

    assert result.thinking is not None
    understanding = result.thinking.understanding

    assert understanding is not None
    assert understanding.intent == assignment.objective

    assert understanding.goals == (
        "Preserve the emotional relationship",
        "Use the smallest effective cast",
    )

    assert understanding.audience == ("Family",)

    assert understanding.constraints == (
        "Family-friendly",
        "Maximum duration: 10 minutes",
    )

    assert understanding.unknowns == ()
    assert understanding.confidence >= 0.7
    assert result.metadata["understanding_ready"] is True


def test_missing_source_requires_clarification():
    studio = Studio("Gilbert Studio")

    result = asyncio.run(
        studio.run(
            CreativeProgram(
                name="Incomplete Understanding",
                operators=[
                    UnderstandOperator(),
                ],
            ),
            CreativeContext(
                thinking=ThinkingContext(
                    assignment=Assignment(
                        profession="Planner",
                        objective="Plan a production.",
                    ),
                    profession_context=ProfessionContext(
                        values=("Protect human intent",),
                    ),
                )
            ),
        )
    )

    assert result.thinking is not None
    understanding = result.thinking.understanding

    assert understanding is not None
    assert "No normalized source context was supplied." in understanding.unknowns
    assert "The expected deliverable type is not specified." in understanding.unknowns
    assert understanding.requires_clarification()


def test_understand_operator_requires_thinking_context():
    studio = Studio("Gilbert Studio")

    with pytest.raises(
        ValueError,
        match="CreativeContext.thinking",
    ):
        asyncio.run(
            studio.run(
                CreativeProgram(
                    name="Missing Thinking Context",
                    operators=[
                        UnderstandOperator(),
                    ],
                ),
                CreativeContext(),
            )
        )


def test_values_are_preserved_as_governing_context():
    studio = Studio("Gilbert Studio")

    values = (
        "Human imagination defines the destination",
        "Values override education and experience",
    )

    result = asyncio.run(
        studio.run(
            CreativeProgram(
                name="Values Understanding",
                operators=[
                    UnderstandOperator(),
                ],
            ),
            CreativeContext(
                thinking=ThinkingContext(
                    assignment=Assignment(
                        profession="Planner",
                        objective="Plan a short film.",
                        deliverable_type="BlueprintSeed[]",
                    ),
                    profession_context=ProfessionContext(
                        values=values,
                        source="# Creative Brief\n\nA short story.",
                    ),
                )
            ),
        )
    )

    assert result.thinking is not None
    assert result.thinking.profession_context.values == values

    understanding = result.thinking.understanding
    assert understanding is not None
    assert understanding.metadata["values_loaded"] == 2
