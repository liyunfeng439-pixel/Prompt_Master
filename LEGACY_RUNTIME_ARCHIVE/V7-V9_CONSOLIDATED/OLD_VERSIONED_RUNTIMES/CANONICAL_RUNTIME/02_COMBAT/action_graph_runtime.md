# Action Graph Runtime — 6.4

Represent combat as executable action nodes connected by state-compatible transitions.

Each node defines actor, target, action_type, prerequisites, tactical_reason, timing, contact/outcome expectation, resulting state delta and candidate follow-ups.

## Transition rule
An edge is valid only if the source after-state satisfies the destination prerequisites. Invalid edges are rejected before prompt compilation.

## Event identity
A physical action owns one event identity. Multiple shots may observe it; shots never create duplicate physical actions.
