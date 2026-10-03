# MiniMax H3 Native Adapter V10.1.6

Runtime Contract: V10.1.6. Established visible output template is unchanged.

Purpose: transform the same SHOT_IR into a structured, long-context-friendly model-facing prompt while preserving all causal invariants.

## Compilation order
Scene
→ Characters / Asset Lock
→ Combat Objective
→ Action Sequence by time
→ Camera
→ Physics / Environment
→ Visual Effects
→ Consistency Rules
→ Ending State
→ Negative Constraints

## Action rule
Write actions as chronological executable clauses: preparation → initiation → acceleration/change → contact/avoidance → force/result → recovery/next decision.

## Long-context rule
Repeat only identity-critical constraints when needed for continuity; do not restate decorative style text in every shot.

## Continuity rule
Preserve identity, weapon count/type, positions, damage, environment state, event order and ending state exactly from SHOT_IR.

## Output rule
Return only the model-facing prompt unless the user explicitly requests internal diagnostics.

Note: this adapter defines a Skill-native compilation contract; it does not claim to reproduce undocumented vendor-internal formatting.
