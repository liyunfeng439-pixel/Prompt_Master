# SHOT_IR Contract V10.1.9

SHOT_IR remains the sole presentation contract. V10.1.9 adds semantic compilation metadata without changing physical facts.

Required fields per shot:
- shot_id
- duration
- story_function
- beat_ids
- event_ids
- actor_state
- spatial_state + provenance
- action_chain
- ability_contract_ids
- camera
- physics
- vfx
- continuity
- ending_state

Semantic compiler extension:
- `semantic_feature_priority`
- `semantic_dedup_trace`
- `camera_compression_trace`
- `vfx_compression_trace`
- `prompt_quality_hash`

These fields are trace metadata. They cannot modify actor identity, weapon identity, event order, result, state, or ending.
