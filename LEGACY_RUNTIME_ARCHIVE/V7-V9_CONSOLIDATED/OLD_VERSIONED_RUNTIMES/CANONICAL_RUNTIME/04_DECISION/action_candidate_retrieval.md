# Action Candidate Retrieval Runtime — 6.4

Convert current combat context into a retrieval query over DATA knowledge assets.

## Query fields
actor_style, actor_state, target_state, weapon, distance, stance, opening, tactical_goal, environment, phase, resource_state, ability_state, requested_intensity.

## Retrieval sources
actions_10000, unified_combat_graph_5000, martial_motion_graph_2000, weapon_actions_1000, combo_tree_1000, boss_skills_500, reaction_profiles_256, ability_graph_1024, combat_dna_512 and relevant presets.

Retrieval produces candidates, never final truth. Candidate records must retain source asset IDs and source provenance.
