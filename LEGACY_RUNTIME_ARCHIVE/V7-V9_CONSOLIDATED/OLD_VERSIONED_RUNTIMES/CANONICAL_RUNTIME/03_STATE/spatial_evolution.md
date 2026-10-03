# Spatial Evolution Runtime — 6.4

Spatial topology is persistent and mutable through physical events.

`CONTACT / FORCE / DAMAGE -> STRUCTURAL_CHANGE -> NEW_TOPOLOGY`.

Examples: wall breach creates a new passage; floor collapse creates a height transition; debris creates a new obstacle. Subsequent movement and camera planning must use the evolved topology.
