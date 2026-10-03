# Fact / Inference Guard V1.0

The guard prevents asset-inferred details from becoming false Canon facts during prompt compilation.

### Required propagation
`source → provenance → Canon/MASTER_COMBAT_STATE eligibility → execution contract → SHOT_IR → adapter`.

### Hard rules
- `INFERRED` may influence style/compatibility selection but cannot silently become Canon.
- `UNKNOWN` cannot be filled with invented ability, weapon property, scene fact or action fact.
- `CONFLICT` blocks execution until resolved.
- User hard constraints are authoritative Canon.
