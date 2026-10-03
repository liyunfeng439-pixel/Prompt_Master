# Shot Budget Controller V10.1.6

## Contract
This controller controls **final shot allocation**, not causal Beat decomposition.

### Default 30-second profile
- target: 7 shots
- soft minimum: 6 shots
- hard maximum: 7 shots
- S01: 0–4s impact-first opening
- S02: 4–8s first causal exchange
- S03: 8–13s counter / tactical change
- S04: 13–18s escalation / environment response
- S05: 18–23s high-intensity exchange
- S06: 23–27s final build / decisive exchange setup
- S07: 27–30s final impact + result lock + ending observation

Timestamps are defaults only; user-specified timing overrides them.

## Hard rules
1. A 30s default run MUST NOT output more than 7 final shots.
2. Beat Auto-Split may create sub-beats but MUST NOT create final shots by itself.
3. Combat Director and Action Transition Validation happen before Beat→Shot compilation.
4. Prefer merging adjacent causally linked and transition-valid beats into one continuous shot.
5. Never remove a required physical event or required transition state to satisfy the budget.
6. Never invent an event to fill a shot.
7. Ending observation should normally live inside S07.
8. If overload remains, return `SHOT_BUDGET_PRESSURE` and repair within the existing budget.

## Required SHOT_IR fields
`shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, physics, vfx, continuity, damage_state, ending_state`

## PASS
PASS only when shot_count <= hard_max, all required events and transition dependencies survive, no event is duplicated, and duration/continuity remain valid.
