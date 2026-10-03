# Temporal Combat State Machine — 6.4

Every meaningful combat beat is a timed state transition linked to tactical cause and physical result.

`TACTICAL_REASON → ACTION_INTENT → TEMPORAL_PHASE → CONTACT/OUTCOME → AFTER_STATE → NEXT_DECISION`

Required fields: `state_id`, `start_time`, `duration`, `action_phase`, `contact_window`, `event_id`, `after_state`, `linked_tactical_reason`, `linked_camera_event`, `linked_physics_event`.

## Time invariants
- `start_time >= 0`; `duration > 0`; end time = start + duration.
- Sequential beats must not overlap unless they share an explicit `concurrency_group`.
- A predecessor must end at or before a sequential successor begins.
- Parallel beats may overlap only inside the same declared concurrency group.
- Contact windows must lie inside the beat interval.
- A beat at a sequence boundary may omit predecessor/successor; interior beats may not silently orphan either side.

Phases: `IDLE → PREP → ACCELERATION → COMMIT → CONTACT → IMPACT → RESPONSE → RECOVERY → TRANSITION`.

Rules:
- CONTACT requires spatial compatibility and a valid commit path.
- IMPACT creates an explicit consequence unless miss, glance or deflection is declared.
- RECOVERY starts from the actual post-contact state.
- The next beat inherits the previous `after_state`.
- Camera cuts do not rewrite physical time or state.
- One physical beat may be observed by multiple shots; a shot cut cannot create a second physical event.
