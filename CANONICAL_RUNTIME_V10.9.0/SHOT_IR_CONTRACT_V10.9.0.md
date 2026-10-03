# SHOT_IR Contract V10.9.0

SHOT_IR remains the sole presentation semantic source. V10.9.0 adds semantic-diversity metadata for compiler audit only; it cannot alter immutable facts.

Required fields: `shot_id, beat_id, beat_index, shot_index, shot_count_in_beat, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, camera_role, closeup, closeup_role, physics, vfx, continuity, damage_state, ending_state`.

Hierarchy invariant: `EVENT → BEAT → SHOT`; `beat_ids` identifies the single parent Beat of the Shot. A Beat may contain 1–3 Shots.

Compiler-only trace may record: `semantic_bundle_id, selected_component_keys, novelty_score, suppression_reason, story_role`. These are not user-facing prompt tokens.

Close-up fields are presentation-only: `closeup` is boolean and `closeup_role` must be null or one of the canonical close-up roles. They cannot alter immutable event semantics.


## Spatial semantics
`spatial_state` must preserve the causal space state presented by the runtime. Required semantic subfields are `combat_layer_before`, `combat_layer_after`, `spatial_mode`, `transition_trace`, `actor_states`, `relative_height`, and `anchors`. Each actor state preserves `layer`, `anchor`, and `support` when known. Spatial transitions are presentation of committed event results and cannot invent new movement.
Allowed layers: `ground`, `low_air`, `mid_air`, `high_air`, `extreme`. A transition must be physically motivated and continuous.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
