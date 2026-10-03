# Native Prompt Optimization Runtime Hook Fix V1.0

## Purpose
Integrate 23_NATIVE_PROMPT_OPTIMIZATION_LAYER_V1.0 into the canonical runtime execution chain.

## Changes
- Added native_prompt_optimization stage after semantic_compression and before model_capability_adapter.
- Registered native_prompt_optimization in runtime module registry.
- Preserved Combat_IR, Shot_IR, Prompt_IR, official output contracts.

## Non Changes
- No changes to combat generation logic.
- No changes to Seedance 2.5 template.
- No changes to MiniMax H3 template.
- No changes to shot budget or 7-shot controller.
