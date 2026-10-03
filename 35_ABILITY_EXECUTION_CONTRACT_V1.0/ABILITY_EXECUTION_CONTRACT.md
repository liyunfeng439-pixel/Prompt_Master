# Ability Execution Contract V1.0

## Contract fields
- `ability_contract_id`
- `ability_family`
- `authorization_source`
- `actor_identity`
- `activation_state`
- `manifestation_state`
- `weapon_sync`
- `ability_motion`
- `contact_or_field_result`
- `opponent_response`
- `resource_state`
- `persistence_state`
- `result_lock`
- `exit_state`
- `trace`

## Manifestation sequence
`readiness → activation cue → energy gathering → form manifestation → weapon/stance synchronization → first ability action → clash/result → depletion or persistence → RESULT_LOCK → exit`.

## 法相 contract
For `法相`, use the actor's verified archetype/style only to select a compatible manifestation profile. Visual details that are not locked facts remain `INFERRED`, not Canon.

The manifestation must move with the actor's actual combat line; the avatar cannot become an independent unrelated attacker.

## Final clash
The final clash must be resolved as:
`commit → collision → force transfer → manifestation damage → actor result → winner/loser state → escape/chase decision`.

When the user specifies that the defeated opponent escapes and the victor does not pursue, the ending decision becomes an explicit `NO_CHASE` state after `RESULT_LOCK`.


## Multi-Actor Final Clash
When two or more persistent abilities participate in one final clash, the runtime uses one shared `joint_clash_event_id` and one shared `result_lock_event_id`. Individual ability contracts reference the shared lock; they must not independently terminate the duel before the shared clash is resolved.
