# Weapon Control & Morph Runtime V1.1

V10.18.0 incremental control-layer upgrade.

## Core change

御器不再由武器类别决定。

所有已经进入 Canonical Weapon Identity 的武器，都具备统一的脱手御器能力。剑、刀、枪、棍、鞭、链、扇、法器以及用户提供的其他合法武器，均可在明确的战斗语义下进入：

- TELEKINETIC
- SPIRIT_CONTROLLED
- REMOTE_ATTACK
- RETURN_CONTROL

`HAND_HELD` 仍然保留，并且不会被自动替换。

## Trigger principle

触发条件是“武器脱手后仍被持续控制”，而不是武器名称。

允许：

`手持 → 脱手 → 空中受控 → 攻击/变线 → 命中 → 回收`

或：

`手持 → 脱手 → 环绕/追踪 → 多角度攻击 → 返回`

## Hard locks

- 武器身份不变
- 武器数量不变
- 武器形态/材质/质量属性不变
- 受控变线必须有灵力、法力或精神控制原因
- 不允许瞬移式脱手
- 不允许无因方向突变
- 不允许无重量飞行
- 返回必须有控制或回收语义

## Morph boundary

御器能力是 Universal；伸缩、变形仍然遵循原有武器特定规则。不要因为“所有武器可御器”而自动赋予所有武器变形能力。
