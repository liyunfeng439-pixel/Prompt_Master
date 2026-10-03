# Combat Intent Contract

Before action generation, normalize what the fight is supposed to accomplish.

Required dimensions:
- `narrative_goal`
- `tactical_goal`
- `emotional_goal`
- `visual_goal`
- `power_goal`
- `pacing_goal`
- `ending_goal`
- `forbidden_behavior`

Each field stores value, priority, source, confidence and whether it is immutable.

The compiler must distinguish user intent from runtime inference. If two goals conflict, higher-priority explicit constraints win and the conflict is recorded.
