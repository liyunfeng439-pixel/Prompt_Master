# QA Matrix — 6.4

Validate each beat, sequence and final compiled output.

| Gate | PASS condition |
|---|---|
| Canon / Asset Lock | identity-critical fields and explicit constraints remain stable |
| Confidence Integrity | no illegal confidence promotion or silent conflict overwrite |
| Reference Integrity | every required ID/reference resolves; no illegal orphan derived state |
| Conflict | no unresolved high-impact conflict is silently ignored |
| Tactical | major action has grounded reason and observable trigger |
| Temporal | timing, contact window, predecessor/successor and concurrency are coherent |
| Action | action is executable and state-compatible |
| Spatial | positions, facing, distance and obstacles are coherent |
| Feasibility | body/weapon/space/reach/recovery checks pass |
| Physics | impact has causal force, contact and consequence |
| Damage | damage/environment state persists correctly |
| Camera | camera maps to events and does not conceal failures |
| Shot Continuity | screen direction, axis and handoff remain coherent |
| Event Uniqueness | observation does not create duplicate physical events |
| Impact | requested intensity is observable and paced |
| Density | MUST information and causal nodes survive compilation |
| Model Adapter | adapter changes expression only, not state/canon/causality |
| Hard Constraints | every explicit user constraint is preserved |

Any FAIL triggers targeted repair, dependency invalidation/rebuild, recompilation and re-validation.
