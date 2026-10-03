# Internal Consistency Tests — 6.3.1

1. Canonical runtime contract validates all existing state domains.
2. No second canonical runtime contract exists outside `09_CONTRACTS`.
3. INFERRED/UNKNOWN/CONFLICT cannot be promoted silently.
4. Tactical event and temporal beat reference the same physical event.
5. Multiple shots may reference one beat without duplicating the event.
6. Repair invalidates/rebuilds dependent fields only.
7. Semantic compression preserves protected causal chains.
8. Model adapter cannot mutate canon or physical state.
9. Camera repair cannot resolve physical failure.
10. Existing user hard constraints survive recompile and repair.
