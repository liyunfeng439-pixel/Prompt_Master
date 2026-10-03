# Tactical Action Selection Runtime — 6.4

Select among valid candidates using a qualitative priority vector:

`TACTICAL_FIT + STATE_FIT + SPATIAL_FIT + WEAPON_FIT + STYLE_FIT + CONTINUITY_FIT + RHYTHM_FIT + CINEMATIC_VALUE - FEASIBILITY_RISK - REPETITION_PENALTY - COMPLEXITY_PENALTY`.

This is a decision policy, not a requirement to expose numeric scores in output.

Selection must record the chosen reason and the rejected hard constraints. If no candidate survives, invoke fallback policy rather than inventing an action.
