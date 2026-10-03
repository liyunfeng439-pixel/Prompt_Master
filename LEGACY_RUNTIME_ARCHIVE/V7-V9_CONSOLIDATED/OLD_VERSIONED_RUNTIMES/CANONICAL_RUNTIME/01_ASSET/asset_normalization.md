# Asset Normalization Runtime — 6.4

Normalize heterogeneous inputs into stable Character, Weapon, World/Scene and Style records.

## Normalized domains
- identity / appearance
- anatomy / proportions
- clothing / equipment
- weapon geometry / grip / reach when observable
- environment geometry / surfaces / obstacles
- style and rendering constraints
- reference provenance

## Rule
Normalization may standardize representation, never invent missing facts. Each field retains `source_ref`, `confidence`, and `status`.

## Output
Normalized assets become candidates for lock; only confirmed facts enter IMMUTABLE_CANON.
