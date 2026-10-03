---
name: prompt-master
version: "10.1.3"
description: "生产级多模态战斗视频提示词与战斗导演 Skill：从角色、武器、场景资产图与参考视频建立规范化资产档案，推理战斗人格与连续动作，通过 Combat Director、Shot Compression、状态/物理/镜头/连续性验证，编译为可直接投喂视频模型的最终提示词。"
---

# Combat Prompt Master V10.1.3 — Native Combat Execution OS

## 1. 定位

本 Skill 的唯一当前执行版本为 **V10.1.3**。核心任务是把用户提供的角色、武器、场景、风格/动作参考与战斗意图，转换为可直接投喂视频生成模型的生产级战斗提示词。

V10.1.3 是基于 V10.1.2 的 Runtime Integrity + Combat Director + Shot Compression 升级，不改变既有最终输出模板的产品形态。

当前唯一执行链：

`资产输入 → Asset Ingestion/Normalization → Immutable Canon → MASTER_COMBAT_STATE → Combat Intent → Combat-First Pacing → Combat/Style Inference → Combat Director Brain → Knowledge Retrieval → Candidate Filtering → Tactical Action Selection → Action/Ability Runtime → Actor Reaction → Temporal/Spatial/Event Identity/Physics → Power/Impact/Damage → VFX Result Visualization → Final Combat Sequence → Ending State → Beat Graph → Shot Compression → Shot Budget → SHOT_IR → Native Output Router → Model Adapter → QA/Repair → Regression Gate → Final Output`

旧版 V6–V10.1.2 Runtime、旧 Compiler、旧 Model Adapter 和旧 Output Policy 不属于当前执行链。它们仅保留在 `LEGACY_RUNTIME_ARCHIVE/` 供兼容参考，不得作为当前规则、当前输出入口或当前事实来源。

## 2. 当前权威文件

- 当前 Runtime：`CANONICAL_RUNTIME_V10.1.3/RUNTIME_MASTER_CANONICAL_V10.1.3.yaml`
- 当前 Shot Budget：`CANONICAL_RUNTIME_V10.1.3/SHOT_BUDGET_CONTROLLER_V10.1.3.md`
- 当前 SHOT_IR：`CANONICAL_RUNTIME_V10.1.3/SHOT_IR_CONTRACT_V10.1.3.md`
- 当前 Compiler Bridge：`CANONICAL_RUNTIME_V10.1.3/NATIVE_COMPILER_BRIDGE_V10.1.3.md`
- 当前 Combat Director：`30_COMBAT_DIRECTOR_BRAIN_V1.0/COMBAT_DIRECTOR_RUNTIME.md`
- 当前 Shot Compression：`31_SHOT_COMPRESSION_ENGINE_V1.0/SHOT_COMPRESSION_RULES.md`
- 当前 Output Router：`NATIVE_OUTPUT_ROUTER_V10.1.3/router.yaml`
- 当前 QA：`QA_V10.1.3/V10.1.3_REGRESSION_RULES.md`
- 当前 Governance：`V10.1.3_RUNTIME_GOVERNANCE.md`

只有上述当前文件可以定义默认执行行为。知识库版本可以独立于 Runtime 版本，例如 `29_ACTION_UNIVERSE_DATABASE_EXPANSION_V8.1` 是数据资产版本，不构成 Runtime 版本冲突。

## 3. 触发

以下任务触发本 Skill：
- 上传角色、武器、场景、风格参考图并要求设计打斗；
- 上传参考视频并要求提取、迁移或重构动作；
- 双人/多人近身战、兵器战、徒手战、Boss 战、群战、空战、御剑、远程战；
- 战斗分镜、运镜、爽感、冲击感、即时破坏、连续战损、镜头连续性；
- 要求生成任意时长战斗视频提示词；
- 要求优化已有战斗提示词。

## 4. 输入优先级

`用户硬约束 > 已确认资产事实 > 角色/武器/场景档案 > MASTER_COMBAT_STATE > 战斗意图 > 战斗人格 > 物理/连续性状态 > 知识库候选 > 镜头语言 > 风格修饰`

不得虚构用户未提供且资产、参考或知识库无法确认的角色能力、武器属性、动作事实、镜头事实或参考内容。FACT / INFERRED / UNKNOWN / CONFLICT 必须全链路传播。

## 5. Asset Ingestion / Normalization

建立统一的 Character Bible、Weapon Bible、World/Scene Bible，并记录 `source / confidence / locked_fields / unknowns / conflicts`。

多参考图出现服装、发型、武器、颜色、比例等冲突时，先判定 PRIMARY / SECONDARY / CONFLICT / UNKNOWN；不得静默拼接冲突信息。

Immutable Canon 锁定用户硬约束、确认资产事实、固定结局与显式锁定项。任何自动修复不得静默修改 Canon。

## 6. Combat Intent & Combat-First Pacing

显式管理 `narrative / tactical / emotional / visual / power / pacing / ending` goals 与 forbidden behavior。

当用户目标以打斗为主时默认启用 Combat-First：
- 首个有效战斗事件优先于静态人物展示和说明性铺垫；
- 角色/环境介绍默认不超过总时长 10%；
- 首个有效战斗事件目标不晚于总时长 10%；
- 战斗有效时间默认不低于 70%；
- 优先用“人物识别 → 动作 → 后果”完成出场；
- 抑制站桩、走入、摆POSE、慢推脸、重复武器展示和冗余 Establishing Shot；
- 可用 `IMPACT_OPEN / COUNTER_OPEN / WEAPON_CLASH_OPEN / AMBUSH_OPEN / CHASE_OPEN / ABILITY_OPEN / ENVIRONMENT_BREAK_OPEN / MID_COMBAT_OPEN`；
- 用户明确要求慢节奏人物出场时，该策略降级为非强制。

## 7. Combat Director Brain

Combat Director 是 V10.1.3 的新增核心决策层，负责把战斗人格、战斗目标、动作候选与对手反应组织成真实的战术因果。

标准决策闭环：

`OBJECTIVE → OBSERVATION → TACTICAL_PROBLEM → DECISION → ACTION → RESULT → OPPONENT_INTERPRETATION → COUNTER_DECISION → NEW_ACTION → TACTICAL_SHIFT → ESCALATION`

每个关键动作必须回答至少一个问题：
- 角色当前想达成什么？
- 角色观察到了什么？
- 当前战术问题是什么？
- 为什么选择这个动作而不是其他合法候选？
- 动作造成了什么可观察结果？
- 对手如何理解这个结果？
- 对手为什么改变决策？
- 下一动作如何由前一个结果产生？

禁止无决策的 `A攻击 → B防御 → A攻击 → B防御` 循环。

若连续两个交换单元没有 meaningful decision/state change，必须触发战术修复：改变距离、角度、地形、资源、攻击目标、能力使用、风险水平或终结策略；不得为了打破重复而随机增加动作。

### Combat Personality Binding

Combat Personality 不是视觉标签，而是决策偏置。它可影响：
- preferred distance
- attack entry
- risk tolerance
- defensive response
- counter preference
- terrain use
- recovery behavior
- finishing preference

人格只能在合法候选中进行选择，不能覆盖 Canon、武器锁定、物理可行性、空间连续性或用户硬约束。

## 8. Knowledge Retrieval / Candidate Selection

知识库是候选生成器，不是 Canonical Authority。

候选必须经过：

`Retrieval → Source/Applicability Check → Hard Filter → Tactical Validity → Spatial/Physics Check → Readability → Personality Preference → Complexity Budget → Camera Followability → QA`

动作数据库的数量不能代替战术选择质量。优先选择能解释当前战术问题、能自然产生下一状态、且能在有限 Shot Budget 中执行的动作。

## 9. Action / Ability / State / Physics

每个关键 Beat 至少建立 `before_state → event → after_state`。

动作必须满足身体力学、武器约束、攻击距离、空间条件与前后状态衔接。能力按 `激活 → 蓄力 → 目标 → 轨迹 → 接触 → 能量/力传递 → 响应 → 持续/打断` 建模。

每个主要动作必须有可追溯战术原因。关键动作产生可观察结果；足够强度的建筑、墙体、地面或器物冲击默认接触后立即产生碎裂、断裂、崩塌、飞散或形变，不允许无因果停顿。

MASTER_COMBAT_STATE 是统一运行状态源。位置、朝向、距离、高度、速度、姿态、支撑脚、双手、武器、受击、资源、战损、环境损伤等状态必须由事件驱动并记录 `source_event`。

## 10. Spatial / Event / Continuity / Damage

维护角色位置、朝向、距离、高度、障碍物、破坏物、武器攻击包络、镜头轴线、机位与主体屏幕关系。

每个有因果意义的物理事件分配稳定 `EVENT_ID` 与 semantic hash。多个镜头可以观察同一事件，但一个物理事件不得被重复计算。

战损与环境状态持久继承：`INTACT → LIGHT_DAMAGE → STRUCTURAL_DAMAGE → SEVERE_DAMAGE → COLLAPSE/DESTRUCTION`。

镜头切换不得重置角色身份、武器数量/类型、空间状态、战损或环境结果。

## 11. Impact / VFX / Damage / Rhythm

冲击强度来自动作速度、接触、受力、重量、位移、破坏和恢复，而不是单纯增加爆炸或粒子。

VFX 必须在动作结果确定后生成，并绑定角色/武器/能力/环境因果链。VFX 的职责是解释已经发生的力、能量、材质响应和环境反馈，而不是凭空制造战斗结果。

视觉反馈优先遵循：
`BODY/WEAPON → ENERGY → CONTACT → FORCE TRANSFER → MATERIAL RESPONSE → ENVIRONMENT RESPONSE → TRAIL/AFTEREFFECT`

战斗强度使用时间曲线管理动作、冲击、移动、镜头、破坏与恢复。镜头跟随战斗原因，不用无意义旋转、抖动、缩放掩盖动作问题。

## 12. Final Combat Sequence / Ending

需要战斗高潮时，终段执行：

`FINAL_BUILD → FINAL_OPENING → FINAL_EXCHANGE → FINAL_COMMIT → FINAL_IMPACT → RESULT_LOCK → ENDING_SHOT`

Final Impact 遵循：`CONTACT → FORCE_TRANSFER → RESULT → BODY/WEAPON RESPONSE → ENVIRONMENT RESPONSE → FINAL_STATE_DELTA`。

`RESULT_LOCK` 后的 Ending Shot 只能观察已锁定结果，可展示状态、武器、废墟、距离、余波或未解决威胁，不得创造新攻击、新命中、新破坏或偷偷改变结局。

## 13. Beat Graph → Shot Compression

Beat 与 Shot 是不同层级。

一个 Final Shot 可以承载多个连续 Beat，只要：
- 因果连续；
- 空间连续；
- 镜头能够跟随；
- 具有共同 story function；
- 不需要为了可读性强制切镜。

Shot Compression 优先：
1. 合并相邻且因果连续的 Beat；
2. 将微反应合并进母事件；
3. 将同一接触事件的接触/结果/恢复保持在同一 Shot；
4. 保留决定性战术变化；
5. 保留 Final Sequence 边界；
6. 不删除唯一能解释后续状态的事件。

禁止为了压镜头而：
- 合并不兼容的空间状态；
- 删除解释反制的决策；
- 删除解释战损的冲击事件；
- 改变因果顺序；
- 用镜头文字掩盖缺失的物理结果。

内部可以保留 `beat_ids / compression_reason`，但这些诊断字段不得泄漏到最终模型提示词。

## 14. Shot Budget — 30秒硬上限

Shot Budget 控制最终镜头数量，不等于 Beat 数量。

30 秒默认：
- Target = 7
- Soft Min = 6
- Hard Max = 7
- S01：Impact-first opening
- S02：First causal exchange
- S03：Counter / tactical change
- S04：Escalation / environment response
- S05：High-intensity exchange
- S06：Final build / decisive exchange setup
- S07：Final impact + result lock + ending observation

**硬规则：** 30 秒默认运行不得输出第 8 个最终镜头。Beat Auto-Split 可以创建子 Beat，但不得自行创建 Final Shot。优先合并相邻且因果连续的 Beat；不得为满足预算删除必要物理事件或虚构事件填充镜头。

如果压缩后仍超预算，触发 `SHOT_BUDGET_PRESSURE`，按最小责任层重新设计非必要展示和冗余镜头，而不是删除核心因果。

用户明确指定镜头数量或时间结构时，以用户硬约束为准，并由 Shot Budget 重新分配。

## 15. SHOT_IR — 唯一语义中间层

所有最终模型输出必须来自同一 `SHOT_IR`。

Required fields：

`shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, physics, vfx, continuity, damage_state, ending_state`

其中：
- `beat_ids` 仅表示该 Shot 包含哪些 Beat，绝不自动生成新 Shot；
- `event_ids` 是稳定因果事件；
- `action_chain` 保存该 Shot 内的有序行动/结果/反应；
- `ending_state` 在终局 Shot 中承载 RESULT_LOCK。

跨模型不可改变的语义不变量：

`event_ids, causal_order, actor_identity, weapon_identity, spatial_state, physical_result, damage_state, ending_state`

Final Prompt 是输出表示，不是事实权威；Prompt 文本不得反向修改 MASTER_COMBAT_STATE。

## 16. Native Output Router

当前唯一输出入口：`NATIVE_OUTPUT_ROUTER_V10.1.3/router.yaml`。

默认未指定模型时输出三个独立产品：
1. Universal Cinematic Prompt
2. Seedance 2.5 Native Prompt
3. MiniMax H3 Native Prompt

用户指定单一目标模型时，只输出对应 Adapter。

三个 Adapter 必须共享同一个 `MASTER_COMBAT_STATE / SHOT_IR / Ending State`，但禁止复制粘贴。Adapter 只允许改变模型面向的表达结构、信息密度、句法和字段顺序，不得改变事件、角色、武器、空间、物理结果、战损或结局。

### Universal Adapter

保持既有 Universal Cinematic Prompt 的输出模板与字段结构。它是 Universal Adapter 的输出表示，不是所有模型的唯一格式。

### Seedance 2.5 Adapter

保持既有 Seedance 2.5 Native Prompt 的输出模板；只由 SHOT_IR 编译事件、连续动作、方向、接触/规避、物理结果与下一状态。每个最终 Shot 是一个连续执行单元，子 Beat 不得生成额外 Shot 编号。

### MiniMax H3 Adapter

保持既有 MiniMax H3 Native Prompt 的输出模板；只由 SHOT_IR 编译长上下文中的 Scene、Asset Lock、Objective、Chronological Action、Camera、Physics/VFX、Continuity、Ending 与 Negative Constraints。只在必要处重复身份锁定信息。

这些 Adapter 是 Skill-native compilation contracts，不宣称复制任何未公开的厂商内部模板。

## 17. Final Visible Output Contract

除非用户明确要求内部分析，最终响应只输出可执行的模型提示词，不输出 Runtime 字段、评分、节点 ID、状态机诊断、内部 QA 日志或 IR。

### Universal 默认输出结构

保持既有模板：
1. 标题
2. 生成目标
3. 时间统一规范
4. 全局统一规范
5. 人物物理效果铁律
6. 碰撞特效体系
7. 分镜
8. 负面约束

每个 Universal Shot 使用既有结构：

`[镜头X] 时间戳｜持续时间`

`镜头标题`

`复合运镜`

`极速动势与连续性`

`锚定碰撞与特效`

`视觉节奏与震动`

`钩子`

最终输出不得出现站桩、动作跳跃、肢体穿模、武器消失、场景漂移、无物理反馈、无绑定特效、字幕/UI/水印或现代元素等违反用户设定的内容。

## 18. Knowledge Retrieval

默认知识入口：`DATA/COMBAT_KNOWLEDGE/`；武术动作主入口：`DATA/MARTIAL_DATABASE/martial_unified_2000_full.json`。检索必须经过候选检索、来源与适用性检查、Hard Filter、结构化选择与状态验证。知识资产是候选，不是 Canonical Authority。

数据资产版本独立于 Runtime 版本。除非任务需要，不读取历史 Runtime 文件。

## 19. QA / Auto Repair / Regression

Correctness QA 与 Cinematic Quality QA 分离。所有 FAIL 必须路由到最低因果责任层，修复后按依赖闭包重新编译、重新验证。

修复顺序：`LEVEL 1 参数 → LEVEL 2 动作 → LEVEL 3 状态 → LEVEL 4 空间 → LEVEL 5 澄清`。不得用镜头、VFX、Prompt 压缩掩盖上游错误。

Regression 至少覆盖：单人、双人近战、兵器、远程、1v2、2v2、Boss、跨镜头轴线、即时破坏、持续战损、能力持续性、参考图冲突、未知武器属性、长序列继承、模型适配、Combat Director 决策链、Beat→Shot 压缩，以及 30 秒 ≤7 Shot。

## 20. Runtime Governance

当前唯一 Runtime = **V10.1.3**。

任何文件、说明或历史模块只要声明自己为 V6–V10.1.2 Current Runtime、Current Output Authority、Current Compiler 或 Current Shot Budget，均视为 Legacy，不得覆盖本 Skill。

当前权威路径必须真实存在。任何指向不存在路径的当前引用均为 Runtime Integrity FAIL。

Legacy 资产只能在明确需要兼容或检索时读取；Legacy 不得改变 Canonical Runtime、MASTER_COMBAT_STATE、SHOT_IR、Output Router 或 QA 规则。

## 21. Output Modes

支持：`DESIGN / STORYBOARD / FINAL_PROMPT / PACKAGE`。输出模式只改变外部展示，不改变底层 Combat State、Causal Graph、Combat Director、Shot Compression、Shot Budget、SHOT_IR 或 Ending State。

## 22. Final Execution Invariants

1. 角色身份不漂移。
2. 武器数量、类型和绑定关系不漂移。
3. 战斗事件具有因果链。
4. 每个关键动作具有可解释的战术原因。
5. 对手反应必须来自上一结果或可观察状态。
6. 物理结果立即且可追溯。
7. 战损与环境状态跨镜头继承。
8. 一个物理事件只有一个 EVENT_ID。
9. Beat 数量不得直接等于 Final Shot 数量。
10. 30 秒默认最终镜头数 ≤7。
11. Beat Auto-Split 不得突破 Shot Budget。
12. Shot Compression 不得删除核心因果依赖。
13. 所有模型输出均来自同一 SHOT_IR。
14. Adapter 不得改变语义不变量。
15. Ending Shot 不得改变 RESULT_LOCK。
16. Final Prompt 永远不是事实来源。
17. QA FAIL 不得伪造 PASS。
18. 未确认能力、武器、神器或世界规则不得被编造为 FACT。
19. 当前 Runtime 路径必须存在且版本一致。
20. Legacy 不得覆盖 Current Runtime。
