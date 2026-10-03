# Action Scoring Runtime — 6.5

Convert the V6.4 qualitative selection policy into a structured decision record. Scores are internal decision features and are not required in final user-facing prompts.

## Features
- tactical_fit
- state_fit
- spatial_fit
- weapon_fit
- style_fit
- continuity_fit
- rhythm_fit
- cinematic_value
- feasibility_risk
- repetition_penalty
- complexity_penalty

## Selection order
1. Apply hard filters first.
2. Compute comparable decision features for surviving candidates.
3. Apply tactical and continuity constraints before cinematic preference.
4. Apply variety only when it does not conflict with tactical necessity.
5. Select one candidate or invoke fallback when no candidate is valid.

## Trace
Store candidate_id, feature basis, rejected constraints, selection reason, source provenance and confidence.


## V6.8 High-Impact Combat Extension
After hard filters pass, compute a separate `stylish_action_priority` trace with:
- motion_amplitude
- acceleration_change
- contact_payoff
- displacement_payoff
- weapon_identity
- combo_link_quality
- silhouette_readability
- camera_followability
- environment_payoff
- action_readability
- complexity_change_count
- execution_budget_fit

This layer is a preference, not an authority. It cannot override tactical necessity, feasibility, asset locks, state continuity or event identity. When several valid candidates are equivalent on those constraints, apply Action Readability Gate first; then prefer stronger readable action and consequence. Complexity beyond budget is penalized and may trigger Beat Auto-Split.
