# V9.9.5 Combat Prompt Execution Kernel Clean Runtime

Goals:
- single execution entry
- preserve reference image to final prompt chain
- remove runtime ambiguity
- optimize Qwen3.8 context usage

Main flow:
Reference -> Character -> Scene -> Combat -> Camera -> VFX -> Prompt -> Validation -> Repair
