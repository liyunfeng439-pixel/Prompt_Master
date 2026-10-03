# Combat Prompt Master V10.18.6 — Weapon Signature Ultimate Switch + Weapon Semantic Variant Compiler

Production runtime upgrade from V10.18.6; incremental semantic-coherence repair with no top-level architecture change.

Key fixes:
- Dual-actor spatial state instead of one global layer
- Target-aware `目标离地` semantics
- Actor-aware `空中` semantics
- Explicit high-air gating
- Pairwise relative height/distance state
- Environment-anchor continuity with UNKNOWN protection
- Spatial tactical decision layer
- Corrected spatial QA gates
- Active package cleaned of .bak and __pycache__

Core hierarchy remains EVENT → BEAT → SHOT, 30s ≤7 Beats, 1–3 Shots/Beat, cinematic close-up layer, immutable SHOT_IR, native adapters, and RESULT_LOCK.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.


V10.18.2 integrates Adaptive Combat Narrative into the executable runtime: semantic Shot Director, true B→C lookahead replan, budget remerge, Action Knowledge camera/VFX activation, and stronger runtime QA.


### V10.18 Adaptive Combat Narrative
Every action_result carries a bounded reason/intent/state transition and the runtime derives an adaptive narrative curve from actual events. Narrative cannot invent outcomes or create events.


## V10.18.4
Weapon Semantic Variant Compiler is the current incremental repair: after final action commit, remote weapon execution now replaces the active prompt semantic core with a variant-consistent core sentence. Native hand-held wording is retained only as provenance.

Canonical execution order is synchronized with the actual Harness: transition validation/replanning/lookahead precede Universal Weapon Control and Execution Variant commit. The top-level Universal / Seedance 2.5 / MiniMax H3 output structures are unchanged.

## V10.18.4 Single-Source Semantic Closure
V10.18.4 closes the remaining semantic-source gap without changing the top-level runtime architecture. The final Execution Variant writes its authoritative `prompt_semantics.core_sentence` into SHOT_IR; the Native Compiler consumes that payload directly. Action Components may add outcome/recovery detail, but they cannot reconstruct or overwrite the remote-execution core. Deep QA now verifies the end-to-end chain:

`Execution Variant → prompt_semantics.core_sentence → SHOT_IR → semantic_trace → final model prompt`

The Universal / Seedance 2.5 / MiniMax H3 top-level output structures remain unchanged.


## V10.18.6 Weapon Signature Ultimate Switch

新增显式功能开关：仅当用户输入包含完整短语“专属大招”时触发。当前内置徒手、剑、刀、枪、棍、戟、双刃、链刃、弓、法器、扇、鞭专属招式。专属大招叠加在已有终结/高价值 Combat Event 上，不创建新 Event；核心语义经 `prompt_semantics → SHOT_IR → Native Compiler` 单源传播，三模型顶层输出结构不变。

未出现“专属大招”时，专属大招层保持关闭且不改变既有动作、镜头、VFX、Beat/Shot 或最终 Prompt。
