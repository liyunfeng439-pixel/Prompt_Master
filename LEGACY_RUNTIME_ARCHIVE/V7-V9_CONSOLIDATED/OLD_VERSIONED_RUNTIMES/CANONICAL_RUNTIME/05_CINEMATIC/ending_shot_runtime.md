# Ending Shot Runtime — 6.5.1

Ending Shot Runtime is an observation layer after `RESULT_LOCK`.

## Allowed
- reveal final actor condition
- reveal weapon/ability/resource state
- show persistent environment damage
- show distance/separation or unresolved threat
- provide a short visual punctuation beat

## Forbidden
- creating a new physical event
- silently changing the winner/result
- restoring destroyed geometry
- restoring spent resources
- introducing a new attack or hit
- using a camera cut to conceal a continuity failure

All ending shots must reference an existing EVENT_ID or RESULT_LOCK and preserve its semantic hash.
