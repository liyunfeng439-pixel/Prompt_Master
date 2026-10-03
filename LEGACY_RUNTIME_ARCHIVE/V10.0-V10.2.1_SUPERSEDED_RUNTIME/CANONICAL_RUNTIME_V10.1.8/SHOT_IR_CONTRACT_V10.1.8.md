# SHOT_IR Contract V10.1.9

SHOT_IR is the only presentation-layer semantic source. Native prompts must be compiled from SHOT_IR; adapters must not invent or remove combat facts.

Required fields:
`shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, ability_contract_ids, camera, physics, vfx, continuity, damage_state, ending_state`

Trace extensions:
- knowledge_action_id
- execution_contract_id
- state_contract_hash
- provenance_status
- ability_contract_id

Hard gates:
1. beat_ids are non-empty and unique.
2. one event has one stable EVENT_ID.
3. 30s default uses ≤7 Final Shots.
4. RESULT_LOCK cannot be followed by an attack event.
5. inferred details retain provenance and cannot silently become Canon.
6. all model outputs originate from this same SHOT_IR.
