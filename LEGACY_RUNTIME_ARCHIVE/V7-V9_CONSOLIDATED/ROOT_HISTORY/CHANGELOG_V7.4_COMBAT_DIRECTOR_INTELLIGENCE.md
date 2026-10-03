

# V7.4 Combat Director Intelligence Upgrade

## 目标
在 V7.3 Cinematic Execution Output Engine 基础上强化：
- 角色独有战斗逻辑
- 高燃动作风格化
- 战斗空间导演能力
- 自动复杂度修复

V7.4 不增加新的输出格式，仅优化现有战斗提示词生成链。

---

# Combat Director Layer

在 Combat Intent 与 Tactical Action Selection 之间增加导演决策层。

执行顺序：

Asset Combat Relevance
→ Combat Personality Matrix
→ Conflict Core
→ Battle Arc
→ Signature Action
→ Beat Generation

---

# Combat Personality Matrix

每个角色必须生成：

1. Combat Personality
- 冷静/狂暴/戏谑/谨慎/压迫等

2. Decision Habit
- 面对攻击如何反应
- 如何寻找机会
- 如何改变策略

3. Preferred Advantage
- 距离优势
- 速度优势
- 力量优势
- 技巧优势
- 能力控制优势

4. Forbidden Behavior
自动过滤不符合角色人格的动作。

---

# Signature Action Generator

生成角色专属动作，不允许只调用通用动作库。

动作必须满足：

- 来源于武器特性
- 来源于身体能力
- 来源于角色战斗人格
- 产生可识别视觉轮廓

优先生成：
- 招牌起手
- 招牌反击
- 招牌转换
- 招牌终结动作

---

# Battle Space Graph Upgrade

在 Spatial Intelligence 基础上增加：

战斗空间节点：

- 起始区域
- 压制区域
- 反击区域
- 高潮区域
- 终局区域

每次空间移动必须说明：

移动原因
→ 接触事件
→ 环境结果
→ 新战术状态

禁止：
无目的飞行
无因果位移
纯视觉移动。

---

# Battle Arc Generator

Beat 不再只是动作排列。

必须形成：

阶段1：
优势建立

阶段2：
优势破解

阶段3：
策略调整

阶段4：
能力升级

阶段5：
决定性结果


---

# Predictive QA Repair

QA 不只检测错误。

发现：

- Beat复杂度过高
- 连续动作重复
- 镜头不可执行
- 战斗信息密度过载

自动执行：

拆分动作
降低镜头复杂度
补充因果结果
替换重复动作

---

# High-Impact Priority Rule

当用户要求：

高燃
帅
爽感
战斗为主

优先级调整：

1. Stylish Action Priority
2. Combat Readability
3. Tactical Causality
4. Physical Impact
5. Visual Scale

禁止：
仅增加爆炸/VFX提升强度。

---

# V7.4 输出保持兼容

继续使用 V7.3 Cinematic Execution Output：

Global Base
Asset Lock
Combat Intent
Timeline Beat
Continuity
Negative Constraints
Production Prompt
QA PASS

不改变用户使用方式。
