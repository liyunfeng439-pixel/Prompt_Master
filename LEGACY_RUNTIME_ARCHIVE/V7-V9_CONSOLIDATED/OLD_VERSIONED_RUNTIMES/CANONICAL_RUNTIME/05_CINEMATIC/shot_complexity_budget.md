# Shot Complexity Budget — 6.4 / V7.9.5.3 Budget-Aware Patch

Budget per shot:
actor_count, action_count, camera_complexity, physics_complexity, VFX_complexity, environment_complexity, continuity_complexity.

## Budget-aware split rule
If combined complexity exceeds the target model's stable capacity or the shot's duration, first attempt compression inside the existing shot. Use the following order:
1. reduce decorative camera complexity;
2. merge adjacent causally linked beats;
3. reduce redundant reactions/recovery/establishing coverage;
4. simplify non-essential VFX density;
5. simplify action density without changing physical outcome;
6. split into an additional shot **only when the active Shot Budget Controller has an unused slot**.

For the default 30-second combat profile, `hard_max_shot_count = 7`. Once seven shots are allocated, no additional shot may be created by this module.

Do not solve overload by deleting required causal events. If seven shots are insufficient after compression, emit `SHOT_BUDGET_PRESSURE` for repair/QA rather than silently exceeding the hard cap.
