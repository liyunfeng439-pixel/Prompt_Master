# V4 Runtime Validation Rules V1.1

## V4-001 Source Integrity
Selected action must resolve to a real V4 action_id/core_id/variant.

## V4-002 Canon Compatibility
V4 cannot invent or override locked character, weapon, scene or ability facts.

## V4-002-A Weapon Execution Integrity
`action.weapon`, `execution_model.weapon_control.weapon`, `weapon_binding.canonical_weapon`, `prompt_semantics.weapon_identity` and transition-contract weapon identity must be identical. Mismatch triggers Weapon Integrity Repair, then revalidation.

## V4-003 Pre-State Compatibility
Distance, stance, support, facing, weapon state and terrain must be compatible. Environment surfaces are soft constraints unless the action explicitly requires physical contact with that surface.

## V4-004 Execution Completeness
Required phases: setup/load/acceleration/contact/reaction/recovery.

## V4-005 Causal Result
Hit/block/dodge/miss/bind must produce a physically and tactically observable result.

## V4-006 Counter Validity
Counter window requires its stated exposure and defender condition.

## V4-007 Recovery Validity
Miss/block/dodge/over-rotation cannot silently disappear; recovery must be resolved when required.

## V4-008 Transition Contract
Each production action must provide `transition_contract`. The next action must satisfy `requires` and inherit `result` state.

## V4-009 Presentation Causality
Camera, VFX and environment cannot precede the event that causes them.

## V4-010 State Persistence
The resolved post-state becomes the next MASTER_COMBAT_STATE delta.

## V4-011 Traceability
Every Beat action must retain `knowledge_action_id`, `execution_contract_id`, `event_id`.

## V4-012 SHOT_IR Trace
Every SHOT_IR action_chain entry must reference the resolved execution contract.

## V4-013 Ability Contract
Persistent or escalation abilities, including `法相`, must enter Beat Graph only through an `ABILITY_EXECUTION_CONTRACT`.

## V4-014 Result Lock / No-Chase
After final ability clash, loser exit and victor chase behavior are explicit state decisions. A user-specified no-chase ending must emit `NO_CHASE` after RESULT_LOCK.
