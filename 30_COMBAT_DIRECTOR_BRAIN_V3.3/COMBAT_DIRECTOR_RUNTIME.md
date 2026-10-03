# Combat Director Runtime V3.0 — Battle-Level Strategy

The Director plans the battle at two levels: **dynamic strategic phase** and **local tactical exchange**. It does not impose a fixed six-stage story.

## Core loop
`OBJECTIVE → OBSERVATION → TACTICAL_PROBLEM → DECISION → ACTION → RESULT → OPPONENT_OBSERVATION → OPPONENT_INTERPRETATION → OPPONENT_PREDICTION → COUNTER_DECISION → NEW_ACTION → TACTICAL_SHIFT → PHASE_CHECK → ESCALATION`

## Dynamic phase state
Each phase may persist, split, skip, or terminate. Required state:
`phase_id, phase_goal, dominant_problem, resource_pressure, positional_goal, opponent_prediction, allowed_escalation, phase_exit_condition, shot_budget_pressure`.

A phase transition requires an observable change: tactical discovery, result, position, resource/ability state, terrain state, damage state, or ending condition.

## Opponent prediction
Prediction is a small qualitative candidate set generated from personality, current state, recent results, tendencies, terrain, resources, and prior failed attempts. It is not a probability claim and never overrides Canon, user constraints, weapon lock, physical feasibility, or ending state.

## Candidate selection
Select an action only when it solves the current tactical problem, creates a useful next state, is physically executable, anticipates plausible counters, fits combat personality, and remains viable under the current shot budget.

## Transition-aware replanning
`A→B` must pass validation. If invalid:
`reject → re-rank B candidates → try alternate → optional recovery/position/redirect link → validate → commit`.
Default bound: three alternate candidates plus one recovery-link attempt. If all fail, re-plan the tactical decision rather than emitting an impossible sequence.

## A→B→C lookahead
When a viable C candidate exists, validate `A→B` and then `B→C`. A B candidate that is locally valid but leaves no viable continuation is rejected or down-ranked while the current phase still requires continuation.

## Budget-aware planning
Shot pressure feeds back to phase/action planning. The Director may merge compatible micro-beats, fold low-value recovery into a parent event, or select a more compressible valid action. It may never delete the unique result/state transition that explains a later event.

## Escalation
Escalation is driven by tactical difficulty, range, position, tempo, terrain, resource pressure, multi-angle pressure, ability interaction, damage accumulation, or environmental collapse. Larger VFX alone is not strategic escalation.
