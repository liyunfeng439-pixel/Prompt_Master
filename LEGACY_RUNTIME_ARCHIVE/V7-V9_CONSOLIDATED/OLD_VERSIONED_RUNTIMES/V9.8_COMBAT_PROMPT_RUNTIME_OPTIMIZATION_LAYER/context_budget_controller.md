# Context Budget Controller

目的：
避免 Qwen3.8 执行时被低优先级世界模拟信息占用上下文。

优先级：

P0:
最终视频Prompt
角色一致性
动作连续性

P1:
动作、镜头、VFX

P2:
战斗背景

P3:
世界历史、文明模拟
