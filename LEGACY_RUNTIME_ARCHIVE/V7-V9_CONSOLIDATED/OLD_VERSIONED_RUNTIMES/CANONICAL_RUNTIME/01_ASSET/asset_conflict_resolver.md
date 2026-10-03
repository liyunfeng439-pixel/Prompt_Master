# Asset Conflict Resolver

## Purpose
Resolve inconsistent information across multiple character, weapon, scene and style references without silently overwriting facts.

## Evidence classes
- PRIMARY: user-designated or clearest canonical reference.
- SECONDARY: compatible supporting reference.
- CONFLICT: directly inconsistent reference.
- UNKNOWN: not visible or not safely inferable.

## Rules
1. Never merge incompatible visual facts into one invented design.
2. Preserve PRIMARY facts; downgrade conflicting fields to CONFLICT.
3. If no primary exists, prefer the most complete and internally consistent reference, but mark the decision as inferred.
4. Lock identity-critical fields before combat generation: face, hair, silhouette, costume key shapes, weapon identity, dominant colors/materials.
5. For shot-specific variants, create an explicit variant state rather than mutating the base asset.
6. Propagate unresolved conflicts into QA and final negative constraints when they can cause model drift.
