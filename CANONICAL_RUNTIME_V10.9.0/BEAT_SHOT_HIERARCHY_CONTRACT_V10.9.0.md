# Beat / Shot Hierarchy Contract V10.9.0

## Core rule
`EVENT → BEAT → SHOT` is mandatory.

- **Event**: one atomic combat occurrence/result.
- **Beat / 分镜段**: one complete causal combat unit that may contain multiple Events.
- **Shot / 镜头**: one continuous camera coverage unit inside a Beat.

## 30-second rule
- Core Beats: **1–7**, hard maximum 7.
- Each Beat: **1–3 Shots**, chosen by cinematic readability, never by quota.
- Therefore a 30s sequence may have 7 Beats and more than 7 actual Shots.
- Beat count is the storyboard budget; Shot count is the camera coverage budget.

## Split rule
A Beat may split into 2–3 Shots when camera position, action scale, reaction readability, impact emphasis, or spatial reveal materially benefits.
Shot splitting must NOT create a new attack, hit, destruction, tactical decision, or result.

## Merge rule
If one camera can clearly cover the whole causal unit without harming readability, keep the Beat at one Shot.

## Ending
The final Beat may contain 2–3 Shots: build-up, final exchange/impact, and result observation. After `RESULT_LOCK`, no new combat Event may be created.

## Invariants
- Every Event belongs to exactly one Beat and one Shot.
- Every Shot belongs to exactly one Beat.
- `1 <= shots_per_beat <= 3`.
- Beat budget is checked independently from Shot count.


## Cinematic Close-Up Layer
- Close-up is a presentation mode of an existing Event, not a new Event.
- Allowed roles: `impact_contact_closeup`, `weapon_contact_closeup`, `decision_reaction_closeup`, `energy_manifestation_closeup`, `final_impact_closeup`.
- A close-up Shot must contain at least one existing `event_id`.
- At most one close-up Shot per Beat.
- For a 30s sequence, target 2–4 close-up Shots when enough high-value Events exist; fewer is valid.
- Close-ups must be triggered by contact, reaction/decision, ability manifestation, or final impact value. They must not be inserted merely to increase visual variety.
- After a close-up, camera continuity must return to the Beat's spatial/result relationship.
- `RESULT_LOCK` never creates a new close-up combat event; a final close-up may only emphasize the already-locked final impact before result observation.

## V10.9.0 Spatial Snapshot Rule
Every Shot must derive spatial before/after state from the first/last Event assigned to that Shot. The runtime final spatial state must never be reused as a snapshot for earlier Shots.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
