# Ending State Runtime — 6.5

The Ending State is the authoritative terminal/continuation snapshot of a battle sequence. It is derived from MASTER_COMBAT_STATE and immutable user ending constraints; it never invents an outcome.

## Required domains
- battle_result: WIN / LOSS / DRAW / INTERRUPTED / OPEN
- actor_survival: ALIVE / DEAD / UNKNOWN per actor
- actor_condition: current injury, impairment, stance and mobility
- weapon_condition: held / dropped / damaged / destroyed / unavailable
- ability_condition: active / spent / interrupted / cooldown / unavailable
- resource_condition: stamina, energy, charge, fatigue
- spatial_condition: positions, exits, destroyed routes, changed topology
- environment_condition: persistent damage/collapse/debris state
- unresolved_conflict: explicit unresolved tactical/narrative threads
- continuation_hook: next valid state or open continuation requirement

## Rules
1. Ending constraints from IMMUTABLE_CANON cannot be changed by repair, model adaptation or cinematic quality logic.
2. OPEN endings may omit a winner, but may not erase observable damage, resource, weapon, spatial or survival state.
3. Every terminal field must trace to a state/event source or be explicitly UNKNOWN.
4. A later sequence must inherit the ending snapshot instead of rebuilding it from prose.
5. Final Prompt is only a representation of Ending State.
