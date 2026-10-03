# SHOT_IR Contract V10.1.7

SHOT_IR remains the only presentation-layer semantic source. V10.1.7 adds normalized-state and provenance trace extensions.

## Required fields
`shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, physics, vfx, continuity, damage_state, ending_state`

## Required internal trace
- `knowledge_action_id`
- `execution_contract_id`
- `event_id`
- `state_contract_hash`
- `provenance_status`
- `ability_contract_id` when applicable

## Invariants
Adapters must preserve actor identity, weapon identity, causal order, event IDs, spatial state, physical result, damage state, ending state and provenance status.

`INFERRED` scene/style details must not be serialized as locked Canon facts.
