# V4 Runtime Field Binding Matrix

| V4 field | Runtime consumer | Required behavior | Output destination |
|---|---|---|---|
| execution_model.distance | Candidate Filter / State | reject incompatible range | actor_state / spatial_state |
| execution_model.stance | State / Transition | validate support and posture | actor_state |
| execution_model.joint_chain | Action Runtime / Physics | preserve causal body chain | action_chain / physics |
| execution_model.center_of_mass | Physics / Transition | calculate/describe weight transfer and recovery | physics / continuity |
| execution_model.weapon_control | Weapon Runtime | preserve grip, trajectory and weapon identity | actor_state / action_chain |
| execution_model.contact_geometry | Physics / VFX | determine contact type and force result | physics / vfx |
| opponent_response | Actor Reaction / Director | create observable target result and next tactical state | action_chain / actor_state |
| counter_logic | Director / Transition | expose counter window only when state permits | action_chain / continuity |
| failure_and_recovery | Transition / State | resolve miss/block/dodge recovery | continuity / ending_state |
| transition | Transition Graph | choose legal link class and next conditions | action_chain |
| cinematic | Shot Compiler | follow action phases without hiding causality | camera |
| vfx | VFX Runtime | instantiate only after causal event | vfx |
| environment | Physics/VFX/State | apply persistent material/environment response | physics / vfx / continuity |
| prompt_semantics | Native Compiler | compress resolved facts into model-facing language | action_chain |
| transition_contract | Transition Graph | hard-gate required pre/post states | action_chain / continuity |
| native_execution | Weapon Runtime | bind weapon-specific mechanics | actor_state / physics |


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
