# 7 Shot Storyboard Control Layer — Incremental Upgrade

## Purpose
Controls storyboard generation density without changing combat logic, VFX logic, physics, model adapters, or prompt compilation rules.

## Core Constraint
When a cinematic sequence requests storyboard / 分镜 output:
- Maximum storyboard units: 7
- Default generation target: 7 shots
- Shorter sequences may output fewer shots when duration requires compression.
- Never exceed 7 shots.

## Shot Allocation Policy

30s combat sequence default:
1. Opening threat / visual hook
2. Character positioning and combat intent
3. First major exchange
4. Escalation / ability interaction
5. Turning point / environment impact
6. Final decisive exchange
7. Ending image / aftermath

## Preservation Rules
This layer only controls storyboard segmentation.
It does not:
- alter action selection
- alter character identity
- alter VFX selection
- alter physics simulation
- alter camera intelligence
- alter Seedance 2.5 or MiniMax H3 native compiler behavior

## Runtime Validation
Reject output when:
- storyboard_count > 7

Repair:
- merge adjacent low-impact shots
- preserve causal events
- preserve final exchange and ending state
