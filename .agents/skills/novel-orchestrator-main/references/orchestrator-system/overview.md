# Overview

This system supports long-form and open-ended series fiction as a stateful creative project.

It solves for:

- World and timeline consistency.
- Character continuity and evolving relationships.
- Searchable canon and dynamic state.
- Chapter-to-chapter carry-forward.
- Foreshadowing, open loops, and sequel seeds.
- Rolling planning without premature final-arc lock-in.
- Quality review that separates structure, scene heat, voice, continuity, and language surface.
- Context compression across long writing timelines.

## Core Principles

- Treat the novel as a stateful project, not isolated chat turns.
- Keep prose and state files separate.
- Use one public skill entry point.
- Keep specialist behavior as internal role packs.
- Load context progressively.
- Let canon accrete from stable scenes.
- Label future ideas as candidates until confirmed.
- Use independent review seats for high-quality output.

## System Boundary

The simplified novel system has one skill:

- `novel-orchestrator-main`

It contains these internal role packs:

- `canon_keeper`
- `plot_planner`
- `scene_writer`
- `voice_editor`
- `continuity_gate`
- `memory_summarizer`

Use sub-agents only as fresh executions of these roles, not as separate skills.
