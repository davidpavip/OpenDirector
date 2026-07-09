# ADR-0016: Intent Is the Source of Creative Truth

## Status

Proposed

## Context

OpenDirector is not built around prompts, files, renderers, or timelines.

OpenDirector is built around creative evolution.

For creative evolution to work, every agent needs a shared understanding of what the work is trying to become.

Without a stable source of creative truth, agents may optimize for different goals:

- A renderer may optimize visual quality.
- A reviewer may optimize technical correctness.
- An editor may optimize pacing.
- A producer may optimize cost.
- A model may optimize prompt compliance.

Those are useful, but they are not the same as the creator's intent.

OpenDirector therefore needs a first-class object that represents the human creator's purpose.

That object is `Intent`.

## Decision

OpenDirector will treat `Intent` as the immutable source of creative truth for a Movie, Scene, CandidateSet, or other creative work.

Intent defines **why** the creative work exists.

It may include:

- audience
- emotion
- message
- tone
- style
- constraints
- priorities
- success definition
- creator notes

Intent is not a prompt.

A prompt is an implementation detail used by a specific model or renderer.

Intent is model-independent.

## Consequences

### Positive

- AI agents share the same North Star.
- Reviewers can evaluate candidates against intent.
- Evolution can measure whether a candidate moves closer to intent.
- Renderers can generate prompts from intent without owning the creative purpose.
- Future non-prompt-based models can still use the same intent object.
- Creative decisions become more explainable and reproducible.

### Negative

- More structure is required before generation.
- Some users may initially prefer simple prompts.
- Intent design must remain flexible enough for many creative domains.

## Rules

1. Intent is immutable.
2. Changing intent creates a new intent version.
3. Intent is not a prompt.
4. Prompts may be derived from intent.
5. Reviewers evaluate candidates against intent.
6. Evolution improves candidates toward intent.
7. Human creators own intent.

## Example

```python
intent = Intent(
    audience="family",
    emotion="hope",
    message="Never give up.",
    success_definition="The audience should feel emotionally moved by the ending.",
    constraints=[
        "No graphic violence",
        "PG tone",
    ],
    priorities=[
        "Story",
        "Emotion",
        "Visual beauty",
    ],
)
