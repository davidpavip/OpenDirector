from __future__ import annotations

from enum import StrEnum


class Track(StrEnum):
    STORY = "story"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    DIALOGUE = "dialogue"
    SUBTITLE = "subtitle"
    CAMERA = "camera"
    REVIEW = "review"
    NOTES = "notes"
    MARKER = "marker"
