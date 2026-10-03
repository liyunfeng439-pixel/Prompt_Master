# Seedance 2.5 Native Adapter V10.1.4

Runtime Contract: V10.1.4. Established visible output template is unchanged.

Purpose: transform the same SHOT_IR into a concise model-facing cinematic prompt while preserving all causal invariants.

## Compilation order
Reference / Asset Lock
→ Creative Brief
→ Global Visual Direction
→ Timeline / Shot Sequence
→ Motion Continuity
→ Physics and VFX
→ Camera Motivation
→ Ending State
→ Negative Constraints

## Timeline rule
Each final shot is one continuous executable unit. Sub-beats may be written as a single temporal chain inside that shot. Do not create additional shot numbers from sub-beats.

## Motion rule
Use explicit subject + action + direction + contact/avoidance + physical result + next state. Avoid abstract verbs without visible consequences.

## Camera rule
Camera movement must follow the causal event: weapon trajectory, impact, body displacement or environment consequence. No decorative spin/shake/zoom without cause.

## Continuity rule
Preserve identity, weapon count/type, spatial relation, damage state and ending state exactly from SHOT_IR.

## Output rule
Return only the model-facing prompt unless the user explicitly requests internal diagnostics.

Note: this adapter defines a Skill-native compilation contract; it does not claim to reproduce undocumented vendor-internal formatting.
