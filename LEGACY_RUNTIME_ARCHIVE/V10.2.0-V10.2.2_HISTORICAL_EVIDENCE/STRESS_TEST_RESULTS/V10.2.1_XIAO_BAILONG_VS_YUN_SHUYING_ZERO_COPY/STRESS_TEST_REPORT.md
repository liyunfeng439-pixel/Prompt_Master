# V10.2.1 Runtime Stress Test — 小白龙 vs 云疏影

## Test input
30s high-intensity combat prompt using the supplied character reference sheets. Locked ending: both activate 法相, Yun Shuying loses and escapes, Xiao Bailong does not pursue.

## Runtime result
- Contract integrity: PASS
- Action contracts: 10
- Ability contracts: 2
- Events: 27
- Final shots: 7
- Recovery events: 6
- RUNTIME_STRESS_TEST: PASS

## Ending gates
- victor = xiao_bailong
- defeated_actor = yun_shuying
- result_lock = true
- escape = true
- no_chase = true

## Semantic compiler
- Universal: 1,794 chars
- Seedance 2.5: 1,752 chars
- MiniMax H3: 2,001 chars
- runtime term leakage: 0 on all models
- semantic bundle collisions: 0
- component reuse ratio: 0.05
- exact duplicate sentences: 0
- deep semantic QA: PASS

## Performance regression
V10.2.0 standard Harness did not complete within the 60-second benchmark window in the same environment. V10.2.1 completed end-to-end in 12.457 seconds.

V10.2.1 uses:
1. streaming-hash preflight instead of a second full JSON parse;
2. one parent load of the large action/graph datasets;
3. selected-action payloads in `runtime_trace.selected_action_payloads`;
4. in-process Native Prompt Compiler;
5. in-process Deep Prompt Semantic QA;
6. explicit performance telemetry.

## Evidence
See the JSON artifacts in this directory for the runtime trace, Beat Graph, SHOT_IR, native prompts, semantic metrics, QA, adapter outputs and performance benchmark.
