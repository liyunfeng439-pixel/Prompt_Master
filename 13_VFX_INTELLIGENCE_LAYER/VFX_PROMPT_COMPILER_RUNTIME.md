# VFX Prompt Compiler Runtime

Pipeline:

VFX Graph
 ->
Semantic VFX Events
 ->
AI Video Prompt Language

Goal:
reduce token load while preserving:
- causality
- material response
- motion logic
- visual identity

## V4 Action Knowledge Binding

When a selected action contains V4 `vfx`, the VFX compiler must bind `primary`, `timing`, `direction`, and `suppression` to the already-resolved physical event. V4 VFX cannot create a physical event by itself.

Order:
`ACTION_EXECUTION_CONTRACT → physical result → V4 VFX binding → material/environment response → prompt language`.

If V4 VFX conflicts with the actual weapon/material/environment facts, the runtime uses the factual state and drops the conflicting VFX rather than rewriting the state.
