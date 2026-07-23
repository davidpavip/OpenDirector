from __future__ import annotations

import pytest

from opendirector.core.timeline import (
    Timeline,
    TimelineEvent,
    VideoClipEvent,
)
from opendirector.core.timestamp import Timestamp
from opendirector.core.track import Track


def test_timestamp_stores_integer_milliseconds():
    timestamp = Timestamp.parse("00:00:03,125")

    assert timestamp.milliseconds == 3125
    assert timestamp.seconds == pytest.approx(3.125)
    assert str(timestamp) == "00:00:03,125"


def test_float_input_means_seconds():
    timestamp = Timestamp.parse(3.125)

    assert timestamp.milliseconds == 3125
    assert timestamp.seconds == pytest.approx(3.125)


def test_integer_input_means_milliseconds():
    timestamp = Timestamp.parse(3125)

    assert timestamp.milliseconds == 3125
    assert timestamp.seconds == pytest.approx(3.125)


def test_timeline_event_uses_exact_internal_time():
    event = TimelineEvent.create(
        start=1.250,
        duration=2.500,
        track=Track.DIALOGUE,
        event_type="dialogue",
        metadata={
            "text": "Are you alive?",
        },
    )

    assert event.start_milliseconds == 1250
    assert event.duration_milliseconds == 2500
    assert event.end_milliseconds == 3750

    assert event.start_seconds == pytest.approx(1.250)
    assert event.end_seconds == pytest.approx(3.750)

    assert str(event.start) == "00:00:01,250"
    assert str(event.end) == "00:00:03,750"


def test_timeline_sorts_by_exact_milliseconds():
    timeline = Timeline()

    later = TimelineEvent.create(
        start=3.0,
        duration=1.0,
        track=Track.MUSIC,
        event_type="music",
    )

    dialogue = TimelineEvent.create(
        start=1.0,
        duration=1.0,
        track=Track.DIALOGUE,
        event_type="dialogue",
    )

    ambience = TimelineEvent.create(
        start=1.0,
        duration=4.0,
        track=Track.AMBIENCE,
        event_type="ambience",
    )

    timeline.extend(
        [
            later,
            dialogue,
            ambience,
        ]
    )

    assert timeline.events() == [
        ambience,
        dialogue,
        later,
    ]


def test_track_filter_accepts_enum_or_string():
    timeline = Timeline()

    dialogue = timeline.add(
        TimelineEvent.create(
            start=1.0,
            duration=2.0,
            track=Track.DIALOGUE,
            event_type="dialogue",
        )
    )

    timeline.add(
        TimelineEvent.create(
            start=0.0,
            duration=5.0,
            track=Track.MUSIC,
            event_type="music",
        )
    )

    assert timeline.by_track(Track.DIALOGUE) == [dialogue]

    assert timeline.by_track("dialogue") == [dialogue]


def test_timeline_exposes_all_time_boundaries():
    timeline = Timeline()

    timeline.add(
        TimelineEvent.create(
            start=0.0,
            duration=5.0,
            track=Track.VIDEO,
            event_type="video_clip",
        )
    )

    timeline.add(
        TimelineEvent.create(
            start=4.0,
            duration=2.0,
            track=Track.MUSIC,
            event_type="music",
        )
    )

    assert timeline.duration_milliseconds == 6000
    assert timeline.duration_seconds == (pytest.approx(6.0))
    assert timeline.duration == pytest.approx(6.0)
    assert str(timeline.duration_timestamp) == "00:00:06,000"


def test_video_clip_event_accepts_seconds():
    event = VideoClipEvent(
        start=0.0,
        duration=5.0,
        clip_path="shot-001.mp4",
        shot_id="shot-001",
        trim_start=0.250,
    )

    assert event.track is Track.VIDEO
    assert event.start_milliseconds == 0
    assert event.duration_milliseconds == 5000

    assert event.metadata["trim_start_milliseconds"] == 250
    assert event.metadata["trim_start_seconds"] == pytest.approx(0.250)


def test_timeline_supports_clip_postproduction_tracks():
    timeline = Timeline()

    timeline.extend(
        [
            TimelineEvent.create(
                start=0.0,
                duration=5.0,
                track=Track.VIDEO,
                event_type="video_clip",
            ),
            TimelineEvent.create(
                start=0.0,
                duration=5.0,
                track=Track.NATIVE_AUDIO,
                event_type="native_audio",
            ),
            TimelineEvent.create(
                start=1.2,
                duration=1.6,
                track=Track.DIALOGUE,
                event_type="dialogue",
            ),
            TimelineEvent.create(
                start=0.5,
                duration=4.0,
                track=Track.NARRATION,
                event_type="narration",
            ),
            TimelineEvent.create(
                start=0.0,
                duration=5.0,
                track=Track.AMBIENCE,
                event_type="ambience",
            ),
            TimelineEvent.create(
                start=0.0,
                duration=5.0,
                track=Track.MUSIC,
                event_type="music",
            ),
            TimelineEvent.create(
                start=1.2,
                duration=1.6,
                track=Track.SUBTITLE,
                event_type="subtitle",
            ),
        ]
    )

    assert len(timeline.events()) == 7
    assert len(timeline.by_track(Track.DIALOGUE)) == 1
    assert len(timeline.by_track(Track.NARRATION)) == 1
    assert len(timeline.by_track(Track.AMBIENCE)) == 1
    assert timeline.duration_milliseconds == 5000


def test_exact_internal_time_renders_as_srt():
    event = TimelineEvent.create(
        start=1.2,
        duration=1.6,
        track=Track.SUBTITLE,
        event_type="subtitle",
    )

    rendered = f"{event.start} --> {event.end}"

    assert rendered == ("00:00:01,200 --> 00:00:02,800")


def test_metadata_search_remains_compatible():
    timeline = Timeline()

    dialogue = timeline.add(
        TimelineEvent.create(
            start=1.0,
            duration=2.0,
            track=Track.DIALOGUE,
            event_type="dialogue",
            metadata={
                "speaker": "Boy",
                "language": "English",
            },
        )
    )

    assert timeline.find(
        speaker="Boy",
        language="English",
    ) == [dialogue]
