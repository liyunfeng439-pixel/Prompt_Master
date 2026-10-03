# SHOT_IR Contract V10.2.2

SHOT_IR remains the sole presentation semantic source. V10.2.2 adds semantic-diversity metadata for compiler audit only; it cannot alter immutable facts.

Required fields: `shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, physics, vfx, continuity, damage_state, ending_state`.

Compiler-only trace may record: `semantic_bundle_id, selected_component_keys, novelty_score, suppression_reason, story_role`. These are not user-facing prompt tokens.
