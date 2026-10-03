# Weapon Execution Data Repair Rules

## Repair mapping
`weapon` is the source identity. It drives the execution-control profile, not the other way around.

## Do not repair by blind string replacement
Only the weapon-introduction fields are rewritten. Target anatomy, tactical purpose and reaction semantics are preserved unless the record is explicitly inconsistent.

## Required repaired fields
- `execution_model.weapon_control`
- `weapon_binding`
- `prompt_semantics.weapon_identity`
- `prompt_semantics.core_sentence` weapon prefix
- `retrieval_tags` weapon tag
- `transition_contract.requires.weapon_identity`
- `transition_contract.result.weapon_identity`

## Coverage target
0 mismatches across all production action records.
