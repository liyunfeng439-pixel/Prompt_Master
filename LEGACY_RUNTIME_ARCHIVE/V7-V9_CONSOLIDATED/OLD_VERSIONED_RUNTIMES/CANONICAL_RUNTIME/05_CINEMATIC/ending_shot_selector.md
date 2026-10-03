# Ending Shot Selector Runtime — 6.5.2

Ending Shot Selector chooses an observation template only after `RESULT_LOCK` exists. It never decides the battle result; it selects how an already-locked result is visually punctuated.

## Selection authority
Priority:
1. IMMUTABLE_CANON ending constraint
2. RESULT_LOCK / Ending State
3. final_combat_event and finish_type
4. final_impact_chain
5. persistent environment state
6. actor/weapon/ability condition
7. cinematic intent and available shot budget

## Selection rules
- Select exactly one primary ending template unless the user explicitly requests a multi-beat ending.
- A template must be compatible with `finish_type` and the observable final event.
- Never select a template merely because it looks dramatic if its required physical result is absent.
- Prefer a template that exposes the strongest already-existing result: impact, displacement, weapon break, environmental destruction, ability clash, or unresolved threat.
- Ending duration is short by default; preserve combat momentum and avoid converting the ending into a character-introduction scene.
- Ending shots are observation-only after RESULT_LOCK.

## Template registry

### T01 — TERMINAL_IMPACT_FREEZE
Use when a decisive hit has a strong readable physical result and the actor remains visually legible.
Sequence: final impact → immediate response → brief camera punctuation → locked result.

### T02 — KNOCKBACK_REVEAL
Use for launch, knockback or knockdown finishes.
Sequence: final force transfer → high-speed displacement → landing/impact consequence → result reveal.

### T03 — THROUGH_DESTRUCTION
Use when the final event destroys or penetrates a structure.
Sequence: final impact → immediate structural break → character/object passes through → debris clears enough to reveal locked state.

### T04 — DUAL_CLASH_BURST
Use for draw, open, ability-clash or mutual-impact endings.
Sequence: simultaneous clash → force separation → environmental shock → both actors remain readable → unresolved/result state.

### T05 — WEAPON_BREAK_REVEAL
Use when weapon damage, disarm or destruction is the decisive result.
Sequence: final contact → weapon failure/disarm → weapon trajectory or break detail → actor state reveal.

### T06 — ABILITY_CLASH_AFTERGLOW
Use when an ability collision is the final event and the residual visual state is already supported.
Sequence: clash → energy dissipation → terrain/effect residue → actor condition reveal.

### T07 — RUINS_STANDOFF
Use when the battle leaves persistent environmental destruction and the actors remain active or standing.
Sequence: destruction settles → both actors framed against damaged terrain → final distance/stance → continuation state.

### T08 — DUST_REVEAL
Use when debris/smoke/dust is an actual consequence of the final event and the actor state is initially occluded.
Sequence: impact → debris/dust expansion → controlled reveal → locked condition.

### T09 — OPEN_CONFRONTATION
Use for OPEN or CLIFFHANGER endings where both sides remain active.
Sequence: final observable exchange → separation → brief tension hold → unresolved tactical state.

### T10 — BATTLEFIELD_PULLBACK
Use when the environment/state change is more important than a close actor reveal.
Sequence: final result → immediate aftermath → camera widens to expose persistent battlefield change → state lock.

### T11 — DISARM_LOCK
Use when the decisive result is loss of weapon/control rather than incapacitation.
Sequence: contact → weapon/control loss → short reaction → actor separation/stance → result.

### T12 — PURSUIT_CONTINUES
Use when the final event does not resolve the conflict and the user explicitly wants the fight to continue beyond the clip.
Sequence: final exchange → separation/reposition → immediate continuation cue → hard cut or transition without inventing a new attack.

## Forbidden mismatches
- No `WEAPON_BREAK_REVEAL` without a grounded weapon damage/disarm/break event.
- No `THROUGH_DESTRUCTION` without persistent structural damage or destruction.
- No `DUST_REVEAL` when no debris/dust consequence exists.
- No `VICTORY` visual punctuation for OPEN/DRAW/INTERRUPTED results.
- No victory pose, stare-down, slow face push-in or decorative hero shot when it adds no information beyond RESULT_LOCK.

## Template priority heuristics
When multiple templates are valid, choose by observable consequence in this order:
1. weapon break/disarm if decisive
2. environmental destruction if decisive
3. displacement/knockdown if decisive
4. ability clash if decisive
5. direct terminal impact if decisive
6. unresolved/open confrontation
7. battlefield pullback
8. dust reveal as a visibility solution, not as a default style

The selector does not rank battle outcomes. It only selects a compatible presentation template after the outcome is already locked.
