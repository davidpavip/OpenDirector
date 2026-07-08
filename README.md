# OpenDirector

## *An Open Source Operating System for Filmmaking*

> **AI agents replace jobs, not people.**

OpenDirector is an open-source filmmaking platform built on one simple belief:

> **Technology should remove repetitive work while people remain the authors of their stories.**

OpenDirector is not designed to replace filmmakers. It provides an AI production crew that helps filmmakers direct, review, edit, critique, and improve their movies.

## Core Philosophy

A movie is **not** a collection of files.

A movie is a collection of **creative events unfolding over time**.

Every image, every camera movement, every line of dialogue, every sound effect, every musical cue, every subtitle, every story beat, every review, and every edit exists on one shared timeline.

## The Timeline is the heart of OpenDirector.

Everything else exists to serve it.

```text
Story
  ↓
Director AI
  ↓
Timeline Core
  ├── Renderer
  ├── Narrator
  ├── Music
  ├── Reviewer
  ↓
Editor AI
  ↓
Final Movie
```

## Architecture Decision #0001

**The Timeline is the central abstraction of OpenDirector.**

Every module communicates through the Timeline.

## Architecture Decision #0002

**Everything is a Timeline Event.**

The Director creates Timeline Events. The Renderer creates Timeline Events. The Narrator creates Timeline Events. The Reviewer analyzes Timeline Events. The Editor composes Timeline Events.

OpenDirector never merely stitches files together. It composes a movie from a timeline of creative events.

## Our Principles

- Stories belong to people.
- AI agents replace jobs, not people.
- AI should automate repetition, not imagination.
- AI should explain its reasoning.
- Every creative decision remains editable.
- Every AI module is replaceable.
- The human creator is always the final authority.

## Quick Start

```bash
cd opendirector
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

opendirector inspect projects/TheLostRobot
opendirector timeline build projects/TheLostRobot --crossfade 0
opendirector timeline inspect projects/TheLostRobot/edl/timeline_v1.json
```

If your `assets/videos/` folder contains rendered clips, export a first cut:

```bash
opendirector timeline export projects/TheLostRobot
```

## Our Beginning

The first OpenDirector project is **The Lost Robot**.

Every great project has an origin story. This one begins with a boy, a small robot, and a conversation about how humans and AI should create together.
