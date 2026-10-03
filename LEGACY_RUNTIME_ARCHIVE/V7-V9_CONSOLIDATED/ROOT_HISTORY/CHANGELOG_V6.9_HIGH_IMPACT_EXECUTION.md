# V6.9 High-Impact Execution Upgrade

## 核心目标
在 V6.8 “高燃、打斗要帅”的基础上，不继续无上限增加动作复杂度，而是加入可读性门槛与执行预算，让高燃动作更清楚、更稳定、更容易被视频模型执行。

## 新增
- Action Readability Gate
- Beat Complexity Budget
- Beat Auto-Split
- High-Impact Execution Controller
- `action_readability` / `complexity_change_count` / `execution_budget_fit` structured fields

## 新运行顺序
`Hard Filter → Tactical Validity → Action Readability Gate → Stylish Action Priority → Complexity Budget → Beat Heat Check → Camera Followability → Auto-Split if needed → QA/Repair`

## 默认预算
- 普通 Beat：最多 4 个状态变化
- 高潮 Beat：最多 5 个
- 终结 Beat：最多 5 个
- 超过 5：拆拍审查
- 超过 6：禁止作为单一 Beat 直接编译

## 重要原则
`Stylish ≠ Complex`。
动作数量、状态变化数量和 VFX 数量本身不等于爽感。高燃动作必须首先清楚，其次有力量交换和结果，再追求招式复杂度与镜头表现。
