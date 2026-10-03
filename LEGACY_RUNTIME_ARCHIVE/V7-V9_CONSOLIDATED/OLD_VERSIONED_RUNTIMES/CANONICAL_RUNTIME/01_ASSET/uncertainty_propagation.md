# Uncertainty Propagation — 6.3.1

FACT / INFERRED / UNKNOWN / CONFLICT are runtime states, not descriptive labels.

## Propagation rules

1. `FACT` may directly constrain execution.
2. `INFERRED` may guide selection but cannot silently become FACT.
3. `UNKNOWN` cannot be used as a hidden hard constraint; downstream modules must choose a safe compatible option or surface clarification when necessary.
4. `CONFLICT` blocks silent synthesis of conflicting facts and must remain visible until resolved or explicitly scoped.
5. If an upstream field changes confidence, dependent derived fields are invalidated and recomputed.
6. Auto-repair cannot increase confidence without new evidence or an explicit user decision.

## QA invariants

- No INFERRED→FACT promotion without evidence.
- No UNKNOWN→FACT promotion by completion.
- No CONFLICT→FACT overwrite by precedence guess.
- Every derived field retains source/confidence lineage.
