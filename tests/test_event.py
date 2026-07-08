from datetime import datetime, timezone

import pytest

from opendirector.core.event import DomainEvent, EventId


def test_domain_event_requires_name():
    with pytest.raises(ValueError):
        DomainEvent(name="")


def test_domain_event_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError):
        DomainEvent(
            name="project.opened",
            occurred_at=datetime(2026, 7, 8, 12, 0, 0),
        )


def test_domain_event_to_dict_is_json_friendly():
    event = DomainEvent(
        name="render.finished",
        payload={"shot_id": "shot_001", "path": "assets/videos/shot_001.mp4"},
        occurred_at=datetime(2026, 7, 8, 12, 0, 0, tzinfo=timezone.utc),
        source="test",
    )

    data = event.to_dict()

    assert data["name"] == "render.finished"
    assert data["payload"]["shot_id"] == "shot_001"
    assert data["occurred_at"] == "2026-07-08T12:00:00+00:00"
    assert data["source"] == "test"
    assert isinstance(data["id"], str)


def test_event_id_is_stringable():
    event_id = EventId("abc")
    assert str(event_id) == "abc"
