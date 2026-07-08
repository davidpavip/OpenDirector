# OpenDirector

> **AI agents replace jobs, not people.**  
> **Everything is a Timeline Event.**

OpenDirector is an open-source operating system for filmmaking.

## Core 0.4 — Production Diary

This version adds the first module that *reacts* to the Event Bus:

- `EventBus`
- `Timeline`
- `TimelineEvent`
- `ProductionDiary`
- `DiaryEntry`
- CLI demo command

The Production Diary listens to domain events and records the creative history of a movie project.

## Try it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
opendirector diary demo projects/TheLostRobot
cat projects/TheLostRobot/diary/production_diary.md
python3 -m pytest -q
```

## Architecture

```text
Timeline.add(event)
        ↓
EventBus.publish("timeline.event_added")
        ↓
ProductionDiary records what happened
```

The diary is the first example of OpenDirector's reactive architecture.
