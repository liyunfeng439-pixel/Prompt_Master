# Action Transition Graph Runtime V2.0

## Purpose
Validate not only `A → B`, but whether the selected next action remains physically and tactically viable for `B → C`.

## Validation dimensions
- distance/range
- facing/attack line
- support foot/stance
- center of mass
- weapon position/grip
- momentum/recovery
- actor position/elevation
- target position/zone
- terrain dependency
- counter/recovery window
- next-action compatibility
- phase-goal compatibility

## Transition classes
`DIRECT_CONTINUE | RECOVERY_LINK | REDIRECT | POSITIONAL_LINK | COUNTER_LINK | TERRAIN_LINK | ABILITY_LINK | INVALID`

## Lookahead
For each committed candidate B, run:
`A→B validation → B→C candidate scan → B→C validation`.
If A→B passes but all viable B→C paths fail and the current phase still requires continuation, B is rejected or downgraded before commitment.

## Invalid-transition recovery
`INVALID` is a feedback signal, not a terminal state:
1. restore the last valid state;
2. re-rank alternate candidates;
3. try a legal recovery/position/redirect link when required;
4. validate again;
5. commit only after PASS.

Default bounded retry: 3 alternate candidates + 1 recovery-link attempt.

Hard prohibitions remain: teleport/unexplained reposition, weapon replacement/duplication, impossible orientation/support/center-of-mass, missing required recovery, actor/weapon lock contradiction, nonexistent environment state.

## Selection priority
`tactical continuity > physical continuity > spatial continuity > phase-goal fit > combat personality fit > camera followability > causal escalation > visual impressiveness`


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
