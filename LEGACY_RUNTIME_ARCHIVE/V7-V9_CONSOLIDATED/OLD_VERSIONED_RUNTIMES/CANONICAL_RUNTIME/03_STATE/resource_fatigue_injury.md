# Resource / Fatigue / Injury State — 6.4

Track persistent actor resources when relevant: stamina, energy/qi/mana, ability charge, cooldown, fatigue, injury, mobility impairment and weapon control.

## Rules
- Resource changes are event-driven.
- High-cost actions require sufficient resource or an explicit exceptional rule.
- Injury may reduce available action candidates.
- Recovery restores resources only through explicit recovery events.
- UNKNOWN resources cannot be treated as unlimited.

Resource state is part of MASTER_COMBAT_STATE when the task depends on endurance or ability economy.
