# Adaptive Weapon Control Intelligence V1.0

Universal Weapon Control is a capability available to every canonical weapon. This layer decides **when** to activate it without changing the Event/Beat/Shot architecture.

## Decision chain
`combat_situation → tactical_problem → remote_control_value → control_mode → behavior_pattern → existing_action_execution`

## Activation
- Explicit remote/telekinetic/spirit-control intent activates remote control.
- Autonomous mode may activate remote control when tactical value reaches the bounded threshold.
- Close/contact range is biased toward HAND_HELD unless explicit remote intent overrides it.
- RESULT_LOCK disables new remote attacks.

## Patterns
`orbit`, `angle_change`, `multi_angle`, `environment_redirect`, `release/attack/return`

## Invariants
- No new Combat Event is created.
- Weapon identity/count/geometry/material/mass/inertia remain locked.
- A trajectory change requires a control cause.
- Remote control requires a control source.
- Morph/extension remains separately authorized.
- Remote control never becomes teleportation.
