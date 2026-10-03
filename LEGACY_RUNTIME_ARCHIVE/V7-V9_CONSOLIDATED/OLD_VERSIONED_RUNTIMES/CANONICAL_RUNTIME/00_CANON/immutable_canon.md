# Immutable Canon

Immutable Canon is the non-negotiable fact layer. It contains identity-critical asset facts, explicit user constraints, fixed scene facts, fixed ending requirements, and explicitly locked shot requirements.

## Field classes
- `FACT`: directly confirmed by user/asset/source.
- `INFERRED`: derived but revisable.
- `UNKNOWN`: not observable or specified.
- `CONFLICT`: mutually inconsistent evidence.

## Immutability rules
1. Auto-repair may never silently change `FACT` or explicit user constraints.
2. If a repair requires changing a canon field, escalate to clarification.
3. Derived runtime state may change; canon does not.
4. Prompt compilation must preserve all canon fields marked `MUST`.

## Canon precedence
`USER_HARD_CONSTRAINT > CONFIRMED_ASSET_FACT > EXPLICIT_LOCK > DERIVED_RUNTIME > DATABASE_PRIOR`

## Canon-to-runtime split
`IMMUTABLE_CANON → MASTER_COMBAT_STATE → DERIVED_STATE → PROMPT`
