# SHOT_IR Contract V10.1.4

`SHOT_IR` is the only presentation-layer semantic source consumed by the Native Output Router.

## Required fields
- `shot_id`
- `duration`
- `story_function`
- `beat_ids`
- `event_ids`
- `actor_state`
- `spatial_state`
- `action_chain`
- `camera`
- `physics`
- `vfx`
- `continuity`
- `damage_state`
- `ending_state`

## Semantic invariants
The following must survive every adapter unchanged:
`event_ids, causal_order, actor_identity, weapon_identity, spatial_state, physical_result, damage_state, ending_state`.

## Field semantics
- `beat_ids`: internal Beat membership only; never becomes additional final shots.
- `event_ids`: stable causal events. One physical event = one ID.
- `actor_state`: identity, pose, motion, position, facing, support, weapon relation and relevant combat state.
- `spatial_state`: relative positions, distance, height, obstacles, axis and environment state.
- `action_chain`: ordered action/result/reaction sequence within the shot, including any required transition links.
- `camera`: cause-following camera intent, not decorative motion.
- `physics`: contact, force transfer, reaction, displacement, recovery and immediate structural response.
- `vfx`: visual representation of resolved energy/material/impact results.
- `continuity`: inherited identity, spatial, weapon, state and temporal locks.
- `damage_state`: persistent actor and environment damage.
- `ending_state`: final-state transition and RESULT_LOCK behavior when applicable.

## Source authority
`MASTER_COMBAT_STATE` and Canon are upstream facts. SHOT_IR is the single presentation-layer semantic contract. Final prompt text cannot rewrite either.
