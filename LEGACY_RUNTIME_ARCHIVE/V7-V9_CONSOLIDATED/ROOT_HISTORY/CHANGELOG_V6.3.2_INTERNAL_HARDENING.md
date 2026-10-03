# Combat Prompt Master 6.3.2 — Internal Hardening

This release only strengthens existing V6.3.1 functions. No new combat capability category is introduced and historical modules/databases are preserved.

## Changes
- Resolved Final Prompt vs source-of-truth authority wording conflict.
- Tightened Master Runtime Contract and existing domain contracts.
- Added reference-integrity contract for existing Beat/Shot/Event/Decision/Ability links.
- Strengthened temporal sequencing, concurrency and contact-window invariants.
- Strengthened state-transition dependency invalidation/rebuild rules.
- Strengthened Ability, Decision and Shot contracts with existing runtime semantics.
- Converted existing regression cases into explicit pass/fail assertions.
- Changed regression from repair stage to release gate with source-layer rerouting.
- Preserved all legacy modules, databases and compatibility assets.
