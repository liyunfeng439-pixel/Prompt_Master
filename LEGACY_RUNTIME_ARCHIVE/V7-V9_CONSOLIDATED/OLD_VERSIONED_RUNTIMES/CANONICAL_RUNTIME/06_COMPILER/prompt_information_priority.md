# Prompt Information Priority

Assign every compiled statement one of:
- MUST: character identity, action, spatial relation, state change, physics consequence, hard user constraint.
- SHOULD: camera intent, rhythm, lighting interaction, VFX that supports action, audio cues.
- OPTIONAL: decorative adjectives or secondary atmosphere.

Priority order:
CHARACTER LOCK > ACTION > SPACE > STATE > PHYSICS > CAMERA > VFX/AUDIO > DECORATION.

When prompt length is constrained, remove OPTIONAL first, then SHOULD. Never compress away MUST facts.
Avoid contradictory adjectives and repeated synonyms. Prefer concrete observable outcomes.

## V6.9 Execution-aware compression
For combat prompts, preserve the minimum visible execution chain in this order:
`INTENT → ATTACK_LINE → CONTACT/AVOIDANCE → FORCE_TRANSFER → RESULT`.
Remove internal scoring labels, diagnostic qualifiers, duplicate beat metadata and implementation jargon before final prompt emission.
If one Beat contains more than the execution budget, compile its causally split sub-beats as short continuous clauses rather than one overloaded sentence.
