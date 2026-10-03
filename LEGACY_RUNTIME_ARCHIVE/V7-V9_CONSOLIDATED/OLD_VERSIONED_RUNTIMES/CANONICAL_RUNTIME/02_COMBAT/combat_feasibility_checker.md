# Combat Feasibility Checker

Every generated action must pass five checks:

1. BODY: anatomy, stance, reach, balance and recovery are plausible.
2. WEAPON: weapon length, grip, edge/impact direction and handling constraints are respected.
3. DISTANCE: attack range and target location match the current spatial state.
4. SPACE: walls, floor, ceiling, obstacles and destructibles permit the movement.
5. TRANSITION: the previous after_state can physically enter the next before_state.

FAIL examples: impossible reach, weapon passing through the body, unsupported mid-air direction change, teleporting position, instant recovery from a committed heavy strike, or an action requiring absent space.

Repair order: replace action → modify timing/amplitude → modify position → modify camera framing. Do not hide an infeasible action by changing the camera alone.
