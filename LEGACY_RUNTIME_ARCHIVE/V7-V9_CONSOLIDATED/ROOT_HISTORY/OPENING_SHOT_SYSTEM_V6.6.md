# Opening Shot System V6.6

## Purpose
将 Combat-First Pacing 升级为完整 Opening Shot Runtime。

目标：
- 开场快速进入战斗
- 通过动作完成角色识别
- 避免无意义人物展示
- 根据角色、武器、空间、战术关系自动选择开场方式

## Pipeline

INPUT
↓
Opening Context Analysis
↓
Opening Mode Selector
↓
Eligibility Check
↓
Opening Event Generation
↓
Shot Compilation
↓
Combat Runtime

## Opening Modes

- IMPACT_OPEN
- WEAPON_CLASH_OPEN
- COUNTER_OPEN
- AMBUSH_OPEN
- CHASE_OPEN
- ABILITY_OPEN
- ENVIRONMENT_BREAK_OPEN
- MID_COMBAT_OPEN
- CLOSE_QUARTERS_OPEN
- DUEL_TENSION_BREAK_OPEN

## Constraints

- 首个有效战斗事件必须提前出现
- 禁止无战术意义的人物展示
- 禁止开场静态Pose替代动作
- 开场动作必须产生角色识别信息
- 开场事件必须进入Action History
- 开场事件必须生成Event Identity

## Selection Factors

- character_style_fit
- weapon_fit
- distance_fit
- terrain_fit
- tactical_fit
- cinematic_fit
- model_feasibility

## QA

检查：
- 是否超过Intro Budget
- 是否延迟First Combat Event
- 是否重复展示角色
- 是否创造无因果动作
- 是否破坏后续战斗连续性
