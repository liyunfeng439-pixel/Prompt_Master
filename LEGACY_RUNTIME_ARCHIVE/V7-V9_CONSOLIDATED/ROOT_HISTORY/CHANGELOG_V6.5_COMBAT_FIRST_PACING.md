# V6.5 Combat-First Pacing Upgrade

## Goal
Strengthen the Skill for combat-led videos where fighting is the primary content and character introduction must be short.

## Added
- Combat-First Pacing Runtime
- first meaningful combat event deadline
- intro/combat/action/impact/recovery time budgets
- static character introduction suppression
- action-first character identification
- opening templates: IMPACT_OPEN, COUNTER_OPEN, WEAPON_CLASH_OPEN, AMBUSH_OPEN, CHASE_OPEN, ABILITY_OPEN, ENVIRONMENT_BREAK_OPEN, MID_COMBAT_OPEN
- combat-first schema and regression fixture

## Integrated
- Combat Intent
- Battle Blueprint
- Duration Budget
- Combat Rhythm
- Shot Runtime
- Cinematic Quality QA
- Regression Gate

## Contract hardening
- runtime_contract.schema.json corrected to 6.5
- action history / ending state / event identity / action scoring / regression fixture fields now reference their real schemas instead of string placeholders

## Behavior
Default combat-first target when the user asks for a combat-led sequence:
- intro <= 10%
- first meaningful combat event <= 10%
- combat time >= 70%
- static character presentation <= 5%

Explicit slow/dramatic introduction requests override these pacing targets while preserving correctness and canon constraints.
