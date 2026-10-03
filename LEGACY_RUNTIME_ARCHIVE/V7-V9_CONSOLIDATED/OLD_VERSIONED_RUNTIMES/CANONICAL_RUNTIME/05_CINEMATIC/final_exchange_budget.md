# Final Exchange Budget — 6.5.1

Final Exchange Budget reserves a terminal time window for the final combat sequence instead of allowing ordinary exchanges to consume the entire runtime.

## Required fields
- `final_sequence_enabled`
- `final_sequence_ratio`
- `final_exchange_ratio`
- `final_impact_ratio`
- `ending_observation_ratio`
- `final_event_deadline`
- `result_lock_time`

## Defaults
For combat-first sequences, target the final 10–20% of runtime for final exchange, final impact and result observation. Short clips may compress this window, but the causal order must remain intact.

## Allocation priority
1. final combat event
2. final impact/result
3. ending observation
4. micro-recovery
5. decorative punctuation

If over budget, remove decorative setup and redundant recovery before removing a required final causal event.
