# Shot Compression Engine V2.0

## Layer separation
Three different operations must not be conflated:
1. **Beat Compression** — merges compatible causal beats.
2. **Shot Planning / Budgeting** — decides Beat boundaries and Shot coverage and timing.
3. **Text Compression** — shortens wording after SHOT_IR; it never changes event existence.

Text compression can never cause a physical event to disappear from the Shot Plan.

## Budget-aware feedback loop
`Beat Graph → provisional Shot Plan → Shot Budget → pressure? → Combat Director / Beat Graph feedback → recompress → Shot Budget → SHOT_IR`

When the provisional plan exceeds the hard cap:
- merge adjacent causal beats when spatial/camera continuity allows;
- fold micro-reactions into their parent event;
- keep contact, result, tactical decision and unique state-changing events;
- choose a more compressible action candidate when transition and tactical validity remain equal;
- never delete the only event explaining a later state.

## 30-second rule
`Beat target=6–7`, `Beat hard_max=7`. Each Beat uses 1–3 Shots based on cinematic complexity; Shot count is not hard-capped at 7. User timing overrides the default allocation but never the hard maximum unless the user explicitly requests a different runtime contract.

Beat Auto-Split is forbidden from creating additional Beats solely to hit a Shot quota; Shot splitting may create 2–3 camera coverages inside one Beat without creating new Events.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
