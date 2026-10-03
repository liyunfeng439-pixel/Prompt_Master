# Action Readability Gate V6.9

## Purpose
保证“帅感”首先能被视频模型和观众在高速状态下读懂。Readability 是 High-Impact 的前置门槛，不因动作指标数量高而被跳过。

## Required signals
主要动作至少应形成：
- clear_intent：起势/攻击意图可识别
- clear_attack_line：攻击方向或身体运动线路清楚
- clear_contact_or_avoidance：接触、格挡、闪避或借力关系可辨
- clear_force_result：力量传递后的状态结果可辨

## Gate
默认要求：
- `readability_score >= 70`
- `clear_intent = true`
- `clear_attack_line = true`
- `clear_contact_or_avoidance = true`

若低于门槛，不进入 Stylish Action 排序；先换候选、拆拍或降低动作复杂度。

## Readability principle
`Stylish ≠ Complex`。
动作越复杂不自动获得更高爽感分；若复杂度降低 silhouette、攻击线、接触关系或力量结果的可读性，必须扣分或拆分。
