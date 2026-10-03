# V4 Action Runtime Pipeline

## 0. Retrieve
Retrieve V4 candidates using tactical intent, current state, character/weapon facts, domain, distance, action family and personality.

## 0.5 Weapon Integrity Gate
Run `34_WEAPON_EXECUTION_INTEGRITY_LAYER_V1.0` against Canon, action.weapon, execution_model.weapon_control, weapon_binding, prompt semantics and transition contract. Repair from a verified weapon profile when the action weapon is already canonical; otherwise reject.

## 1. Resolve
Build `ACTION_KNOWLEDGE_CANDIDATE` from the selected V4 action. Resolve all required fields.

## 2. Bind pre-state
Compare V4 distance/stance/weapon/state requirements against MASTER_COMBAT_STATE. Any hard mismatch rejects the candidate.

## 3. Execute
Convert V4 execution_model into a chronological action event:
`setup → load → acceleration → contact → result → recovery`.

## 4. Resolve result
Use V4 opponent_response to create an observable target state. Never replace result with a decorative VFX event.

## 5. Resolve counter
Use V4 counter_logic to determine whether a counter window exists. The counter is a conditional state, not an automatic next action.

## 6. Resolve recovery
Use V4 failure_and_recovery after hit/block/dodge/miss/bind as applicable. Recovery becomes the attacker's next state.

## 7. Validate transition
Use V4 transition + transition_contract against the next candidate and current state.

## 8. Bind presentation
Camera follows V4 cinematic phases; VFX follows V4 causal timing/direction; environment follows actual collision/footfall.

## 9. Emit Beat
Only after steps 0–8 pass may the action enter Beat Graph.

## 9.5 Ability Contract
If the beat contains a persistent/escalation ability such as `法相`, resolve `35_ABILITY_EXECUTION_CONTRACT_V1.0` before Beat Graph insertion.

## 10. Emit SHOT_IR
SHOT_IR receives the resolved action/result/reaction/recovery chain, not raw V4 data.

### No-pass behavior
If a candidate cannot resolve all mandatory execution fields, do not partially execute it. Retrieve a compatible candidate.
