# QA Ownership Graph — 6.5

Each failure must route to the lowest causal module capable of correcting it.

| Failure domain | Owner | Forbidden repair |
|---|---|---|
| asset conflict | conflict_resolution | prompt wording |
| action invalidity | action_candidate_filter / action_graph | camera masking |
| tactical mismatch | tactical_action_selection | cosmetic adjectives |
| temporal order | temporal_state_machine | camera-only rewrite |
| spatial impossibility | spatial_topology | prompt-only rewrite |
| physics/impact | physics / power_relationship | camera-only rewrite |
| damage persistence | damage_environment_evolution | shot deletion |
| resource/injury | resource_fatigue_injury | invented recovery |
| event duplication | event_identity_runtime | changing shot labels only |
| shot coverage | shot_coverage | deleting critical event |
| shot overload | shot_complexity_budget | deleting causal state |
| duration overflow | duration_budget | silently changing requested duration |
| semantic trace failure | combat_semantic_ir | adding unsupported prose |
| model incompatibility | model_capability_adapter | mutating canon |
| ending mismatch | ending_state_runtime | rewriting user ending constraint |

Repairs must rebuild all declared downstream dependencies and re-run regression.
