# ADR-0001: The Timeline is the central abstraction

## Status
Accepted

## Context
OpenDirector must coordinate story, image generation, video rendering, narration, music, subtitles, reviews, edits, and exports.

A file-folder model is too weak because movies are not folders of assets. Movies are creative events aligned over time.

## Decision
The Timeline is the central abstraction of OpenDirector.

Every major subsystem communicates by reading or writing Timeline Events.

## Consequences
- Renderers produce timeline events.
- Reviewers analyze timeline events.
- Editors compose timeline events.
- Audio, subtitles, and music live on the same timeline as video.
- Future AI agents can be added without changing the core model.
