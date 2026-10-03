# Output Modes

Support four output modes without changing the underlying runtime:

1. DESIGN: battle blueprint + beat graph + continuity state.
2. STORYBOARD: shot-by-shot production prompt with camera and timing.
3. FINAL_PROMPT: one directly deployable video-model prompt.
4. PACKAGE: multi-shot prompts plus continuity ledger, negative constraints and model adapter.

If the user does not specify a mode, choose FINAL_PROMPT for simple requests and PACKAGE for long/multi-shot requests.


5. DUAL_RIVAL_DIRECTOR: 输出导演分析层、Heat Curve、Beat Balance、Combat QA，再输出最终 Prompt。
