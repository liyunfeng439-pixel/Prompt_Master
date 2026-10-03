# Narrative QA Contract

- narrative coverage: 每个 action_result 都有 narrative
- reason integrity: reason 必须来自显式 tactical_problem、前一结果、当前 phase goal、距离/位置等已有状态之一
- transition integrity: current_state 与上一事件 next_state 可连续
- escalation integrity: escalation 只能由事件/状态变化推动
- curve integrity: 叙事曲线总时长等于 duration；30s 不超过7 Beat
- result lock: RESULT_LOCK 后不得有新的 action narrative
- ending neutrality: open/draw 不自动补胜负
