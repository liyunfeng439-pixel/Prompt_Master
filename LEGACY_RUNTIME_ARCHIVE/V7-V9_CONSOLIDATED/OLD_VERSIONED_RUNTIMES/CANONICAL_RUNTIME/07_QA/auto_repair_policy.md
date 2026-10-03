# Auto Repair Policy — 6.4

Repair the lowest causal failing layer first, then invalidate and rebuild only affected downstream dependencies.

## Repair routing
Conflict/Confidence → asset/confidence layer
Reference Integrity → source/contract layer
Tactical → tactical graph / decision layer
Temporal → temporal state machine
Action → action graph
Spatial → topology/state
Feasibility → action/timing/position
Physics → force/contact/consequence
Damage → evolution state
Camera → cinematic layer
Shot continuity → continuity layer
Density → compiler prioritization
Model compatibility → adapter

## Repair contract
1. Identify failing field, owning layer and source event.
2. Determine dependency closure.
3. Repair only the lowest causal layer capable of resolving the failure.
4. Invalidate dependent derived fields; preserve unaffected locked fields.
5. Recompute downstream state.
6. Recompile and rerun QA + reference-integrity checks.
7. Run regression assertions relevant to the changed dependency closure.

Camera-only repair cannot PASS an action, spatial, feasibility or physics failure. Auto-repair may not change immutable canon or increase confidence without evidence/user clarification.

Regression is a gate, not a repair layer: a regression failure routes back to the owning source layer, then recompiles.
