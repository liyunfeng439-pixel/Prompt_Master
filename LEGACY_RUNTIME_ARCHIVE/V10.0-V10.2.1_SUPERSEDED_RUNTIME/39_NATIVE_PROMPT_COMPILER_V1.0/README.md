# Native Prompt Compiler V10.1.8

Compiles one SHOT_IR into actual model-facing prompt text for Universal, Seedance 2.5 and MiniMax H3. The generated prompt is presentation-only: no director reasoning, no schema exposition, no internal IDs.

Input: `runtime_trace.json` + `shot_ir.json`
Output: `native_prompts_v1018.json`

The invariant manifest and semantic fingerprint remain structured QA metadata and are not required to appear in the final prompt.
