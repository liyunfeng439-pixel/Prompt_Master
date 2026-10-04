---
name: prompt-master
version: "10.18.6"
description: "生产级多模态战斗视频提示词与战斗导演 Skill：从角色、武器、场景资产图与参考视频建立规范化资产档案，进行战斗级战略规划、动作执行、物理/连续性验证、镜头预算与语义编译，最终输出可直接投喂视频模型的模型原生战斗提示词。"
---

# Combat Prompt Master V10.18.6 — Weapon Signature Ultimate Switch + Weapon Semantic Single-Source Compiler + Corrective Battle Director + Zero-Copy Native Runtime

## 1. 定位
唯一当前执行版本为 **V10.18.6**。本 Skill 的目标是从角色、武器、场景、动作/风格参考和用户硬约束，生成“打斗为主、因果完整、物理连续、镜头可执行、模型原生”的最终视频提示词。当前武器控制层采用 Universal Weapon Control：所有 Canonical 武器均可在明确战斗语义下进入脱手御器/遥控攻击模式。

V10.18.0 在既有闭环 Runtime 上增加可执行的 Adaptive Combat Narrative Runtime：保留 Zero-Copy、V4 Action、Weapon Integrity、Semantic Diversity、Deep QA；修复 Native Adapter 结构回退、Compiler 场景硬编码、Combat Director 战斗级规划不足、Transition INVALID 无重规划、Shot Budget 与文本压缩层混淆。

## 2. 当前唯一权威链
`资产输入 → Fact/Inference Guard → Immutable Canon → MASTER_COMBAT_STATE → State Normalization → Combat Intent → Combat-First Pacing → Combat Personality → Combat Director V5.0 + Highlight/Impact Payoff V2.0 → Spatial Combat Director V2.2 → Knowledge Retrieval → Weapon Integrity → V4 Action Resolution → Candidate Filtering → Tactical Selection → Opponent Prediction → Transition Validation → Bounded Replanning → A→B→C Lookahead → Action/Ability Runtime → Actor Reaction → Physics/Spatial/Event State → VFX/Impact/Damage → Phase Check → Beat Graph → Budget-Aware Shot Planning → Beat Compression → Shot Budget → SHOT_IR → Semantic Component Selection → Combat Semantic Compiler → Native Output Router → Model Adapter → Adapter Semantic Regression → Deep Prompt Semantic QA → Regression Gate → Final Output`

## 3. 权威文件
- Runtime: `CANONICAL_RUNTIME_V10.18.0/RUNTIME_MASTER_CANONICAL_V10.18.0.yaml`
- Director: `30_COMBAT_DIRECTOR_BRAIN_V3.3/COMBAT_DIRECTOR_RUNTIME.md`
- Transition: `32_ACTION_TRANSITION_GRAPH_V2.1/ACTION_TRANSITION_GRAPH_RUNTIME.md`
- Shot Compression: `31_SHOT_COMPRESSION_ENGINE_V2.1/SHOT_COMPRESSION_RULES.md`
- SHOT_IR: `CANONICAL_RUNTIME_V10.18.0/SHOT_IR_CONTRACT_V10.18.0.md`
- Shot Budget: `CANONICAL_RUNTIME_V10.9.0/SHOT_BUDGET_CONTROLLER_V10.9.0.md`
- Native Router: `NATIVE_OUTPUT_ROUTER_V10.9.0/router.yaml`
- QA: `QA_V10.9.0/V10.9.0_REGRESSION_RULES.md`
- Governance: `V10.18.0_RUNTIME_GOVERNANCE.md`

## 4. 输入与 Canon
用户硬约束 > 已确认资产事实 > Character/Weapon/Scene Bible > MASTER_COMBAT_STATE > 战斗意图/人格 > 物理连续性 > 知识库候选 > 镜头/风格。
FACT / INFERRED / UNKNOWN / CONFLICT 必须传播。任何自动修复不得静默修改 Canon。

## 5. Combat-First
打斗为主默认：介绍 ≤10%，首个有效战斗事件目标 ≤10%，有效战斗时间 ≥70%。优先人物识别 → 动作 → 结果；压制站桩、摆POSE、慢脸部展示、冗余 Establishing Shot。用户明确要求慢节奏时可覆盖。

## 6. Combat Director V4.0
核心闭环：`OBJECTIVE → OBSERVATION → TACTICAL_PROBLEM → DECISION → ACTION → RESULT → OPPONENT_OBSERVATION → OPPONENT_INTERPRETATION → OPPONENT_PREDICTION → COUNTER_DECISION → NEW_ACTION → TACTICAL_SHIFT → PHASE_CHECK → ESCALATION`。

战斗阶段是跨多个 Action/Beat/Shot 持续的动态状态，不是每个事件一个 Phase，也不是固定六段模板。阶段可持续、跳过、拆分或提前结束。阶段状态至少包含 phase_goal、dominant_problem、resource_pressure、positional_goal、opponent_prediction、phase_exit_condition、allowed_escalation、shot_budget_pressure。

对手预测是候选行为预测，不是确定性事实；在 Director 自主模式下必须参与候选动作排序，但不得覆盖 Canon、武器、物理、结局或用户硬约束。

## 6A. Spatial Combat Director V2.2
空间位置是战斗导演的核心动态状态，而不是动作库标签。Runtime 必须维护 `actor_spatial_state[A/B] + relative_spatial_state + environment_anchor_state`。

### 3D State
每个角色独立维护：`layer、anchor、support、movement_vector`；双方持久维护 `relative_height、relative_distance、facing、attack_axis`。每个 Event 必须保存空间状态 before/after 快照，并在 Shot_IR 中按该 Shot 所属 Event 恢复对应时序状态，禁止使用最终状态覆盖早期镜头。未知信息保持 `UNKNOWN`。

### 语义归属
- `目标离地`：改变被作用目标的高度，不改变攻击者高度
- `空中`：改变执行动作角色进入 `mid_air`
- `高空/云海上方`：只有动作或场景 Canon 明确支持时才能进入 `high_air`
- `坠落/落地回收`：根据明确动作语义恢复支撑状态
不得把“目标离地”误写成“攻击者飞起”，不得把未知高度自动写成高空。

### 空间战术
Director 每次选择动作前必须回答：当前空间问题是什么、这个动作如何改变相对位置、变化是否产生新的攻击轴/防守问题。空间转换是 `战术问题 → 空间决策 → 动作 → 物理结果 → 新空间状态 → 下一决策`。

### 空间路径
允许：地面→低空→中空→高空→极端尺度，也允许任意明确支持的回落；不要求每场都飞天。30 秒 adaptive 战斗在场景明确支持垂直空间时默认寻找至少 1 次有意义转换；grounded/constrained 不强制改写用户。

### 环境锚点
空间转换优先使用 Canon 已知锚点：桥面、屋顶、柱体、悬崖边、云台等。未知锚点不得虚构。

### Camera
空间转换优先使用跟拍、拉远、垂直升降、环境揭示等镜头展示起点→路径→新位置；炫酷特写必须在空间关系建立后短促使用，再恢复中远景可读性。

## 7. Transition V3
动作必须通过 A→B 验证；存在后续候选时再检查 B→C。INVALID 是反馈，不是终止：重新排序候选 → 尝试备用动作 → 必要时插入 Recovery/Position/Redirect Link → 再验证；默认最多 3 个备用候选 + 1 次恢复连接，仍失败则重新规划当前战术问题。

优先级：`战术连续性 > 物理连续性 > 空间连续性 > 阶段目标 > 战斗人格 > 镜头可跟随 > 因果升级 > 视觉华丽`。禁止瞬移、无解释换位、武器复制/替换、非法重心/支撑、缺失恢复。

## 8. V4 / Weapon / Ability
V4 Action 是可执行知识源，不是文字词典。每个动作必须解析为 Execution Contract；Weapon Integrity 必须保证 Canon、动作、执行、Prompt、Transition 的武器一致。Ability 必须经过 Execution Contract。

## 9. Physics / Impact / Damage
动作遵循准备 → 启动 → 加速 → 接触/避让 → 受力 → 结果 → 位移/反应 → 空间层级/位置更新 → 恢复。建筑、墙体、地面等达到足够冲击条件时接触后立即产生材质响应，不允许无因果停顿。VFX 只能解释已发生的力/能量/材质响应。战损跨 Shot 持续。

## 9A. Highlight / Impact Payoff Director V2.0
亮点动作不是单纯的 VFX 或特写，而是一个已经存在于动作知识库中的高价值因果事件。Combat Director 在候选动作排序阶段计算 `impact_payoff_score`，综合 **战术触发、接触几何、重心/关节链、力量来源、重量转移、动量、碰撞规则、受击身体反馈、位移结果、环境反馈、镜头接触覆盖**。

30 秒战斗在动作数量足够时默认寻找约 **2 个高价值亮点动作**，45 秒以上可扩展到 3 个；这是节奏目标，不是强制制造事件。亮点之间必须有普通战术交换、反制或空间变化，禁止连续堆叠。

亮点动作优先遵循：
`战术窗口 → 动作机制 → 接触几何 → 局部受力 → 身体/衣物/装备反馈 → 整体位移 → 已授权的环境反馈 → 镜头强化 → 新战术状态`。

- `signature`：极高视觉/动作价值，优先进入 2–3 Shot Beat。
- `high`：高价值冲击，可触发 Impact Close-Up。
- `support`：作为普通战斗中的局部冲击，不强制拆镜。
- `standard`：维持战斗节奏，不强行包装成爽点。

**禁止编造：** 未确认的人体部位、伤势、断裂、血液、二次碰撞、建筑名称、特殊饰品受力或能力效果。若用户/场景 Canon 明确提供环境锚点或 `secondary_collision`，才能把二次环境碰撞写进最终 Prompt。衣物、护具、绑带、饰品等反馈必须作为已发生接触的材质响应，不得色情化或脱离动作因果。

亮点动作的镜头必须服务于同一 Event：不得为了特写新增攻击、命中、破坏或战术决策。

### V10.9 Highlight Choreography Contract
亮点 Event 允许携带 `highlight_choreography` 表现契约，用于把用户指定的“慢动作→接触慢放→命中恢复→高速结果”编译成可执行的时间/摄影/特效节奏；它只是同一 Event 的表现层，不改变 Event 数量或战斗因果。

支持的核心字段：`duration_s/preferred_duration_s`、`tempo_phases`、`speed_curve`、`camera.angle`、`camera.orbit`、`camera.focus`、`camera.result_follow`、`camera_phases`、`impact_stack`、`result_chain`、`contact_lock`、`restore_on_impact`。

标准高冲击节奏：`approach_normal → entry_slow → contact_slow → impact_normal → result_fast`；命中后恢复正常速度必须与真实接触结果同步，不允许先出现冲击特效再补身体受力。

冲击层可使用 `core / middle / outer` 三层语义，但每一层都必须有对应的 VFX/环境事实来源；不得为了凑“三层”凭空增加能量类型。

若用户明确给出低机位、膝盖高度、慢速环绕、右腿/武器轨迹锁焦等摄影要求，优先写入 `highlight_choreography`，再由 SHOT_IR 编译；不得把摄影指令变成新的 Event。

若指定单个亮点时长，例如 `2.5s`，作为 Shot/Beat 的表现时长偏好处理；总时长仍由全局 duration budget 统一约束，不能破坏 30s ≤7 Beat。

## 10. Beat / Shot Planning
Beat ≠ Shot。30 秒核心分镜段 Beat 硬上限为 7；每个 Beat 可使用 1–3 个连续镜头 Shot。Shot 数量不是 7 的硬上限。

Shot Director 根据 **因果复杂度、空间状态变化、攻击轴变化、接触/结果价值、镜头可读性、环境尺度变化、终局结构** 决定 1/2/3 个 Shot，而不是按 Event 数量机械切分。拆 Shot 只能改变摄影覆盖，不得增加攻击、命中、破坏、战术决策或结果。

30 秒默认 Beat 目标区间为 6–7，但场景复杂度可以动态调整；硬约束只有 Beat≤7、每 Beat 1–3 Shot。

三层必须分离：
1. Beat Compression：压缩因果 Beat；
2. Shot Planning/Budget：决定 Final Shot 边界；
3. Text Compression：SHOT_IR 之后压缩文字。
Text Compression 永远不能改变事件存在、Shot 数量或事件顺序。

Budget Pressure 必须在最终 Shot 分配前进入 Director：先进行候选动作重排/压缩策略选择，再进入 Beat/Shot Planning；优先合并兼容微 Beat、减少冗余展示、选择更容易在有限镜头内承载完整因果的动作；不能删除唯一解释后续状态的事件。

## 11. Final Sequence / Ending
`FINAL_BUILD → FINAL_OPENING → FINAL_EXCHANGE → FINAL_COMMIT → FINAL_IMPACT → RESULT_LOCK → ENDING_SHOT`。RESULT_LOCK 后只能观察结果，不得新增攻击、命中、破坏或改变结局；终局可为胜负、平局、开放式停战或撤离，但不得凭空补写未确认的胜者/败者。

## 12. SHOT_IR
SHOT_IR 是唯一语义中间层，Required：`shot_id, duration, story_function, beat_ids, event_ids, actor_state, spatial_state, action_chain, camera, physics, vfx, continuity, damage_state, ending_state`。

所有 Adapter 必须保持 actor identity、weapon identity、event order、spatial semantics、physical result、damage、ending 不变。

## 13. Native Output
默认输出 Universal + Seedance 2.5 + MiniMax H3；用户指定单一模型时只输出该模型。三者共享 SHOT_IR，但必须使用不同的 Skill-native 可见结构：
- Universal：Generation Goal → Global Visual Direction → Asset Lock → Scene → Time/Shot Sequence → Action Causality → Physics/Impact → Camera → Continuity/Damage → Ending → Negative Constraints
- Seedance 2.5：Reference/Asset Lock → Creative Brief → Global Visual Direction → Timeline/Shot Sequence → Motion Continuity → Physics and VFX → Camera Motivation → Ending → Negative Constraints
- MiniMax H3：Scene → Characters/Asset Lock → Combat Objective → Action Sequence by Time → Camera → Physics/Environment → VFX → Consistency Rules → Ending → Negative Constraints

这些是 Skill-native compilation contracts，不声称为未公开的官方模板。

## 14. Generic Compiler Rule
Compiler 必须从动态 `canon / actor_registry / action_contracts / ability_contracts / SHOT_IR / ending_state` 生成输出。禁止硬编码特定角色、武器、胜负组合、测试场景或固定结局；开放式结尾不得自动补写胜负。

## 15. Zero-Copy Runtime
Runtime 使用 `zero_copy_in_process`。Harness 只传递 selected action payloads 等必要执行数据；知识库不复制成新的 Runtime 数据层。

## 16. Semantic Diversity
语义多样性必须来自战斗动作、战术、轨迹、接触、身体机制、结果与恢复的真实差异，不允许仅靠同义词替换。

## 17. QA / Regression
必须通过：Canon/Inference、Weapon/Ability、Transition、Lookahead/Replanning、Spatial Combat State、空间转换连续性、30s ≤7 Beat、Beat/Shot 分层、SHOT_IR 单源、Adapter semantic preservation、Runtime-term leakage、Semantic Diversity、Deep Prompt QA、RESULT_LOCK。诊断信息不得进入最终 Prompt。

## 19. Legacy
V10.18.6 为当前 Skill Release；Canonical Runtime Schema 保持 V10.18.0 兼容层，V10.18.4/V10.18.5 为历史增量版本，仅作为回归参考，不得覆盖当前规则或输出入口。历史文件继续保留用于兼容性审计。

## 18A-1. Universal Weapon Control（全武器御器）

### V10.18.1 Adaptive Weapon Control Intelligence
Universal Weapon Control 的“能力开放”与“行为触发”分离：所有合法 Canonical 武器均可御器，但自主模式只有在当前战术问题达到阈值时才激活；显式御器意图可直接覆盖阈值。御器选择不新增 Event，只改变既有武器 Event 的控制执行方式。

决策链：`战斗态势 → 战术问题 → 御器价值 → 控制模式 → 行为模式 → 既有动作执行`。支持 `orbit / angle_change / multi_angle / environment_redirect / release_attack_return`。近距离默认偏向持握；RESULT_LOCK 后禁止新增御器攻击。

执行层：`25_WEAPON_INTELLIGENCE_LAYER_2.3_WEAPON_TACTICAL_INTELLIGENCE/ADAPTIVE_WEAPON_CONTROL_INTELLIGENCE_V1.0.py`


### V10.18.2 Weapon Execution Variant Intelligence（历史兼容层）

> V10.18.2/V10.18.4/V10.18.5 历史实现保留用于兼容审计；当前执行语义由 V10.18.6 接管。

### V10.18.4 Weapon Semantic Variant Compiler
- 御器/遥控执行必须在最终动作提交、A→B/B→C 重规划和 lookahead 完成后解析。
- 进入 `TELEKINETIC / SPIRIT_CONTROLLED / REMOTE_ATTACK / RETURN_CONTROL` 后，`prompt_semantics.core_sentence` 必须切换为与脱手执行一致的语义核心；原手持核心仅保存在 `native_core_sentence` 作为 provenance。
- 禁止出现“execution_variant=remote”但 `core_sentence` 仍描述手握驱动的语义冲突。
- 该修复不得创建新 Event，不得改变 Beat/Shot 预算，不得改变 Universal / Seedance 2.5 / MiniMax H3 顶层输出结构。
御器不是对原始动作做文字覆盖，而是为同一战术动作建立独立的执行变体。`HAND_HELD_NATIVE` 保留原知识的手持动力链；`REMOTE_EXECUTION_VARIANT` 在释放后解除手—武器动力耦合，重新定义控制点、武器独立惯性、轨迹、接触与回收阶段。

硬规则：
- Lookahead / transition replan 完成后才提交最终武器控制变体，重规划不得丢失御器语义。
- `tracking` 与 `orbit` 为不同模式：tracking 只要求持续追踪，orbit 才要求围绕目标形成角度变化。
- 御器拥有 tactical_gain / control_cost / tactical_utility；高资源压力、多角度和环境折返会增加控制成本。
- 显式御器意图优先于自主阈值，但仍不得突破 RESULT_LOCK、武器身份、质量/惯性和空间连续性。
- 原始 Action Knowledge 不被修改；执行变体必须标记 provenance，并覆盖会与脱手状态冲突的 grip/body_weapon_coupling/temporal_phases/physics/prompt_semantics。
- 所有 Canonical 武器均可使用通用执行变体；如果某武器缺少专属 Action Knowledge，只能使用已有合法动作的通用执行变体，不得凭空声称存在未验证的专属招式。

V10.18 当前武器控制规则：**御器能力不再由武器类别决定。**

- 剑、刀、枪、棍、鞭、链、扇、法器以及用户提供的其他合法武器，均可进入 `TELEKINETIC / SPIRIT_CONTROLLED / REMOTE_ATTACK / RETURN_CONTROL`。
- 触发依据是“武器脱手后仍被持续控制”，而不是武器名称。
- 标准因果链：`手持 → 脱手 → 空中受控 → 追踪/环绕/变线/攻击 → 命中 → 返回或结果锁定`。
- 远程控制必须有 `qi / magic / spiritual_force` 等明确控制源。
- 受控武器仍保持原武器身份、数量、材质、质量/惯性和几何结构。
- 禁止瞬移式脱手、无因方向突变、无重量飞行、无控制原因的返回。
- `MORPH_CONTROL` 仍遵循原有武器特定能力，不因全武器御器而自动开放伸缩或变形。
- `HAND_HELD` 保留；只有明确远程控制语义时才进入脱手御器模式。

执行层：`25_WEAPON_INTELLIGENCE_LAYER_2.1_WEAPON_CONTROL_MORPH_RUNTIME/WEAPON_CONTROL_RUNTIME.yaml`

## 18C. V10.18.6 Weapon Signature Ultimate Switch（显式开关）

这是一个**默认关闭、显式关键词触发**的增量功能。只有用户输入中出现完整短语 **“专属大招”** 时，`signature_ultimate_switch=ON`；没有该短语时必须保持 `OFF`，不得因为“终结”“绝技”“大招感”“高燃”等其他词自动触发。

### 触发规则
- 唯一标准触发词：`专属大招`；否定意图（如“不要/关闭/取消/禁止专属大招”）优先，保持 OFF。
- 支持从 `user_prompt / prompt / input_prompt / request / user_request / instruction / instructions / text / description / objective / requirements` 等用户输入字段检测。
- 触发后通过 `Ultimate Compatibility Resolver + Candidate Scoring` 从现有 `action_result` 中选择最适合承载专属大招的 Event；不得把 `dodge / miss / block / recovery / reposition` 等非攻击结果强行升级为大招。可用 `signature_ultimate_actor_id` 明确指定角色。
- 只在已有战斗 Event 上叠加专属绝技，不创建新的 Combat Event，不改变 Event 顺序。
- 专属大招只使用当前角色已锁定的武器身份；武器数量、材质、质量/惯性、空间位置和角色身份不能漂移。

### 武器专属招式库
当前内置：
- 徒手 → **天罡震界**
- 剑 → **九霄裂天剑**
- 刀 → **赤霄断岳斩**
- 枪/矛 → **苍龙贯界枪**
- 棍/棒 → **天崩镇岳棍**
- 戟 → **霸极裂阵戟**
- 双刃/双刀/双剑 → **阴阳双极轮杀**
- 链刃/链 → **九转天锁回刃**
- 弓 → **天穹贯日箭**
- 法器 → **万象镇域天轮**
- 扇 → **九霄风雷扇**
- 鞭 → **九霄雷链破界**

每个专属招式都包含：`核心机制 → 起手蓄势 → 招式显现 → 武器轨迹 → 核心接触 → 环境结果 → VFX → 终极摄影`。视觉强度为终极级，但禁止用纯白闪屏、过曝、无因爆炸或粒子堆积遮挡角色、武器、接触点。

### 视觉拉满规则
专属大招默认提升到 `signature` 视觉层级，并允许使用 `ultimate_build → ultimate_release → contact_slow → impact_lock → result_fast` 的表现节奏、接触锁定、极短 Hit-Stop、主次三级冲击层、超高密度 VFX、环境同步响应和结果拉远镜头。

但“视觉拉满”不等于增加新攻击：所有光效、能量环、冲击波、碎片、环境破坏、镜头运动都必须围绕**同一个已有战斗 Event**服务。大招自身的接触、受力、环境响应必须完成 `signature_ultimate_contact_result_lock`；这只是锁定大招自身结果，不代表整场战斗结束。大招完成后允许 Combat Director 继续接入后续打斗，真正的 `RESULT_LOCK` 仍由原有 Ending/Ability 终局逻辑控制。

### 单一语义源
专属大招核心内容写入：
`Action → Execution Variant → prompt_semantics.signature_ultimate_core_sentence → SHOT_IR.prompt_semantics → Native Compiler → Final Prompt`

三种模型输出结构不变。Adapter 只改变表达方式，不得删除或改变专属招式、武器、轨迹、接触、物理结果和终局语义。

### 未触发行为
若输入没有“专属大招”：
`signature_ultimate_switch=OFF → 不调用专属招式库 → 不改变 Action → 不改变 SHOT_IR → 不改变最终 Prompt`。

## 18A. V10.18 Adaptive Combat Narrative Runtime（当前执行层）
Narrative Runtime 位于 `Combat Event Fusion → Physics Impact → Adaptive Combat Narrative → Phase/Beat/Shot Planning`，负责解释已经发生或已选定的战斗事件为什么发生，以及事件如何改变下一状态；它不是剧情小说生成器，也不新增 Combat Event。

每个 `action_result` 必须携带：`current_state → combat_intent → reason_for_action → action/result → state_transition → escalation_level → next_expected_state`。reason 的来源优先级为：用户/场景显式 intent → tactical_problem → 前一事件结果 → 当前 phase goal → 已确认空间状态；未知信息不得补写。

30秒叙事曲线自实际事件压缩生成，不采用固定六段模板。可出现 `establish / test / tactical_shift / escalation / climax / resolution` 的任意连续组合；它不能改变 Beat≤7 或 Shot 预算。

Narrative 进入 SHOT_IR 后，Native Adapter 只能把同一语义换成模型原生表达，不得新增攻击、能力、胜负、环境或结局。RESULT_LOCK 后不得生成新的 narrative action event。

## 18B. V10.18 QA
必须通过 `narrative_coverage`、`narrative_reason_integrity`、`narrative_curve_integrity`、`narrative_result_lock`；并与原有 Canon/Weapon/Ability/Transition/Spatial/Physics/Highlight/SHOT_IR/Adapter/Deep QA 同时通过。

## 20. 最终不变量
`combat_first + causal_chain + physical_continuity + spatial_continuity + identity_lock + weapon_lock + damage_persistence + dynamic_phase_strategy + opponent_prediction + transition_replanning + A_to_B_to_C_lookahead + highlight_impact_payoff + budget_aware_planning + beat_hard_max + single_shot_ir + model_native_structure + semantic_diversity + result_lock`


## V10.10.0 Beat/Shot hierarchy (historical compatibility reference; current authority is V10.18.6)
The runtime does **not** equate storyboard beats with camera shots. The semantic hierarchy is `EVENT → BEAT → SHOT`. A Beat is one complete causal combat unit; a Shot is a camera coverage unit inside that Beat. For 30 seconds, the hard budget is **≤7 core Beats**, not ≤7 Shots. Each Beat may contain **1–3 Shots** when camera coverage materially improves action readability. Shot splitting cannot create new combat events, hits, destruction, decisions, or results.

### Shot allocation
- 1 Shot: simple causal unit that is readable continuously.
- 2 Shots: normal action/reaction or attack/counter unit requiring a motivated cut.
- 3 Shots: only for complex high-intensity units such as approach→contact→reaction, multi-scale impact, or final build→impact→result.
- Never split merely to hit a numeric quota.

### 30s interpretation
`30s ≤ 7 Beats` is the storyboard constraint. Actual camera Shots may be greater than 7. Example: 7 Beats × 1–3 Shots = typically 7–21 camera shots, depending on causal complexity.

### Cinematic Close-Up Layer (historical V10.10.0+ compatibility reference)
特写不是额外剧情事件，而是现有 Event 的高价值视觉覆盖方式。Runtime 可在合适的 Shot 上启用 `closeup=true`，并写入 `closeup_role`。
- `impact_contact_closeup`：命中、反制、摔投、缴械等已发生接触的超近景。
- `weapon_contact_closeup`：格挡、缠压等兵器接触细节。
- `decision_reaction_closeup`：闪避、落空、反制判断后的短促眼神/面部/持械姿态特写。
- `energy_manifestation_closeup`：既有能力事件中的能量材质、压缩、附着与环境反馈特写。
- `final_impact_closeup`：最终碰撞事件的接触点特写，之后必须回到结果观察。
规则：特写必须绑定至少一个已有 Event；不得新增攻击、命中、破坏、战术决定或结果。单个 Beat 最多使用一个特写。30 秒序列通常控制在 2–4 个特写，短序列可少于此值；特写是“价值触发”，不是固定配额。不得连续堆叠脸部特写、武器特写和冲击特写。特写必须服务于动作因果，并在短促强调后恢复空间连续性。


## V10.10.0 Spatial Combat Rules (historical compatibility reference)
`EVENT → BEAT → SHOT` 之外，战斗导演必须维护 `EVENT → SPATIAL_STATE → NEXT_DECISION` 的位置因果链。每个 action event 记录进入该事件前的空间状态与事件后的空间状态；Shot 只能呈现这些已经确定的状态转换。

### Spatial State
- `spatial_layer`: ground / low_air / mid_air / high_air / extreme
- `relative_height`: same_level / slightly_above / airborne / high_air / extreme_scale
- `horizontal_reposition`: none / lateral / forward / retreat / chase / environment_anchor_shift
- `vertical_space_supported`: scene-level capability flag
- `anchor`: 当前可见空间锚点；未知时不得虚构建筑、山谷、云层等具体事实

### Spatial Transition
- Ground → Low Air：必须有起跳、踏地、跃身等动作依据
- Low Air → Mid Air：必须有持续上升、追击或受力路径
- Mid/High Air → Ground：必须有坠落、回落、受击或主动降落依据
- Ground ↔ Ground：允许通过追击、后撤、换角、环境锚点变化产生水平位置转换
- 不允许瞬移、无惯性改变方向、无支撑悬浮、跨 Shot 丢失高度/方向关系

### Spatial Camera
空间转换 Shot 必须优先使用 tracking / follow / pull-back / reveal / vertical crane-like motion 等能够表达路径的镜头逻辑；只有在路径已经建立后才允许使用炫酷特写。特写结束必须恢复空间可读性。


### V10.7 Highlight Choreography Contract
- Highlight tier is calibrated; knowledge-schema completeness alone cannot produce Signature.
- Signature requires multiple independent payoff amplifiers plus visible displacement or environment payoff.
- Every highlighted Event carries a choreography profile: trigger → entry → contact → force transfer → body response → displacement → environment payoff → camera payoff.
- The profile may only reference facts already present in Canon/action knowledge.


### V10.7 Spatial Snapshot Integrity
- Every action Event stores immutable spatial before/after snapshots.
- The next action Event must inherit the previous action Event after-state actor layers without unexplained layer jumps.
- Horizontal reposition resolves a known anchor when available; otherwise it remains explicitly pending rather than inventing a location.


## V10.10.0 Closed-Loop Corrections

- Budget-Aware Planning is now an applied loop: pressure is fed into presentation density and semantic Beat/Shot remerge; unique causal Events are immutable.
- A→B→C Lookahead now has an actual B-replan path when an explicit next C is incompatible with the committed B and a valid B alternative exists.
- Shot Director is semantic-causal: cut points are selected from tactical/result/spatial boundaries instead of evenly slicing Events by count.
- Existing Action Knowledge `cinematic` and `vfx` fields are resolved into SHOT_IR via runtime resolvers; no new camera/VFX architecture is introduced.
- Camera and VFX resolver provenance is carried into native compilation so adapters cannot silently replace the semantic source.
- Highlight target is a soft quality target: the runtime must not invent a highlight merely to satisfy a quota.
- Asset-driven mode remains fact-bound; it may use only supplied actor/weapon/scene/asset facts and cannot invent unseen visual details.
- QA now verifies semantic shot grouping, camera/VFX resolver activation, budget feedback application, and actual lookahead telemetry.


## V10.10.0 Upgrade Notes
- Highlight/Impact Payoff upgraded to Choreography V2.0 inside the existing Combat Director; no new top-level runtime module.
- A highlighted Event may now carry temporal rhythm, speed-reset, camera-phase, impact-stack and result-chain metadata.
- Native compilation emits the choreography as presentation semantics while preserving Event/Beat/Shot invariants.
- User-authored choreography remains fact-bound and cannot invent anatomy, damage, weapons, environment anchors or extra collisions.
- Regression includes a 2.5s-style low-angle slow-orbit impact choreography case.


## V10.10 Highlight Semantic Fidelity
Explicit user highlight directives are promoted into a Highlight Canon inside the existing Combat Director/VFX/Native Compiler path. Critical action, timing, camera, impact-layer, result and negative-constraint facts must survive into SHOT_IR and Universal/Seedance 2.5/MiniMax H3 outputs; missing critical facts are a QA failure. No new Event is created.


## V10.17.0 Weapon Tactical Intelligence
Weapon behavior selection is driven by combat situation. Weapon systems preserve identity, control source, state transition and tactical intent.
