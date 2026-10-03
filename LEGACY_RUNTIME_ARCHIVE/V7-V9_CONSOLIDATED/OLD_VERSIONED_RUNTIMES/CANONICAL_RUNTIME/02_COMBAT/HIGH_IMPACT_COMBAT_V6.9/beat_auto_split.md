# Beat Auto-Split V6.9

## Trigger
当 Beat：
- readability 未达门槛；或
- complexity budget 超限；或
- 同一 Beat 同时发生多个可独立观察的因果事件；
触发自动拆拍审查。

## Split rule
优先寻找以下因果边界：
`准备/借力 → 第一动作 → 对手响应 → 变招 → 命中/结果`

每个子 Beat 至少保留一个完整的“动作 → 接触/规避 → 结果”链。

## Example
高复杂动作：
`蹬柱 → 虚扫 → 阵拦 → 松手 → 反握 → 变向 → 穿刺 → 破阵`

可拆为：
- B6A：蹬柱回弹 → 虚扫诱导阵拦
- B6B：松前手 → 反握变向 → 穿刺
- B6C：枪锋进入薄弱缝隙 → 阵内破界

最终时间轴仍可保持连续，不要求增加总时长。

## Preservation
拆拍不得改变：
- EVENT_ID / causal chain
- 战术意图
- 角色/武器锁
- 命中结果
- 环境损伤结果
- Ending State
