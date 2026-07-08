# ADR-0005: Production Diary

## Decision

OpenDirector will maintain a Production Diary for every project.

The diary records significant domain events, starting with timeline events.

## Rationale

A film is not only the final export. It is a history of creative decisions.

The diary makes that history visible:
- when shots were added,
- why clips were rejected,
- what the reviewer noticed,
- what was regenerated,
- and how the final movie evolved.

## Consequences

Modules should publish meaningful domain events. The diary listens and records them without requiring modules to call it directly.
