# Final Combat Sequence Runtime — 6.5.1

Final Combat Sequence Runtime governs the last combat exchange before an Ending State is committed. It is not a replacement for Ending State Runtime: it creates the causal path that produces the terminal snapshot.

## Activation
Enable when the sequence has a defined combat climax or when the user asks for a decisive, high-impact or explicitly unresolved ending. If the user explicitly requests a non-combat ending beat, preserve that constraint.

## Required phases
`FINAL_BUILD → FINAL_OPENING → FINAL_EXCHANGE → FINAL_COMMIT → FINAL_IMPACT → RESULT_LOCK → ENDING_SHOT`

- `FINAL_BUILD`: establish the last tactical opening, resource state and spatial opportunity.
- `FINAL_OPENING`: the final opportunity or counter window becomes observable; do not invent an opening that the prior state does not support.
- `FINAL_EXCHANGE`: one or more causally linked attacks/counters form the final exchange. Avoid unrelated filler actions.
- `FINAL_COMMIT`: the decisive action, mutual clash, escape, disarm, knockdown or interruption is committed.
- `FINAL_IMPACT`: the physical/ability/environment consequence is observed. If force is sufficient, destruction or fracture is immediate rather than delayed.
- `RESULT_LOCK`: derive the final actor, weapon, ability, resource, spatial and environment states.
- `ENDING_SHOT`: one or more shots observe the locked result without creating a new physical event.

## Final exchange rules
1. The final exchange must be causally connected to the preceding tactical state.
2. A decisive finish requires a `final_combat_event` and an observable result; it may not end on a generic pose or unexplained cut.
3. An OPEN/DRAW/INTERRUPTED ending still requires a final observable combat event unless the user explicitly requests an off-screen or non-combat termination.
4. Do not add a new power, weapon property, rescue, environmental collapse or opponent weakness solely to manufacture a climax.
5. Preserve EVENT_ID and semantic hash through all shot observations and model adaptation.
6. The final impact must update MASTER_COMBAT_STATE before Ending State is derived.
7. Ending Shot observes `RESULT_LOCK`; it cannot mutate the locked result.

## Final impact chain
`ATTACK_OR_CLASH → CONTACT → FORCE_TRANSFER → HIT_OR_CLASH_RESULT → BODY/WEAPON RESPONSE → ENVIRONMENT_RESPONSE → FINAL_STATE_DELTA`

The chain may use ability/energy transfer when canon supports it. Every required node must be observable or explicitly marked as designed off-screen; an off-screen event still needs state provenance.

## Finish types
- `VICTORY_FINISH`
- `DEFEAT_FINISH`
- `DRAW_FINISH`
- `INTERRUPTED_FINISH`
- `OPEN_FINISH`
- `CLIFFHANGER_FINISH`
- `RETREAT_FINISH`
- `DISARM_FINISH`
- `KNOCKDOWN_FINISH`
- `ENVIRONMENTAL_FINISH`
- `ABILITY_CLASH_FINISH`

Finish type is a derived execution mode, not authority over user ending constraints.

## Final exchange budget
Use a dedicated terminal budget inside Duration Budget. The default target is the final 10–20% of runtime for final exchange + final impact + ending observation, adjusted for very short sequences. Decorative exposition is compressed before required final causal events are removed.

For a 30-second combat-led sequence, a typical target is approximately:
- 20–25s: escalation/main exchange
- 25–29s: final exchange + final impact
- 29–30s: result/ending observation

These are targets, not immutable timing facts; user duration and explicit pacing constraints take precedence.

## Ending Shot rules
- Must observe an existing `RESULT_LOCK`.
- May use reaction, debris, weapon state, distance or environment as visual punctuation.
- Must not introduce a new attack, hit, destruction event or state change after `RESULT_LOCK` unless the user explicitly defines an additional beat.
- For OPEN/CLIFFHANGER endings, preserve unresolved conflict and continuation hook.
