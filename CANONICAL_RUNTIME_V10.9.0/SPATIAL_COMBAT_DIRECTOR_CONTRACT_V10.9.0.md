# Spatial Combat Director Contract V10.9.0

## Purpose
Treat combat space as a persistent tactical state rather than an incidental action label. The Director may move combat horizontally or vertically only when the selected action and current scene support the transition.

## State
Spatial state is persistent across Events and snapshotted per Event/Shot.
- `spatial_layer`: ground | low_air | mid_air | high_air | extreme
- `relative_height`: same_level | slightly_above | airborne | high_air | extreme_scale
- `horizontal_reposition`: none | lateral | forward | retreat | chase | environment_anchor_shift
- `vertical_space_supported`: boolean
- `horizontal_reposition_supported`: boolean
- `anchor`: grounded, sourced scene anchor; UNKNOWN remains UNKNOWN
- `previous_layer` and `last_transition`
- `relative_distance`, `facing`, `attack_axis`, `movement_vector`

## Decision rule
1. Observe current layer and tactical problem.
2. Retrieve actions whose execution semantics explicitly support the needed transition.
3. Score spatial change alongside weapon, distance, opponent prediction and phase goal.
4. Reject unsupported transitions.
5. Commit the new spatial state only after the action result is committed.
6. Pass before/after spatial state into Beat/Shot planning and SHOT_IR.

## Default mode
`adaptive`: prefer meaningful spatial variation when supported. A 30s autonomous fight targets at least one spatial transition when vertical space is supported and enough actions exist. This is a target, not permission to invent movement.
`grounded`: no vertical transitions.
`vertical`: actively considers supported vertical transitions.
`constrained`: preserves user-specified action sequence; no silent rewriting.

## Forbidden
Teleportation, unexplained altitude jumps, weightless suspension, invisible support changes, loss of relative height across a cut, or spatial changes created solely by camera movement.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
