# Seedance 2.5 Final Prompt Template

## Output Philosophy
Only output visible continuous video events. Do not output director reasoning, runtime names, validation logs or internal modules.

## Template

[Global Visual]
- style:
- resolution/fps:
- camera language:
- lighting/material:
- atmosphere:

[Character Lock]
A:
- appearance:
- weapon:
- combat identity:
- movement signature:

B:
- appearance:
- weapon:
- combat identity:
- movement signature:

[Scene Continuity]
- location:
- spatial anchors:
- destruction state:
- persistent damage:

[Action Sequence]
00:00-00:XX
- initial visible action:
- movement cause:
- contact event:
- reaction:
- environment response:
- camera movement:

[Physics]
- weight:
- inertia:
- cloth/hair response:
- impact feedback:

[VFX]
- ability source:
- color/material behavior:
- trail/residual effect:
- collision effect:

[Ending State]
- final positions:
- damage state:
- remaining effects:

## Compression Rules
- Keep cause → action → impact → result chain.
- Prefer short continuous actions over abstract descriptions.
- Remove internal labels such as VFX Layer, Physics Runtime, QA PASS.
