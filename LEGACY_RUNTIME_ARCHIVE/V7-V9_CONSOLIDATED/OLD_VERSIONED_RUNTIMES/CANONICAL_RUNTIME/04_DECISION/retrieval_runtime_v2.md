# Knowledge Retrieval Runtime 2.0 — 6.5

Knowledge assets remain candidate evidence. Retrieval 2.0 adds provenance, applicability, conflict state and deterministic source priority.

## Retrieval stages
`QUERY NORMALIZATION → SOURCE PRIORITY → CANDIDATE RETRIEVAL → APPLICABILITY CHECK → PROVENANCE CHECK → CONFLICT RESOLUTION → CANDIDATE SET`

## Source priority
1. task-specific confirmed assets and locked style constraints
2. relevant specialized combat knowledge
3. unified action/motion knowledge
4. generic fallback knowledge

No data source may override IMMUTABLE_CANON or MASTER_COMBAT_STATE.

## Provenance fields
source_asset, source_record_id, retrieval_reason, applicability, conflict_status, confidence.

## Failure behavior
If evidence is insufficient, return UNKNOWN or invoke fallback policy. Never synthesize an undocumented action ID or capability as if retrieved.
