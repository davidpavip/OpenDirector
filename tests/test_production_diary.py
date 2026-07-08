from opendirector.core.event_bus import EventBus
from opendirector.core.timeline import Timeline, StoryBeatEvent
from opendirector.diary.production_diary import ProductionDiary


def test_diary_records_timeline_event(tmp_path):
    bus = EventBus()
    diary = ProductionDiary(tmp_path)
    diary.connect(bus)

    timeline = Timeline(event_bus=bus)
    timeline.add(StoryBeatEvent(start=0, duration=3, goal="Test goal", emotion="hope"))

    output = diary.write()
    text = output.read_text()

    assert "Timeline event added: story_beat" in text
    assert "Test goal" in text
