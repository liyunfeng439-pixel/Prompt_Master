# Shot Continuity Graph — 6.3.1

Maintain cinematic continuity separately from physical continuity while deriving both from `MASTER_COMBAT_STATE`.

## Physical continuity
Position, facing, distance, height, velocity, support foot, weapon state, damage and environment state.

## Cinematic continuity
Screen side, camera axis, camera position, lens behavior, subject screen position, movement vector and shot handoff.

Spatial topology is authoritative for the physical world. Shot Continuity Graph is authoritative only for cinematic presentation. Neither may silently rewrite `MASTER_COMBAT_STATE`.

Cross-axis changes must be explicit camera events; they cannot be introduced as accidental side flips.
