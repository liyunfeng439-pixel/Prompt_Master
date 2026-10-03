# Combat Prompt Master 6.4 — Runtime Upgrade

## Base
Built directly on `V6.3.2_PRODUCTION_CLEAN2`; all original production files are retained unless explicitly superseded by the 6.4 pipeline/schema entry.

## Added
- Asset ingestion/normalization/lock runtime
- Combat style inference runtime
- Battle Blueprint runtime
- Reference motion extraction + transfer contract
- Action Graph runtime
- Knowledge retrieval / candidate filtering / tactical selection / reaction selection / fallback
- Action history and repetition control
- Power relationship + impact outcome taxonomy
- Resource/fatigue/injury state
- Body/equipment hit zones
- Spatial evolution
- Shot coverage graph
- Shot complexity budget
- Duration budget
- Audio event runtime
- Combat Semantic IR → Shot IR → Prompt IR
- Cinematic Quality QA
- Ambiguity policy
- Six new runtime schemas
- 14 new regression gates (19–32)

## Changed
- Runtime pipeline upgraded from 6.3.2 to 6.4.
- Master Combat State now explicitly supports resource and action-history domains.
- Actor schema is tightened to require state domains needed for executable selection.
- Model Adapter now feeds back into design through complexity budgets without mutating semantics.
- DATA is formally candidate knowledge only and cannot become a source of truth.

## Compatibility
Existing 6.3.2 modules remain valid unless superseded by the 6.4 pipeline. The package is intentionally backward-readable at the documentation level, but the canonical release contract is 6.4.
