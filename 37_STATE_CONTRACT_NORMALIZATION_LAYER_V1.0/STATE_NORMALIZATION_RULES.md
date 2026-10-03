# State Contract Normalization Layer V1.0

## Problem fixed
V10.9.0 carried multiple state languages (`preconditions.distance` prose, `execution_model.distance.id`, `transition_contract.requires.distance`). V10.9.0 separates descriptive prose from canonical state IDs.

## Authority
`MASTER_COMBAT_STATE → execution_model.ids → transition_contract normalized fields → descriptive prose`.

`preconditions.distance` remains a human-readable explanation. Runtime matching uses `distance_id`.

## Hard invariants
- `execution_model.distance.id == transition_contract.requires.distance_id`
- `execution_model.stance.id == transition_contract.requires.stance_id`
- `action.weapon == transition_contract.requires.weapon_identity == transition_contract.result.weapon_identity`
- `opponent_response.outcome_class == transition_contract.result.outcome == transition_contract.result.outcome_class`
- descriptive prose never overwrites canonical IDs.
