# Event Identity & Causal Event Runtime — 6.5

Every causally meaningful combat event receives a stable EVENT_ID. Multiple shots may observe one event, but observation cannot create another physical event.

## Event record
- event_id
- parent_event_id
- causal_chain_id
- event_type
- source
- actor_ids
- target_ids
- pre_state_ref
- state_delta
- post_state_ref
- observed_by_shots
- confidence
- semantic_hash

## Causal chain
Typical chain:
`ATTACK_COMMIT → CONTACT → FORCE_TRANSFER → IMPACT → RESPONSE → ENVIRONMENT_RESULT`

## Rules
- Event IDs persist through shot recompilation and model adaptation.
- Equivalent event observations retain the same EVENT_ID.
- A changed physical result requires a new event or an explicit state correction at the owning causal layer.
- Semantic hash is computed from canonical event semantics, not wording, camera prose or decorative adjectives.
