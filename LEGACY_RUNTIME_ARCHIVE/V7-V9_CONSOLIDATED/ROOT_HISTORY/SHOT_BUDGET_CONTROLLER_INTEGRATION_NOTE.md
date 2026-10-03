# Shot Budget Controller Integration

Integrated from V7.9.5.3 Shot Budget Controller architecture.

Scope:
- Only storyboard/shot budgeting control upgraded.
- Existing combat, VFX, compiler, model output and runtime modules preserved.
- No replacement of existing generation logic.

New behavior:
- Controls maximum storyboard shots.
- Uses budget-aware shot planning.
- Preserves beat continuity and causal ordering during shot merging.
