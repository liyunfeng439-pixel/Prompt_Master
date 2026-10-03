# Duration Budget Runtime — 6.5

Allocate requested duration across phases, beats and shots before final compilation. When `combat_first_pacing.enabled = true`, reserve the opening budget before normal phase allocation.

## Required pacing fields

- `requested_duration_seconds`
- `intro_time_ratio` / `intro_time_budget`
- `combat_time_ratio` / `combat_time_budget`
- `first_combat_event_ratio` / `first_combat_event_deadline`
- `action_time_budget`
- `impact_time_budget`
- `recovery_time_budget`
- `static_intro_shot_ratio`

Beat and shot durations must sum within tolerance to the requested runtime.

For combat-first sequences, default targets are `intro <= 10%`, `combat >= 70%`, and first meaningful combat event within `10%` of total duration unless the user specifies different limits. These are presentation targets; hard causal events remain mandatory.

If the requested duration is too short, compress decorative introduction and non-essential recovery first. Then merge character identification into combat beats. Never delete a required causal event or invent an action to satisfy a timing target. If still infeasible, report the conflict.
