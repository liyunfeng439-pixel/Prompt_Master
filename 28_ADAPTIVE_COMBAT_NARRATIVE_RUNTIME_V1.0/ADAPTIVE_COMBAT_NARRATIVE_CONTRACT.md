# Adaptive Combat Narrative Contract

## Event narrative
每个 action_result 至少携带：current_state、combat_intent、reason_for_action、state_transition、escalation_level、next_expected_state、provenance。

## 叙事阶段
阶段从实际事件特征自适应推导：establish / test / tactical_shift / escalation / climax / resolution；不是固定六段模板。

## 禁止
不得凭空生成胜者、败者、秘密技能、未确认动机、未确认环境、未发生攻击或新的结局。RESULT_LOCK 后不生成新的战斗叙事事件。
