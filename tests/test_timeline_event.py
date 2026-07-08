from opendirector.core.timeline_event import TimelineEvent
from opendirector.core.track import Track


def test_timeline_event_end():
    event = TimelineEvent.create(
        start="00:00:10,000",
        duration="00:00:04,500",
        track=Track.VIDEO,
        event_type="video_clip",
    )

    assert str(event.end) == "00:00:14,500"


def test_timeline_event_contains():
    event = TimelineEvent.create(
        start="00:00:10,000",
        duration="00:00:04,000",
        track="video",
        event_type="video_clip",
    )

    assert event.contains("00:00:11,000")
    assert not event.contains("00:00:14,000")


def test_timeline_event_overlap():
    a = TimelineEvent.create(
        start="00:00:10,000",
        duration="00:00:04,000",
        track="video",
        event_type="video_clip",
    )

    b = TimelineEvent.create(
        start="00:00:13,000",
        duration="00:00:04,000",
        track="video",
        event_type="video_clip",
    )

    assert a.overlaps(b)


def test_timeline_event_move():
    event = TimelineEvent.create(
        start="00:00:10,000",
        duration="00:00:04,000",
        track="video",
        event_type="video_clip",
    )

    event.move_to("00:00:20,000")

    assert str(event.start) == "00:00:20,000"
    assert str(event.end) == "00:00:24,000"
