# Core Event

## Purpose

`DomainEvent` is the smallest event primitive in OpenDirector.

It represents a fact that happened inside the system.

Examples:

- `project.opened`
- `project.saved`
- `render.started`
- `render.finished`
- `timeline.event_added`

## Design Rules

- Events are immutable.
- Events are timestamped.
- Events have stable IDs.
- Events are JSON-friendly.
- Events describe facts, not commands.

## Important Distinction

Not every `DomainEvent` is a `TimelineEvent`.

For example:

- `render.started` is a domain event.
- `plugin.loaded` is a domain event.
- `project.saved` is a domain event.

But these are not timeline events.

Timeline events will be added in the next module.
