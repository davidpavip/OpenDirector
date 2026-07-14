import pytest

from opendirector import Studio
from opendirector.knowledge import (
    Education,
    Experience,
    KnowledgeBase,
    KnowledgeKind,
    KnowledgeRecord,
    Value,
)


def test_studio_owns_knowledge_base():
    studio = Studio("Gilbert Studio")

    assert isinstance(studio.knowledge, KnowledgeBase)
    assert len(studio.knowledge) == 0


def test_value_has_highest_priority():
    value = Value(
        title="Nonviolent storytelling",
        statement="Avoid glorifying violence.",
    ).to_record()

    education = Education(
        title="Action pacing",
        statement="Frequent action may increase audience engagement.",
        source="Film editing textbook",
    ).to_record()

    experience = Experience(
        title="Action result",
        statement="Fast action scored highly in the previous production.",
        production_id="production-001",
        confidence=0.9,
    ).to_record()

    knowledge = KnowledgeBase()
    knowledge.extend([experience, education, value])

    resolved = knowledge.resolve("editing")

    assert resolved[0].kind is KnowledgeKind.VALUE
    assert resolved[1].kind is KnowledgeKind.EDUCATION
    assert resolved[2].kind is KnowledgeKind.EXPERIENCE


def test_scoped_knowledge_is_retrieved_for_matching_subject():
    knowledge = KnowledgeBase()

    editing = Education(
        title="Editing rhythm",
        statement="Cutting rhythm should support emotional intent.",
        source="Editing handbook",
        scope=("editor", "editing"),
    ).to_record()

    knowledge.add(editing)

    assert knowledge.for_subject("editor") == [editing]
    assert knowledge.for_subject("composer") == []


def test_unscoped_knowledge_applies_everywhere():
    knowledge = KnowledgeBase()

    value = Value(
        title="Human ownership",
        statement="The filmmaker owns the creative vision.",
    ).to_record()

    knowledge.add(value)

    assert knowledge.for_subject("editor") == [value]
    assert knowledge.for_subject("director") == [value]


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="between 0 and 1"):
        KnowledgeRecord(
            kind=KnowledgeKind.EXPERIENCE,
            title="Invalid",
            statement="Invalid confidence.",
            confidence=1.5,
        )


def test_duplicate_record_is_rejected():
    knowledge = KnowledgeBase()

    record = Value(
        title="Intent first",
        statement="Intent governs creative evolution.",
    ).to_record()

    knowledge.add(record)

    with pytest.raises(ValueError, match="already exists"):
        knowledge.add(record)
