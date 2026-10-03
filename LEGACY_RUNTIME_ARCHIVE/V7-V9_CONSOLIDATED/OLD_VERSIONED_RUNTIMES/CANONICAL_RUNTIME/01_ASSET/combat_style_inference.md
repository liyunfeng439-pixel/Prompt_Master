# Combat Style Inference Runtime — 6.4

Infer executable style tendencies without converting inference into canon.

## Style vector
- preferred_range
- tempo_profile
- footwork_profile
- attack_bias
- defense_bias
- counter_bias
- weapon_usage
- risk_tolerance
- movement_amplitude
- preferred_openings

## Evidence
Use locked anatomy, weapon constraints, confirmed lore, reference motion and observed posture. Every inferred field stores evidence refs and confidence.

## Runtime use
Style is a weighting layer for action retrieval and selection. It may raise/lower candidate priority but cannot authorize an otherwise infeasible action.
