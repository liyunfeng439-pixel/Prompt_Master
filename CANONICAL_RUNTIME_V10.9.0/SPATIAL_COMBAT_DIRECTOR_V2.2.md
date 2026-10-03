# Spatial Combat Director V2.2

## Authority
Spatial state is a first-class combat state. It is not a decorative camera tag.

## State model
Each actor has an independent spatial state:
- `layer`: ground / low_air / mid_air / high_air / extreme
- `anchor`: known scene anchor or `UNKNOWN`
- `support`: grounded / airborne / falling / recovering
- `movement_vector`: explicit or `UNKNOWN`

The runtime also maintains pairwise state:
- relative height: above / below / same_level
- relative distance
- facing / attack axis when known
- environment anchor relationship

## Semantic rules
- `目标离地` changes the target actor, not the attacker.
- `空中` changes the actor performing the aerial action.
- `高空` is only allowed when explicitly supported by action/scene facts.
- Missing spatial facts remain `UNKNOWN`; never invent a bridge, roof, cloud sea, valley, or altitude.
- A spatial transition must be caused by action, force, support loss, pursuit, fall, or explicit scene movement.
- Spatial change must solve or intensify a tactical problem; no decorative flying.

## Environment anchors
Known anchors may be supplied by scene Canon, e.g. bridge, roof, cliff edge, pillar, cloud platform. The Director may move between known anchors, but may not invent an anchor.

## Modes
- `adaptive`: seek meaningful spatial change when supported.
- `vertical`: actively consider explicit vertical actions.
- `grounded`: no vertical transition.
- `constrained`: preserve user action sequence.

## Camera contract
A transition shot must reveal start state, movement path, and new spatial relation. Close-ups may emphasize the event only after spatial readability has been established.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.
