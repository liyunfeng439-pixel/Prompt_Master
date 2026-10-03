# Combat-First Pacing Runtime — 6.5

## Purpose

For requests whose primary intent is combat, the runtime must prioritize visible combat over character introduction, atmospheric establishment and exposition. The default goal is to let characters be introduced **through action**, not through prolonged static presentation.

## Activation

Activate when `combat_intent.primary_goal = COMBAT`, or when the user explicitly requests fighting-first, action-first, fast entry, short character introduction, immediate clash, or similar intent.

Do not activate as a hard constraint when the user explicitly requests a slow character reveal, dramatic entrance, exposition-first opening, or non-combat opening.

## Priority Contract

Default priority for combat-first sequences:

`COMBAT_EVENT > TACTICAL_READABILITY > CHARACTER_IDENTIFICATION > ENVIRONMENT_ESTABLISHMENT > EXPOSITION > DECORATIVE_ESTABLISHMENT`

This changes presentation priority, not canon, character facts, tactical causality or physical feasibility.

## Opening Budget

The runtime allocates an explicit `intro_time_budget` and `first_combat_event_deadline` before shot generation.

Default targets when the user does not specify otherwise:
- `intro_time_ratio_max`: 0.10
- `combat_time_ratio_min`: 0.70
- `first_combat_event_ratio_max`: 0.10
- `static_character_shot_ratio_max`: 0.05
- `recovery_ratio_max`: 0.15

These are targets, not excuses to delete required causal events. For very short clips, absolute time limits are derived from the requested duration and rounded to the model's practical shot granularity.

## First Combat Event

A first combat event is a meaningful physical or tactical event such as:
- weapon clash
- dodge against an incoming attack
- block/parry/contact
- strike/contact
- grab/throw/takedown
- projectile release with immediate combat consequence
- ability activation directed at an opponent
- environmental attack/counter interaction

A pose, stare, walk-in, weapon reveal, hair movement or decorative camera move is not a first combat event unless it is itself a tactically meaningful action.

## Character Introduction Compression

When character identity is already sufficiently known from assets, combine introduction with action. Prefer:

`IDENTIFICATION → ACTION → CONSEQUENCE`

over:

`IDENTIFICATION → STATIC DISPLAY → WALK-IN → POSE → DRAW WEAPON → COMBAT`.

Character shots are permitted only when they add information that cannot be efficiently communicated through the opening action.

## Static Introduction Suppression

Suppress or compress:
- idle character portraits
- prolonged face close-ups
- empty walk-ins
- repeated weapon display
- repeated costume display
- decorative turns
- redundant establishing shots
- pose-only shots
- slow-motion entrances without tactical purpose

If one of these shots is required by canon or explicit user instruction, preserve it but debit it from the intro budget and compensate elsewhere without deleting hard combat events.

## Opening Templates

Select one template when useful:
- `IMPACT_OPEN`
- `COUNTER_OPEN`
- `WEAPON_CLASH_OPEN`
- `AMBUSH_OPEN`
- `CHASE_OPEN`
- `ABILITY_OPEN`
- `ENVIRONMENT_BREAK_OPEN`
- `MID_COMBAT_OPEN`

Template selection is subordinate to asset facts, tactical causality and feasibility.

## Combat Density

Track:
- `intro_time_ratio`
- `combat_time_ratio`
- `action_time_ratio`
- `impact_time_ratio`
- `recovery_time_ratio`
- `static_intro_shot_ratio`
- `first_combat_event_ratio`

The runtime should maximize useful combat density rather than merely maximize the number of cuts or actions.

## Repair Policy

When combat-first constraints fail, repair in this order:
1. remove decorative opening shots;
2. merge character introduction into an action shot;
3. shorten non-combat camera holds;
4. compress recovery/setup language;
5. replace a low-value opening action with a tactically valid action-first candidate;
6. only then reconsider phase allocation.

Never repair by:
- inventing an attack without a tactical cause;
- changing immutable canon;
- hiding an impossible transition with camera movement;
- deleting a required physical event;
- mutating the explicit ending constraint.

## Interaction With Duration Runtime

Combat-First Pacing sets opening and combat-density constraints; Duration Budget allocates actual time. If constraints conflict, preserve hard causal events and report infeasibility rather than silently violating the user's combat-first intent.

## Interaction With Shot Runtime

The first sequence should normally contain a meaningful combat observation. A character-identification shot may share the same physical beat as the first combat event. Multiple shots observing that event do not create duplicate events.

## QA

A combat-first sequence fails when, without explicit user permission:
- the first meaningful combat event occurs after the deadline;
- intro exceeds the configured maximum ratio;
- static character presentation consumes excessive budget;
- combat density falls below the configured minimum;
- opening shots repeat information already available in locked assets;
- an opening presentation block delays a valid combat event without tactical or narrative reason.
