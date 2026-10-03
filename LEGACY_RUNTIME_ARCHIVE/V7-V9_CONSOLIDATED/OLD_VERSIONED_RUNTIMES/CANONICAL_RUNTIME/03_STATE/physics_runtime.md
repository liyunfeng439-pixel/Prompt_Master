# Physics Runtime — 6.4

Physics Runtime resolves physical consequences after a validated contact or movement event.

## Required inputs
actor/target state, mass/stability, velocity, contact geometry, force direction/magnitude class, weapon/ability properties, material resistance, support surface and current damage state.

## Resolution chain
`MOTION → CONTACT → FORCE TRANSFER → MATERIAL/ACTOR RESPONSE → STATE DELTA → ENVIRONMENT DELTA`.

## Rules
- No impact without a valid contact event.
- No knockback without a force-transfer explanation.
- No structural destruction without compatible force, material and support conditions unless immutable canon explicitly defines exceptional behavior.
- Immediate destruction is allowed when the resolved impact crosses the structure's failure threshold; artificial reaction delay is not inserted.
- Physics output becomes state evidence for downstream damage, topology, camera and audio.
