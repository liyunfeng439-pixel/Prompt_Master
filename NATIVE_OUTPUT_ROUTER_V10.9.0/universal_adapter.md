# Universal Cinematic Adapter V10.9.0

This is the Skill-native Universal output contract. It is not a vendor-official template.

Required visible order:
1. Generation Goal
2. Global Visual Direction
3. Asset Lock
4. Scene / Spatial Continuity
5. Time / Shot Sequence
6. Action Causality
7. Physics / Impact / Environment Response
8. Camera Motivation
9. Continuity / Damage
10. Ending State
11. Negative Constraints

The adapter may compact wording, but must preserve SHOT_IR event order, actor/weapon identity, physical result, damage, and ending semantics.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
