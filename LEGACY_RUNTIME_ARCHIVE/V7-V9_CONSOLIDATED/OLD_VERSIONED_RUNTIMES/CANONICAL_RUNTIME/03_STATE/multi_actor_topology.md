# Multi-Actor Combat Topology

Supports 1v2, 2v2, boss/minions and free-for-all structures.

Track per actor:
`role, relation, attention_target, engagement_state, position, facing, distance_to_targets, support_state, damage_state, weapon_state, current_goal`

Global rules:
- Every major action identifies its target.
- Target selection must be compatible with spatial access and tactical context.
- Ally/enemy relations cannot silently change.
- Off-screen actors retain state unless explicitly removed from the scene.
- Simultaneous actions require independent timing windows or an explicit shared event.
