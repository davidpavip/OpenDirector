# Timestamp

## Decision

OpenDirector uses SRT-style timestamps for timeline time:

```text
HH:MM:SS,mmm
```

Example:

```text
00:01:13,500
```

## Why

This is readable by filmmakers, subtitle tools, FFmpeg workflows, and humans.

Internally, `Timestamp` stores integer milliseconds to avoid floating-point rounding errors.

## Accepted Inputs

```python
Timestamp.parse("00:01:13,500")
Timestamp.parse("00:01:13.500")
Timestamp.parse("73.5")
Timestamp.parse(73.5)
Timestamp.parse(73500)
```

All output is canonical:

```text
00:01:13,500
```

## Rule

Timeline code should not use floating-point seconds internally.
