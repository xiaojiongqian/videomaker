# Architecture

## Main Skill

`novel-orchestrator-main` is the single entry point for long-form and series-fiction work.

It is responsible for:

- Understanding the user's writing task.
- Choosing the minimum context to load.
- Selecting the internal role pack.
- Deciding whether work should be serial or parallel.
- Aggregating sub-agent outputs when sub-agents are used.
- Running quality gates.
- Deciding which proposed writebacks are safe.

There are no separate novel sub-skills in the simplified architecture. Former specialist skills now exist as internal role packs.

## Internal Role Packs

- `canon_keeper`
  - Static canon, dynamic state, open loops, foreshadows, timeline, character arcs, and writeback patches.
- `plot_planner`
  - Arc planning, chapter promises, scene beats, reveal order, repair plans, and open-ended sequel entry points.
- `scene_writer`
  - Scene/chapter drafting and targeted prose revision.
- `voice_editor`
  - Dialogue, subtext, character voice, protagonist embodiment, and interaction pressure.
- `continuity_gate`
  - Continuity, causality, knowledge boundaries, language surface, and writeback eligibility.
- `memory_summarizer`
  - Chapter summaries, recent events, carry-forward obligations, state patch proposals.

## Quality Council Layer

When the target is publishable/high-quality text, use `quality_council_loop`:

- `story_engine_seat`
  - role pack: `plot_planner`
  - owns `opening_hook`, `core_event`, `escalation`
- `scene_heat_seat`
  - role pack: `scene_writer`
  - owns `scene_execution`, `ending_hook`
- `voice_embodiment_seat`
  - role pack: `voice_editor`
  - owns `character_embodiment`
- `canon_surface_gate`
  - role pack: `continuity_gate`
  - owns `continuity_causality`, `language_surface`
  - vetoes hard blockers and unsafe writebacks

Use fresh sub-agent sessions for independent council seats when available.

## State Model

Keep prose and state separate:

- Prose artifacts
  - chapters, scenes, drafts, revisions
- Dynamic state
  - `CURRENT_STATE.md`, `OPEN_LOOPS.md`, `FORESHADOWS.md`, `RECENT_EVENTS.md`, `CHARACTER_ARCS.md`, `ARC_STATUS.md`
- Stable canon
  - `WORLD.md`, `CHARACTERS.md`, `RULES.md`, `FACTIONS.md`, `LOCATIONS.md`

Static facts and dynamic evolution must not be mixed.

## Coordination Rule

All cross-role work uses structured artifacts or change sets.
Only the orchestrator decides final writeback.
