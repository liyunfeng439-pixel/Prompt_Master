# Shot Budget Controller V7.9.5.3

## Purpose
Control final cinematic shot count before Shot Runtime so short combat clips remain readable and do not fragment into excessive cuts. This module controls presentation budget only; it never deletes, changes, or invents physical events.

## 30-second production profile
When `requested_duration_seconds = 30` and the user has not explicitly requested another shot count:
- `target_shot_count = 7`
- `soft_min_shot_count = 6`
- `hard_max_shot_count = 7`
- `opening_shot_budget = 1`
- `main_combat_shot_budget = 5`
- `terminal_shot_budget = 1`
- `terminal_window = 27–30s`

The controller therefore prefers exactly 7 shots when the causal material supports it, accepts 6 when events can be grouped without harming readability, and never emits more than 7 shots for the default 30-second profile.

## Recommended 30-second allocation
`S01 0–4s` — impact-first opening / first combat event
`S02 4–8s` — first attack → response → result
`S03 8–13s` — counter / tactical change
`S04 13–18s` — ability or spatial escalation / environment response
`S05 18–23s` — second high-intensity exchange
`S06 23–27s` — final build / final exchange setup
`S07 27–30s` — final impact + result lock + ending observation

These are default allocation targets, not immutable timestamps. User-specified timing always has priority.

## Allocation rules
1. Build the causal Beat Graph first; do not create filler beats merely to reach seven shots.
2. Allocate one shot to each major cinematic phase before considering additional coverage.
3. Prefer one shot containing a continuous causal chain over multiple micro-shots.
4. A shot may observe multiple causally linked beats when temporal, spatial and action readability remain valid.
5. Repeated reaction, travel, recovery, debris and camera punctuation should be folded into the nearest causal shot when they do not constitute independent events.
6. Ending observation is normally folded into S07 for a 30-second clip unless a separate ending shot is explicitly required and can be accommodated within the seven-shot budget.

## Budget-aware overload policy
When `shot_complexity` or model capability exceeds a single-shot budget:
1. First simplify camera complexity.
2. Then compress decorative VFX, redundant reaction coverage and non-essential recovery.
3. Then merge adjacent causally linked beats into one continuous shot.
4. Then simplify action density while preserving the physical event chain.
5. Only split a shot if an unused shot slot exists.
6. If no slot remains, do **not** create an eighth shot; mark the case `SHOT_BUDGET_PRESSURE` and repair within the existing seven-shot allocation.

## Hard constraints
- Never exceed `hard_max_shot_count` for the active profile.
- Never solve shot overload by deleting a required causal event.
- Never solve shot overload by inventing a new physical event.
- Never use additional cuts to conceal continuity, physics or asset errors.
- EVENT_ID, semantic hash, causal order, state transition, damage state and Ending State must survive compression/merging.

## Interaction with Beat Auto-Split
`Beat Auto-Split` remains valid for action readability and causal decomposition, but it no longer implies additional final shots. Sub-beats may remain inside one shot as continuous executable clauses when the shot budget is exhausted.

## QA
PASS only when:
- final shot count <= hard_max_shot_count;
- all critical physical events are observed or explicitly off-screen;
- no required causal event was removed;
- no duplicated physical event was created;
- all shot handoffs remain spatially and temporally valid;
- requested duration is preserved within duration tolerance.
