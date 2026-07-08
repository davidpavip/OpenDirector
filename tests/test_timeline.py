from opendirector.core.timeline import Timeline, TimelineEvent


def test_timeline_duration_and_order():
    t = Timeline()
    t.add(TimelineEvent(id="b", kind="video_clip", track="video", start=3, duration=2))
    t.add(TimelineEvent(id="a", kind="story_beat", track="story", start=0, duration=1))
    assert [e.id for e in t.events] == ["a", "b"]
    assert t.duration == 5
