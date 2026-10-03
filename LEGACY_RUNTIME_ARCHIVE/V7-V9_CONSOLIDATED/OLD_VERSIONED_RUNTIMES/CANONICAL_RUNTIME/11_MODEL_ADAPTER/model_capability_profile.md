# Model Capability Profile — 6.4

The canonical runtime produces model-neutral semantics first, then compiles against a target capability profile.

Profile fields:
- prompt_density_limit
- action_complexity_limit
- multi_actor_capacity
- camera_complexity
- physics_expression
- reference_image_capacity
- long_video_capacity
- continuity_strength
- preferred_prompt_structure
- unsupported_features

Unknown capability values remain UNKNOWN.

## Adapter boundary

The adapter may alter expression, compression, ordering of presentation text and model-specific syntax. It may not alter:
- immutable canon
- actor identity
- action count/order
- tactical cause
- temporal event order
- spatial relationships
- contact/outcome
- physical state
- damage/environment result
- explicit user ending constraints

Adapter output is a compiled view, never a new source of truth.


## Design-feedback boundary
Model capability is evaluated before shot/action finalization. Capability limits may trigger shot splitting, action simplification, density reduction or alternate presentation, but may not change canon, tactical intent, event order or physical outcome.

## Complexity fields
- shot_complexity_budget
- action_complexity_budget
- actor_count_limit
- temporal_consistency
- destruction_reliability
- reference_motion_fidelity
