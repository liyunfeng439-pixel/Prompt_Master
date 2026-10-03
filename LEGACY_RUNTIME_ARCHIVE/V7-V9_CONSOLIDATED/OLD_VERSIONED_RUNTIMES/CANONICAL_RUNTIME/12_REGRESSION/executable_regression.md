# Executable Regression Fixtures — 6.5

Regression cases are represented as machine-readable fixtures under `CANONICAL_RUNTIME/12_REGRESSION/fixtures/`.

Each fixture contains:
- input assumptions
- immutable constraints
- expected state fields
- expected causal events
- expected ending fields when applicable
- expected failure owner for negative cases

The validator checks schema presence, required fields, event identity uniqueness, local references, fixture IDs and expected owner declarations. Runtime-specific semantic assertions remain documented in `regression_suite.md` and are not claimed as executable unless a fixture explicitly encodes them.
