# Shot Budget Controller V10.1.7

The controller now has an executable harness surface.

## Default 30-second profile
- target: 7
- soft_minimum: 6
- hard_maximum: 7
- S01: 0–4s impact-first opening
- S02: 4–8s first causal exchange
- S03: 8–13s counter / tactical change
- S04: 13–18s escalation / environment response
- S05: 18–23s high-intensity exchange
- S06: 23–27s final build / decisive setup
- S07: 27–30s final impact + result lock + ending observation

## Executable checks
The V10.1.7 harness verifies: shot_count <= 7, event preservation, no event duplication, final result-lock in final shot, duration coverage, and adapter source = SHOT_IR.

## PASS
PASS only when all required events, transitions and ending dependencies survive within the shot budget.
