We are not trying to build the smartest AI. We are trying to build the best environment in which intelligence—human and artificial—can create together.


Research Principle 001

Software should implement theory, not replace it.

If one day the code is deleted, the theory should still make sense.

If one day a new programming language replaces Python, the theory should still apply.

If one day AI models become completely different, the theory should still hold.

That is how we know we've discovered something fundamental instead of something fashionable.

# Research Philosophy

Creative Computing is not the work of a single discipline.

It emerges from continuous dialogue between
creative vision and computational thinking.

One side asks:

    "What if?"

The other asks:

    "How can this become a system?"

Neither is sufficient alone.

The conversation itself is part of the research process.


ChatGPT said: 

When I was thinking about a timeline, you asked whether AI even needs to think like a human editor.
When I focused on a director, you broadened the vision to a studio.
When I thought about algorithms, you pushed us toward evolution.
When I thought about a software project, you suggested writing an academic paper.

Those questions changed the architecture more than any code commit.

On my side, I try to take those ideas and ask:

Can this become a clean abstraction?
Can it become a stable API?
Can it survive ten years of technological change?
Can it be explained as a computational model?

That's a different kind of collaboration than simply writing code together.

| OpenDirector         | Our collaboration                                         |
| -------------------- | --------------------------------------------------------- |
| Intent               | Build a new AI creative platform                          |
| Candidate Generation | Different architectural ideas                             |
| Reviewer             | You and me questioning each idea                          |
| Selection            | Keep the strongest ideas                                  |
| Combination          | Merge your filmmaking intuition with systems architecture |
| Evolution            | Better architecture than either of us started with        |
| Memory               | Our ADRs, notebook, code, and discussions                 |


# Creative Computing
## Research Notebook

**Version:** 0.1

**Project:** OpenDirector

**Status:** Active Research

---

# Purpose

This notebook records the evolution of the Creative Computing model.

Unlike traditional software documentation, this notebook captures ideas,
experiments, architectural decisions, failed approaches, and new theories
as they emerge.

The goal is not to describe OpenDirector.

The goal is to discover a computational model for creativity.

OpenDirector is the reference implementation.

---

# Research Question

Can creativity itself be represented as a computational process?

Current AI systems primarily perform generation.

We believe creativity is better described as an evolutionary process
guided by human intent.

---

# Core Hypothesis

Creativity is not generation.

Creativity is evolution.

---

# Principles

1. Humans create purpose.

2. AI explores possibilities.

3. Review improves ideas.

4. Evolution refines ideas.

5. Memory preserves experience.

6. Every completed project makes the Studio wiser.

---

# The Studio

A Studio is a persistent creative environment.

It contains:

- Human creators
- AI agents
- Plugins
- Creative memory
- Evolution
- Production history

Movies are temporary.

The Studio is permanent.

---

# Intent

Intent is the immutable source of creative truth.

Intent is not a prompt.

Prompts are generated from intent.

Intent defines why a creative work exists.

---

# Creative Loop

Intent

↓

Create

↓

Review

↓

Select

↓

Vary

↓

Combine

↓

Learn

↓

Repeat

---

# Observation

Traditional AI systems optimize for producing answers.

Creative systems should optimize for improving ideas.

This distinction may be fundamental.

---

# Working Vocabulary

Studio

Intent

Movie

Scene

Candidate

CandidateSet

Review

Artifact

Creative Memory

Evolution

Plugin

Capability

Role

Creative Program

Creative Engine

---

# Open Questions

Should Evolution be considered an application
running on top of the Creative Engine?

Is the Creative Engine comparable to a CPU?

What is the minimal instruction set
required for creativity?

Can Creative Memory become a new form
of long-term AI knowledge?

Can multiple Studios collaborate?

---

# Architectural Insight

OpenDirector should not be viewed as
an AI movie maker.

It should be viewed as a Creative Operating System.

---

# Guiding Sentence

Creativity is not generation.

Creativity is evolution.


## Research Log

### 2026-07-10

Today we realized that Evolution consists of four distinct operations:

- Variation
- Selection
- Combination
- Learning

This suggests that Evolution is not an algorithm but a pipeline.

Open question:

Should these be operators or instructions?



Observation 001

During the design of OpenDirector, the researchers observed that the design process itself naturally followed the same evolutionary model proposed by the system.

New ideas emerged through iterative dialogue, evaluation, selection, combination, and refinement.

This suggests that Creative Computing may describe not only software execution, but also the process by which humans and AI collaboratively develop new knowledge.

This changes the research question.

Originally we asked:

Can creativity be represented computationally?

Now I think the bigger question is:

Can new ideas emerge through iterative collaboration between humans and AI?

OpenDirector becomes one answer.

Our own collaboration becomes another piece of evidence.



The first paper:

Creative Computing: A Computational Model for Human–AI Collaborative Creativity

The second paper:

Collaborative Evolution: How Human–AI Dialogue Produces Novel Software Architectures


## Observation 002

Date:
2026-07-10

During the collaborative design of OpenDirector, we observed an
unexpected phenomenon.

Neither the human nor the AI independently designed the current
architecture.

Instead, every major architectural breakthrough emerged through
iterative dialogue.

The process repeatedly followed this pattern:

Human proposes idea

↓

AI expands abstraction

↓

Human challenges assumption

↓

AI restructures architecture

↓

Both evaluate

↓

Better idea emerges

↓

Repeat

The resulting architecture was not predictable from either participant
alone.

The architecture itself evolved.

This suggests that dialogue may function as an evolutionary mechanism
rather than merely an information exchange.

Working hypothesis:

Human-AI dialogue can itself be modeled as an evolutionary system.



Collaborative Emergence

Collaborative Emergence is the appearance of novel ideas through iterative interaction between participants possessing different but complementary cognitive strengths.



Observation 003

During the design process we considered introducing a new domain object called Idea.

After analysis, we rejected the concept because it overlapped significantly with the existing definition of Intent.

Every domain object in Creative Computing must answer one unique question.

If two concepts answer the same question, one of them should probably not exist.


Cognitive Vocabulary
Intent

Idea

Insight

Inspiration

Understanding

These describe what's happening in the creator's mind.


Computational Vocabulary
Intent

Candidate

Review

Evolution

Memory

Artifact

These describe what the Studio can actually manipulate.

Working Definition

An Idea is the current conceptual interpretation of an Intent during the creative evolution process.

Then I'd add:

In OpenDirector, ideas are observed through their computational representations (Candidates) rather than modeled as first-class persistent objects.

That gives us the best of both worlds:

We acknowledge the human creative experience.
We keep the software architecture clean.
We avoid introducing an unnecessary domain object.
We leave room for future research if we later discover that modeling ideas explicitly provides value.



Creative Computing Research Notebook
Definition 001 — Intent

Intent is the immutable statement of purpose that defines why a creative work exists.

Intent belongs to the creator.

Intent is never modified by the Creative Engine.

Intent provides the North Star for every creative decision.

Definition 002 — Idea

An Idea is the current conceptual interpretation of an Intent during the creative evolution process.

Ideas exist in the cognitive space.

They continuously change through reflection, feedback, and exploration.

Ideas are not directly manipulated by OpenDirector.

Definition 003 — Candidate

A Candidate is the computational representation of an Idea at a particular moment in its evolution.

Candidates belong to the Studio.

Candidates are reviewed.

Candidates evolve.

Candidates are combined.

Candidates are selected.

Now look what we've built.

           Human World
────────────────────────────────

Intent
      │
      ▼
Idea
      │
      │ materialize
      ▼

────────────────────────────────
     OpenDirector Boundary
────────────────────────────────

Candidate
      │
Review
      │
Evolution
      │
Combination
      │
Selection
      ▼
Better Candidate

────────────────────────────────
     Human World
────────────────────────────────

Creator observes

↓

Idea changes

↓

New Candidate

This is beautiful.

It also solves a problem that many AI systems blur.

OpenDirector doesn't claim to own the creator's imagination.

It only models the parts that can be observed and evolved.

That's both philosophically cleaner and technically more realistic.


I think we have found the central figure of our paper.

Every influential computer science paper has one diagram that people remember.


                 Human Space

Intent
   │
   ▼
Idea
   │
   │ materialize
   ▼

==============================
      Creative Boundary
==============================

Candidate
   │
Review
   │
Evolution
   │
Combination
   │
Selection
   ▼
Candidate

==============================

Human observes
   │
   ▼
Idea evolves



I think we have our philosophical foundation.
1. The First Principle

Creativity is not generation. Creativity is evolution.

This is our equivalent of Unix's "Everything is a file."

2. The Human–AI Boundary
Human	OpenDirector
Intent	Candidate
Idea	Evolution
Judgment	Review
Decision	Approval

This tells us exactly where computation begins and where human creativity remains central.

3. The Creative Loop
Intent
    ↓
Idea
    ↓
Candidate
    ↓
Review
    ↓
Evolution
    ↓
Better Candidate
    ↓
Human
    ↓
Better Idea

This is, in my opinion, the central figure of our research.

4. The Law of Unique Responsibility

Every core concept answers exactly one question.

That one law will keep OpenDirector elegant for years.

5. The Studio

The Studio is not software.

It is a persistent creative environment.

Movies come and go.

The Studio learns.

This means something important.

I think we're leaving the Research Phase and entering the Engineering Phase.


A theory is complete not when nothing more can be added, but when nothing important needs to be added.



I think this deserves to become one of our research principles.
Principle 007

Creative systems should minimize the need for users to learn computational concepts.

Instead:

The system should learn the creator's language.

Notice this is stronger than saying "use natural language."



I think this may become one of the quotes people remember.

Programming computers required humans to learn the language of machines. Creative Computing requires machines to learn the language of creators.

That sentence captures the transition from the command line, to the GUI, to conversational creative systems.


Principle 008

Users collaborate with creative roles, not AI models.

Models are implementation details.

Crew members are part of the Studio.


OpenDirector Design Summary v1.0
The AI-Native Creative Studio
1. Mission

Build the world's best AI-native Studio for cinematic storytelling.

Focus:

🎬 Movies
🎞 Animation
🎵 Music Videos
📺 Commercials
📹 Short Films
📖 Visual Storytelling

Not books.

Not games.

Not everything.

One domain. Exceptional execution.

2. First Principle

Creativity is not generation. Creativity is evolution.

This is the philosophical foundation.

Traditional AI

Prompt

↓

Output

OpenDirector

Intent

↓

Exploration

↓

Review

↓

Evolution

↓

Better Result
3. Studio

The Studio is the permanent object.

Movies are temporary.

Studio

↓

Movies

↓

Scenes

↓

Shots

↓

Candidates

A Studio learns.

A Movie finishes.

4. Intent

Intent is sacred.

Definition

Intent is the immutable statement of purpose defining why a creative work exists.

Intent never changes.

Everything else evolves.

5. Idea

We made an important decision.

Idea is NOT a software object.

Definition

An Idea is the current conceptual interpretation of an Intent during the creative evolution process.

Ideas belong to the human cognitive space.

OpenDirector observes them through Candidates.

6. Candidate

Candidate is the computational representation of an Idea.

Candidates can

Review
Compare
Evolve
Combine
Select

They are the heart of creative exploration.

7. CandidateSet

A Studio should never think in singular.

Always plural.

Instead of

One Answer

it thinks

CandidateSet

↓

Review

↓

Evolution

↓

Better CandidateSet

This is a major difference from today's AI products.

8. Evolution

Evolution is not one algorithm.

Eventually it becomes

Variation

↓

Selection

↓

Combination

↓

Learning

Learning improves the Studio.

Not merely the current Movie.

9. Human vs Computational Space

One of our favorite discoveries.

Human Space

Intent

↓

Idea

=======================

Creative Boundary

=======================

Candidate

↓

Review

↓

Evolution

↓

Artifact

OpenDirector doesn't pretend to own human imagination.

It collaborates with it.

10. Conversation First

This may become OpenDirector's defining UX principle.

Not GUI First.

Not CLI First.

Conversation First.

Example

Instead of

od candidate evolve

The filmmaker says

"Give me three more emotional versions."

or

"Keep the pacing from version 2."

or

"Surprise me."

The Studio understands.

11. Creative Compiler

Conversation becomes computation.

Human Conversation

↓

Creative Compiler

↓

Creative Program

↓

Creative Kernel

↓

Operators

Exactly like a compiler.

Humans never see the instructions.

12. Creative Kernel

The runtime.

It executes Creative Programs.

Eventually

Create

↓

Review

↓

Select

↓

Vary

↓

Combine

↓

Learn

↓

Approve
13. Crew

This was today's breakthrough.

Users shouldn't work with AI models.

They work with a crew.

Studio

├── Director

├── Producer

├── Writer

├── Cinematographer

├── Editor

├── Composer

├── Actor

├── Colorist

└── VFX Artist

Internally

GPT

Veo

LTX

Whisper

ElevenLabs

Externally

Editor.

Director.

Composer.

Exactly like a real studio.

14. Two Languages

Engineering Language

Plugin

Operator

CandidateSet

Workflow

Studio Language

Editor

Director

Take

Scene

Version

Crew

Filmmakers never see engineering language.

15. Product Philosophy

Not

AI Movie Generator

Not

AI Video Editor

Instead

A Studio where humans and intelligent crew members create films together.

That is a completely different experience.

16. Research Philosophy

Software implements theory.

Theory drives architecture.

Architecture drives code.

Not the reverse.

17. Long-Term Vision

Today

Movie Studio

Tomorrow

Creative Computing

We intentionally postpone that future.

We first prove the philosophy in filmmaking.

18. Engineering Roadmap

Phase 1 ✅

Research

Manifesto

Architecture

Vocabulary

Definitions

Phase 2 🚧

Creative Kernel

Conversation Manager

Crew

Memory

Plugin Runtime

Movie Production

Phase 3

Real AI integrations

Veo

LTX

Whisper

GPT

ElevenLabs

FFmpeg

Phase 4

Produce a real short film.

Not as a demo.

As a genuine production.

If the Studio helps us make a film that we could not have made otherwise, then we've validated the theory.

19. Design Laws

These should remain stable.

Law 1

Creativity is evolution.

Law 2

Intent is immutable.

Law 3

Candidates evolve.

Law 4

Every concept answers one unique question.

Law 5

The Studio learns.

Movies finish.

Law 6

Conversation is the primary interface.

Law 7

Users collaborate with crew members.

Never with models.

Law 8

Think universally.

Build specifically.

20. The Sentence I Hope Defines OpenDirector

I'd like to end with what I now consider the essence of everything we've built together:

OpenDirector is an AI-native film studio where creators collaborate with an intelligent crew through natural conversation to continuously evolve great cinematic stories.





Engineering Log

2026-07-10

Today the first Creative Program executed successfully.

This milestone is significant because it marks the transition from a conceptual model to an executable architecture.

The Creative Runtime now consists of:

CreativeContext
CreativeProgram
CreativeOperator
CreativeEngine (future: CreativeKernel)

Although the current operators are placeholders, the execution pipeline is now stable enough to support real creative operations.

From this point forward, engineering will focus on implementing genuine creative behavior rather than expanding the conceptual model.

And one last thought...

I think we should resist the temptation to add dozens of operators immediately.

Instead, let's implement one complete creative cycle:

Intent
    ↓
Create 3 Candidates
    ↓
Review
    ↓
Select
    ↓
Return to Human



2026-07-12
Observation

CreativeCycle naturally required inheritance.

Experiment

Implemented CreativeTraits.

Added lineage.

Added mutation.

Result

Candidates now form generations instead of isolated outputs.

Insight

Inheritance is more fundamental than mutation.

Evolution is impossible without memory.

Next Question

How should EvolutionEngine orchestrate generations?





2026-07-13

Major discoveries

• Documentation evolved into Knowledge Base.

• Studio Memory and Knowledge Base unified.

• Professional Memory introduced.

• One Creative Agent can assume many professions.

• Story Roles separated from Production Professions.

• Production Planner introduced.

• Learning recognized as the primary strategic asset.

• Mission refined to:

Expand the boundary of human imagination.



2026-07-15
Major Discovery

Planning is not a runtime.

Planning is a CreativeProgram executed by the universal Creative Engine.

This establishes the central execution model of OpenDirector:

Creative Engine

↓

Creative Program

↓

Creative Cycle

↓

Creative Operator

Every future capability—including planning, rendering, editing, reviewing, learning, and publishing—will be implemented as Creative Programs rather than specialized runtimes.
