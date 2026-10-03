# Combat State Transition Contract — 6.4

`BEFORE_STATE + EVENT + CONSTRAINTS → AFTER_STATE`

Every transition declares `transition_id`, `beat_id` when applicable, `changed_fields`, `unchanged_locked_fields`, `cause`, `confidence`, and `source_event`.

## Dependency rule
A changed field invalidates its registered downstream dependencies before recompilation. Examples:
- position/facing/distance → spatial, feasibility, camera continuity, shot handoff;
- weapon state → action availability, decision, feasibility, continuity;
- damage/environment state → later spatial state, destruction visibility, continuity;
- ability state → targeting, action availability, physics/effect continuity.

Downstream modules may not invent changed fields absent from the transition. A repair must preserve unaffected locked fields.
