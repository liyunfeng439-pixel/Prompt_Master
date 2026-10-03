# High-Impact Rhythm Controller V6.8

## Goal
让高燃贯穿主体战斗，而不是只有开头和结尾高燃。

### Default soft targets for combat-led short videos
- 首个有效战斗事件 ≤ 10% duration
- 主要战斗段 `ACTION_DENSITY` 高于 `RECOVERY_SPACE`
- 重要爽点/冲击锚点默认间隔约 2–4 秒；允许因动作长度、模型能力、战术需要调整
- Tactical Pause 默认 ≤ 2.0 秒；超过 2.5 秒必须有明确的战术信息、能力蓄力或结果确认理由
- 单次纯观察镜头不得连续吞噬多个可用于战斗事件的时间预算

### Heat curve
`IGNITION → HIGH → HIGHER → MICRO_BREATH → HIGH → PEAK → RESULT`

Micro-breath 是短暂读招/恢复，不等于静态剧情段。

### Anti-fatigue
高燃不等于每一拍都爆炸。至少交替两种维度：
- speed
- direction
- elevation
- distance
- force
- displacement
- environment
- weapon interaction

这样避免“全程同一种炫技”。
