# Weapon Execution Integrity Layer V1.0

## Purpose
Prevent weapon identity drift between action identity, execution mechanics, weapon-action knowledge and model-facing prompt semantics.

## Hard invariant
`action.weapon == execution_model.weapon_control.weapon == weapon_binding.canonical_weapon == weapon_binding.execution_weapon == prompt_semantics.weapon_identity`

## Runtime position
`Immutable Canon → Weapon Integrity Gate → V4 Action Resolution → ACTION_EXECUTION_CONTRACT`

The gate runs before tactical action commitment. A mismatch is repaired from the weapon execution profile when the top-level action weapon is already canonical; Canon itself is never changed.

## Repair policy
1. Treat `action.weapon` / locked Weapon Bible as factual authority.
2. Rebind execution-level weapon control from `WEAPON_EXECUTION_PROFILES_V1.json`.
3. Refresh prompt weapon references and retrieval tags.
4. Rebuild the action transition contract if it is missing.
5. Re-run V4 resolution and transition validation.
6. Reject the candidate if the repaired record is still inconsistent.

## Scope
This layer fixes and validates `actions_10000`, `weapon_actions_1000`, martial production nodes, action graph nodes and combo causal-chain weapon identity.
