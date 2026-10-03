# Asset Ingestion Runtime — 6.4

Purpose: convert user-provided images, video, text profiles and references into traceable raw observations before normalization.

## Input classes
- character_reference
- weapon_reference
- environment_reference
- style_reference
- reference_video
- battle_frame
- user_text_constraint

## Required output
Every extracted item carries `asset_id`, `source`, `observation`, `confidence`, `status`, and `locked_candidate`.
Status is FACT only when directly supported by the source; otherwise INFERRED, UNKNOWN, or CONFLICT.

## Prohibited behavior
- Do not infer hidden anatomy, weapon properties, powers, identities, or unseen scene geometry as FACT.
- Do not merge conflicting sources before conflict resolution.
- Do not let a compiled prompt become an asset source.

## Handoff
`raw_observation -> asset_normalization -> conflict_resolution -> immutable_canon/master_combat_state`.
