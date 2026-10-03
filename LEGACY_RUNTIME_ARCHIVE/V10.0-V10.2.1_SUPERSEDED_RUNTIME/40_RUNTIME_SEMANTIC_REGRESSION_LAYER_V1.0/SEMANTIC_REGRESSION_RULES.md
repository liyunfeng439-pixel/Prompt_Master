# Runtime Semantic Regression V1.0

Checks the full chain after compilation:

1. one SHOT_IR source for all adapters
2. actor and weapon invariants preserved
3. event order and event coverage preserved
4. ending/result/no-chase preserved
5. INFERRED provenance does not become FACT/CANON
6. 30s default uses at most 7 Final Shots
7. Beat IDs are non-empty and unique
8. native prompt compiler produced actual prompt text, not a manifest-only placeholder
9. adapter semantic fingerprints are derived from the same locked invariant manifest
10. no RESULT_LOCK event is followed by a new attack event
