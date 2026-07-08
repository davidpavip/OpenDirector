# ADR-0002: Everything is a Timeline Event

## Status
Accepted

## Context
A filmmaking system needs one shared language across many creative roles.

## Decision
Everything meaningful in OpenDirector is represented as a Timeline Event.

Examples:

- StoryBeatEvent
- VideoClipEvent
- AudioEvent
- MusicEvent
- SoundEffectEvent
- SubtitleEvent
- CameraEvent
- TransitionEvent
- ReviewEvent
- DirectorNoteEvent

## Consequences
The timeline can hold not only media, but also intent, emotion, review comments, and director notes.

The Reviewer can compare intent against actual rendered media.

The Editor can compose a movie from creative events instead of blindly concatenating files.
