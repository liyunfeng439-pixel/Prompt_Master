# Master Combat State — 6.4

`MASTER_COMBAT_STATE` is the sole runtime source of truth. Existing modules remain specialized views/writers; none may maintain an independent authoritative state.

## State domains

- `immutable_canon`: immutable user/asset facts and hard constraints
- `assets`: normalized character, weapon and world assets
- `uncertainty`: FACT / INFERRED / UNKNOWN / CONFLICT lineage
- `actors`: actor state, target/attention/engagement relations
- `world`: spatial topology, obstacles and environment state
- `intent`: narrative/tactical/emotional/visual/power/pacing/ending goals
- `temporal`: beat timing and state-machine phase
- `action`: action graph and current executable action
- `ability`: activation, trajectory, contact, persistence and interruption state
- `physics`: force, contact, motion and material response
- `damage`: actor and environment evolution
- `impact`: intensity/rhythm/escalation state
- `camera`: camera event state
- `shot`: shot/sequence observation state
- `continuity`: physical and cinematic continuity ledgers
- `resource`: stamina, energy, charge, cooldown, fatigue and injury when relevant
- `qa`: gates, failures, repairs and validation history
- `action_history`: recent action families, repetition patterns and variety constraints

## Mutation contract

Every mutation must include `source_event`, `changed_fields`, `unchanged_locked_fields`, and `confidence`. A downstream module may derive a view, but may not silently invent a state change.

## Authority order

`IMMUTABLE_CANON > CONFIRMED_ASSET_FACT > MASTER_COMBAT_STATE > DERIVED_RUNTIME_STATE > COMPILED_PROMPT_TEXT`

Prompt text can never become a new source of truth.

## Dependency rule

When a state field changes, only downstream dependent fields are invalidated and rebuilt. Unaffected state remains locked. A repaired state must carry its source event and confidence lineage forward.
