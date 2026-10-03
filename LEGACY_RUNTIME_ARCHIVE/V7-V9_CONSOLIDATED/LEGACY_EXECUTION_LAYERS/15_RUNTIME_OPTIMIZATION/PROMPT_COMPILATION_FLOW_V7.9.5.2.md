# Runtime Flow Optimization

Old:
Combat -> Prompt -> Optional VFX

New:
Asset -> Combat Graph -> Move VFX Binding -> Physics/VFX Event -> Cinematic Controller -> Model Adapter -> Final Prompt

No new combat logic added. Existing modules are activated through the runtime path.
