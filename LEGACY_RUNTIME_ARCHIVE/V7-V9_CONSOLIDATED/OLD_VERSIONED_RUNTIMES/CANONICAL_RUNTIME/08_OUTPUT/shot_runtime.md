# Shot Runtime — 6.4

Hierarchy:
`BATTLE → SEQUENCE → SHOT → BEAT → ACTION`

Physical authority flows upward from the combat runtime; shots are observations/presentations of physical events.

`ACTION → BEAT → PHYSICAL_EVENT → SHOT_OBSERVATION`

Each shot must reference existing `observed_beat_ids`. If it represents an impact, its physical event must already exist in the combat state. Multiple shots may observe one beat. A cut cannot duplicate, reset, accelerate or reverse the physical event unless the underlying temporal state explicitly does so.

A Shot handoff carries screen side, camera axis, subject screen position, movement vector and lens behavior. Handoff state must resolve against the preceding shot or explicit sequence boundary.
