# Beat Complexity Budget V6.9

## Purpose
限制单个 Beat 同时发生的状态变化数量，防止导演层动作设计超过视频模型的稳定执行能力。

## Counted changes
每个 Beat 统计以下变化：
1. `actor_motion_change`
2. `weapon_state_change`
3. `direction_change`
4. `body_orientation_change`
5. `environment_event`
6. `ability_state_change`
7. `camera_mode_change`

## Default budget
- 普通 Beat：`max 4` 变化
- 高潮 Beat：`max 5`
- 终结 Beat：`max 5`
- `>5`：触发 `AUTO_SPLIT_REVIEW`
- `>6`：不得直接编译为单一 Beat

超过预算时，优先按因果边界拆分，而不是删除核心动作。

## Anti-inflation
增加变化数量本身不得增加 Stylish Score。`complexity_penalty` 应随超预算程度增加。
