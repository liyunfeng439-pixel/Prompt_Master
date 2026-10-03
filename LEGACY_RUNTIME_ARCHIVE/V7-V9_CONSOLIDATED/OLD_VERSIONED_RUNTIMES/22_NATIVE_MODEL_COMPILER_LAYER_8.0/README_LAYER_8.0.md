# Native Model Compiler Layer 8.0

Purpose:
Replace generic output formatting with model-specific compilation.

Pipeline:
Combat Master -> Universal Combat Master -> Native Compiler -> Model Output

Rules:
1. Never copy Universal Prompt directly.
2. Recompile according to target model schema.
3. Run validator before final output.
4. Support CN/EN output.
