# Weapon Execution Integrity Gate V1.0

## Preconditions
- Immutable Canon / Weapon Bible provides a locked weapon identity, or the action itself has an already verified weapon identity.
- A V4 action candidate is otherwise structurally complete.

## Verification
Check all of the following before `ACTION_EXECUTION_CONTRACT` creation:

```text
action.weapon
== execution_model.weapon_control.weapon
== execution_model.weapon_control.weapon_identity
== weapon_binding.canonical_weapon
== weapon_binding.execution_weapon
== prompt_semantics.weapon_identity
```

Also verify:
- `weapon_actions.weapon` matches the action weapon.
- `martial_unified.weapon` matches the core action weapon.
- `action_graph.weapon_identity` matches the action weapon.
- transition contract carries `requires.weapon_identity` and `result.weapon_identity`.

## Failure behavior
- If top-level weapon is locked: repair execution fields from the profile, then revalidate.
- If top-level weapon conflicts with locked Canon: reject candidate; do not rewrite Canon.
- If the weapon cannot be identified: mark UNKNOWN and retrieve an alternative.

## Output
`WEAPON_INTEGRITY_RESULT = PASS | REPAIRED_PASS | REJECT`
